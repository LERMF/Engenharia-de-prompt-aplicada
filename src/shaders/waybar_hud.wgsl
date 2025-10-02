// Fragment shader for Waybar 3D HUD
// Optimized for Intel HD 620 (48MB GPU memory)

@group(0) @binding(0)
var<uniform> time: f32;

@group(0) @binding(1)
var<uniform> resolution: vec2<f32>;

@group(0) @binding(2)
var<uniform> swarm_status: vec4<f32>; // [active_models, memory_usage, latency, consensus]

struct VertexOutput {
    @builtin(position) position: vec4<f32>,
    @location(0) uv: vec2<f32>,
    @location(1) world_pos: vec3<f32>,
};

@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
    let uv = input.uv;
    let pos = input.world_pos;
    
    // Base HUD color
    var color = vec3<f32>(0.1, 0.2, 0.3);
    
    // Swarm activity visualization
    let active_models = swarm_status.x;
    let memory_usage = swarm_status.y;
    let latency = swarm_status.z;
    let consensus = swarm_status.w;
    
    // Create neural network effect
    let grid_size = 20.0;
    let grid = fract(uv * grid_size);
    let grid_line = step(0.9, max(grid.x, grid.y));
    
    // Pulse effect based on swarm activity
    let pulse = sin(time * 2.0 + active_models) * 0.5 + 0.5;
    
    // Memory usage heatmap
    let memory_color = mix(
        vec3<f32>(0.0, 1.0, 0.0), // Green for low usage
        vec3<f32>(1.0, 0.0, 0.0), // Red for high usage
        memory_usage
    );
    
    // Latency indicator
    let latency_factor = smoothstep(0.0, 150.0, latency); // Target < 150ms
    let latency_color = mix(
        vec3<f32>(0.0, 1.0, 0.0), // Green for low latency
        vec3<f32>(1.0, 1.0, 0.0), // Yellow for high latency
        latency_factor
    );
    
    // Consensus visualization
    let consensus_rings = sin(length(uv - 0.5) * 10.0 - time * 3.0 + consensus * 6.28) * 0.5 + 0.5;
    
    // Combine effects
    color = mix(color, memory_color, grid_line * 0.3);
    color = mix(color, latency_color, pulse * 0.2);
    color += consensus_rings * consensus * 0.1;
    
    // Add some holographic effect
    let hologram = sin(uv.y * 100.0 + time * 10.0) * 0.02;
    color += hologram;
    
    // Transparency for HUD overlay
    let alpha = 0.8;
    
    return vec4<f32>(color, alpha);
}