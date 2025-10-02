-- ISO-SWARM Database Schema
-- SQLite 3.46 bytecode VM optimized for Intel i3-7020U

PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 268435456; -- 256MB mmap

-- Models registry table
CREATE TABLE models (
    id TEXT PRIMARY KEY,
    persona TEXT NOT NULL,
    model_path TEXT NOT NULL,
    expertise TEXT NOT NULL, -- JSON array
    memory_usage INTEGER DEFAULT 0,
    load_count INTEGER DEFAULT 0,
    last_access INTEGER DEFAULT 0,
    average_latency_ms INTEGER DEFAULT 0,
    consensus_score REAL DEFAULT 0.0,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Query history for consensus learning
CREATE TABLE query_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id TEXT NOT NULL,
    prompt TEXT NOT NULL,
    persona TEXT,
    response TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    consensus_score REAL NOT NULL,
    token_count INTEGER DEFAULT 0,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Memory pool tracking
CREATE TABLE memory_pool (
    timestamp INTEGER PRIMARY KEY DEFAULT (strftime('%s', 'now')),
    total_usage INTEGER NOT NULL,
    available INTEGER NOT NULL,
    loaded_models INTEGER NOT NULL,
    swap_count INTEGER DEFAULT 0,
    compression_ratio REAL DEFAULT 0.0
);

-- Performance metrics
CREATE TABLE performance_metrics (
    timestamp INTEGER PRIMARY KEY DEFAULT (strftime('%s', 'now')),
    cpu_usage REAL NOT NULL,
    memory_usage REAL NOT NULL,
    gpu_memory REAL NOT NULL,
    active_sessions INTEGER NOT NULL,
    queries_per_second REAL DEFAULT 0.0,
    average_latency_ms REAL DEFAULT 0.0
);

-- Consensus token analysis
CREATE TABLE token_consensus (
    token TEXT PRIMARY KEY,
    frequency INTEGER DEFAULT 1,
    contexts TEXT, -- JSON array of context hashes
    weight REAL DEFAULT 1.0,
    last_seen INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Indexes for performance
CREATE INDEX idx_models_persona ON models(persona);
CREATE INDEX idx_models_last_access ON models(last_access DESC);
CREATE INDEX idx_query_history_persona ON query_history(persona);
CREATE INDEX idx_query_history_created ON query_history(created_at DESC);
CREATE INDEX idx_memory_pool_timestamp ON memory_pool(timestamp DESC);
CREATE INDEX idx_performance_timestamp ON performance_metrics(timestamp DESC);
CREATE INDEX idx_token_frequency ON token_consensus(frequency DESC);

-- Views for monitoring
CREATE VIEW active_models AS
SELECT 
    id,
    persona,
    memory_usage,
    last_access,
    datetime(last_access, 'unixepoch') as last_access_human,
    load_count,
    average_latency_ms
FROM models 
WHERE memory_usage > 0
ORDER BY last_access DESC;

CREATE VIEW persona_performance AS
SELECT 
    persona,
    COUNT(*) as query_count,
    AVG(latency_ms) as avg_latency_ms,
    AVG(consensus_score) as avg_consensus_score,
    MAX(created_at) as last_query
FROM query_history 
GROUP BY persona
ORDER BY avg_consensus_score DESC;

CREATE VIEW memory_usage_trend AS
SELECT 
    datetime(timestamp, 'unixepoch') as time,
    total_usage,
    available,
    loaded_models,
    compression_ratio
FROM memory_pool 
ORDER BY timestamp DESC 
LIMIT 100;

-- Triggers for automatic cleanup
CREATE TRIGGER cleanup_old_metrics 
AFTER INSERT ON performance_metrics
BEGIN
    DELETE FROM performance_metrics 
    WHERE timestamp < (strftime('%s', 'now') - 86400); -- Keep 24h
END;

CREATE TRIGGER cleanup_old_queries
AFTER INSERT ON query_history
BEGIN
    DELETE FROM query_history 
    WHERE created_at < (strftime('%s', 'now') - 604800); -- Keep 7 days
END;

CREATE TRIGGER update_model_stats
AFTER INSERT ON query_history
BEGIN
    UPDATE models 
    SET 
        last_access = NEW.created_at,
        load_count = load_count + 1,
        average_latency_ms = (average_latency_ms + NEW.latency_ms) / 2,
        consensus_score = (consensus_score + NEW.consensus_score) / 2
    WHERE id LIKE NEW.persona || '%';
END;

-- Initialize with sample data
INSERT INTO models (id, persona, model_path, expertise) VALUES
('coder_01', 'coder', './models/coder_01.gguf', '["rust", "algorithms", "optimization"]'),
('coder_02', 'coder', './models/coder_02.gguf', '["rust", "patterns", "clean-code"]'),
('analyst_01', 'analyst', './models/analyst_01.gguf', '["data", "statistics", "research"]'),
('architect_01', 'architect', './models/architect_01.gguf', '["systems", "design", "scalability"]'),
('security_01', 'security', './models/security_01.gguf', '["security", "vulnerabilities", "pentesting"]');

-- Optimize for Intel i3-7020U (2 cores, 4 threads)
PRAGMA threads = 4;
PRAGMA optimize;