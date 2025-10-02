use anyhow::{Context, Result};
use crossbeam_channel::{Receiver, Sender};
use llama_cpp_rs::{LlamaModel, LlamaParams, LlamaSession};
use nix::sys::resource::{setrlimit, Resource};
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::sync::Arc;
use std::time::Instant;
use tokio::net::{UnixListener, UnixStream};
use tokio::sync::RwLock;
use tracing::{error, info, warn};

#[derive(Debug, Serialize, Deserialize)]
struct SwarmRequest {
    id: String,
    prompt: String,
    persona: Option<String>,
    max_tokens: Option<u32>,
}

#[derive(Debug, Serialize, Deserialize)]
struct SwarmResponse {
    id: String,
    response: String,
    persona: String,
    latency_ms: u64,
    consensus_score: f32,
}

#[derive(Clone)]
struct MiniLLM {
    id: String,
    model_path: PathBuf,
    persona: String,
    expertise: Vec<String>,
    model: Option<Arc<LlamaModel>>,
    session: Option<Arc<RwLock<LlamaSession>>>,
    memory_usage: usize,
}

struct SwarmManager {
    models: HashMap<String, MiniLLM>,
    memory_pool: MemoryPool,
    access_map: AccessMap,
    socket_path: PathBuf,
}

struct MemoryPool {
    max_size: usize,
    current_usage: usize,
    zstd_level: i32,
}

struct AccessMap {
    usage_count: HashMap<String, u32>,
    last_access: HashMap<String, Instant>,
}

impl SwarmManager {
    async fn new() -> Result<Self> {
        // Set cgroup v2 memory limit
        setrlimit(Resource::RLIMIT_AS, Some(1024 * 1024 * 1024), None)
            .context("Failed to set memory limit")?;

        let socket_path = PathBuf::from("/tmp/iso-swarm.sock");
        
        let mut manager = Self {
            models: HashMap::new(),
            memory_pool: MemoryPool {
                max_size: 1024 * 1024 * 1024, // 1GB
                current_usage: 0,
                zstd_level: 3,
            },
            access_map: AccessMap {
                usage_count: HashMap::new(),
                last_access: HashMap::new(),
            },
            socket_path,
        };

        manager.load_models().await?;
        Ok(manager)
    }

    async fn load_models(&mut self) -> Result<()> {
        let models_dir = PathBuf::from("./models");
        let persona_configs = [
            ("coder", vec!["rust", "algorithms", "optimization"]),
            ("analyst", vec!["data", "statistics", "research"]),
            ("architect", vec!["systems", "design", "scalability"]),
            ("security", vec!["security", "vulnerabilities", "pentesting"]),
            ("optimizer", vec!["performance", "memory", "cpu"]),
        ];

        // Load 40 models per persona (200 total)
        for (persona, expertise) in persona_configs {
            for i in 0..40 {
                let model_id = format!("{}_{:02}", persona, i);
                let model_path = models_dir.join(format!("{}.gguf", model_id));
                
                if model_path.exists() {
                    let mini_llm = MiniLLM {
                        id: model_id.clone(),
                        model_path,
                        persona: persona.to_string(),
                        expertise: expertise.clone(),
                        model: None,
                        session: None,
                        memory_usage: 0,
                    };
                    
                    self.models.insert(model_id, mini_llm);
                }
            }
        }

        info!("Loaded {} models configurations", self.models.len());
        Ok(())
    }

    async fn load_model_on_demand(&mut self, model_id: &str) -> Result<()> {
        if let Some(mini_llm) = self.models.get_mut(model_id) {
            if mini_llm.model.is_none() {
                // Check memory pool availability
                if !self.memory_pool.can_allocate(300 * 1024 * 1024) {
                    self.evict_lru_model().await?;
                }

                let params = LlamaParams::default()
                    .with_n_ctx(512)
                    .with_n_threads(2)
                    .with_use_mmap(true)
                    .with_use_mlock(false);

                let model = LlamaModel::load_from_file(&mini_llm.model_path, params)
                    .context("Failed to load model")?;
                
                let session = model.new_session_with_params(Default::default())
                    .context("Failed to create session")?;

                mini_llm.model = Some(Arc::new(model));
                mini_llm.session = Some(Arc::new(RwLock::new(session)));
                mini_llm.memory_usage = 300 * 1024 * 1024; // Estimated 300MB

                self.memory_pool.current_usage += mini_llm.memory_usage;
                self.access_map.usage_count.insert(model_id.to_string(), 1);
                self.access_map.last_access.insert(model_id.to_string(), Instant::now());
                
                info!("Loaded model {} into memory", model_id);
            }
        }
        Ok(())
    }

    async fn evict_lru_model(&mut self) -> Result<()> {
        let lru_model = self.access_map.last_access
            .iter()
            .min_by_key(|(_, &time)| time)
            .map(|(id, _)| id.clone());

        if let Some(model_id) = lru_model {
            self.unload_model(&model_id).await?;
        }
        Ok(())
    }

    async fn unload_model(&mut self, model_id: &str) -> Result<()> {
        if let Some(mini_llm) = self.models.get_mut(model_id) {
            if mini_llm.model.is_some() {
                self.memory_pool.current_usage -= mini_llm.memory_usage;
                mini_llm.model = None;
                mini_llm.session = None;
                mini_llm.memory_usage = 0;
                
                self.access_map.last_access.remove(model_id);
                info!("Unloaded model {} from memory", model_id);
            }
        }
        Ok(())
    }

    async fn query_swarm(&mut self, request: SwarmRequest) -> Result<SwarmResponse> {
        let start_time = Instant::now();
        
        let target_personas = if let Some(persona) = &request.persona {
            vec![persona.clone()]
        } else {
            self.select_best_personas(&request.prompt)
        };

        let mut responses = Vec::new();
        
        for persona in target_personas {
            let persona_models: Vec<_> = self.models
                .keys()
                .filter(|id| id.starts_with(&persona))
                .take(5) // Use top 5 models per persona
                .cloned()
                .collect();

            for model_id in persona_models {
                self.load_model_on_demand(&model_id).await?;
                
                if let Some(response) = self.query_model(&model_id, &request.prompt).await? {
                    responses.push((model_id, response));
                }
            }
        }

        let consensus_response = self.calculate_consensus(&responses);
        let latency = start_time.elapsed().as_millis() as u64;

        Ok(SwarmResponse {
            id: request.id,
            response: consensus_response.0,
            persona: consensus_response.1,
            latency_ms: latency,
            consensus_score: consensus_response.2,
        })
    }

    fn select_best_personas(&self, prompt: &str) -> Vec<String> {
        let prompt_lower = prompt.to_lowercase();
        let mut persona_scores = HashMap::new();

        for (model_id, mini_llm) in &self.models {
            let persona = &mini_llm.persona;
            let score = mini_llm.expertise.iter()
                .map(|exp| if prompt_lower.contains(exp) { 1.0 } else { 0.0 })
                .sum::<f32>();
            
            *persona_scores.entry(persona.clone()).or_insert(0.0) += score;
        }

        let mut sorted_personas: Vec<_> = persona_scores.into_iter().collect();
        sorted_personas.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        
        sorted_personas.into_iter()
            .take(2)
            .map(|(persona, _)| persona)
            .collect()
    }

    async fn query_model(&mut self, model_id: &str, prompt: &str) -> Result<Option<String>> {
        if let Some(mini_llm) = self.models.get(model_id) {
            if let Some(session) = &mini_llm.session {
                let session_guard = session.read().await;
                
                let response = session_guard.inference_with_prompt(
                    prompt,
                    request.max_tokens.unwrap_or(100) as usize,
                    &Default::default(),
                )?;

                self.access_map.last_access.insert(model_id.to_string(), Instant::now());
                *self.access_map.usage_count.entry(model_id.to_string()).or_insert(0) += 1;
                
                return Ok(Some(response));
            }
        }
        Ok(None)
    }

    fn calculate_consensus(&self, responses: &[(String, String)]) -> (String, String, f32) {
        if responses.is_empty() {
            return ("No response".to_string(), "unknown".to_string(), 0.0);
        }

        // Token overlap consensus
        let mut token_counts = HashMap::new();
        for (_, response) in responses {
            let tokens: Vec<&str> = response.split_whitespace().collect();
            for token in tokens {
                *token_counts.entry(token.to_lowercase()).or_insert(0) += 1;
            }
        }

        let mut best_response = String::new();
        let mut best_score = 0.0;
        let mut best_persona = String::new();

        for (model_id, response) in responses {
            let tokens: Vec<&str> = response.split_whitespace().collect();
            let overlap_score: u32 = tokens.iter()
                .map(|token| token_counts.get(&token.to_lowercase()).unwrap_or(&0))
                .sum();
            
            let score = overlap_score as f32 / tokens.len() as f32;
            
            if score > best_score {
                best_score = score;
                best_response = response.clone();
                if let Some(mini_llm) = self.models.get(model_id) {
                    best_persona = mini_llm.persona.clone();
                }
            }
        }

        (best_response, best_persona, best_score)
    }

    async fn start_server(&mut self) -> Result<()> {
        let _ = fs::remove_file(&self.socket_path);
        let listener = UnixListener::bind(&self.socket_path)?;
        
        info!("ISO-SWARM daemon listening on {:?}", self.socket_path);
        
        loop {
            match listener.accept().await {
                Ok((stream, _)) => {
                    self.handle_connection(stream).await?;
                }
                Err(e) => {
                    error!("Failed to accept connection: {}", e);
                }
            }
        }
    }

    async fn handle_connection(&mut self, mut stream: UnixStream) -> Result<()> {
        use tokio::io::{AsyncReadExt, AsyncWriteExt};
        
        let mut buffer = vec![0; 4096];
        let n = stream.read(&mut buffer).await?;
        
        if n == 0 {
            return Ok(());
        }

        let request: SwarmRequest = serde_json::from_slice(&buffer[..n])?;
        let response = self.query_swarm(request).await?;
        let response_json = serde_json::to_vec(&response)?;
        
        stream.write_all(&response_json).await?;
        Ok(())
    }
}

impl MemoryPool {
    fn can_allocate(&self, size: usize) -> bool {
        self.current_usage + size <= self.max_size
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt::init();
    
    info!("Starting ISO-SWARM daemon...");
    
    let mut swarm = SwarmManager::new().await?;
    swarm.start_server().await?;
    
    Ok(())
}