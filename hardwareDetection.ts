/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * Hardware Detection Module
 * Provides system information similar to CPU-Z for browser environments
 * Uses browser APIs and user agent parsing to gather hardware/system details
 */

export interface HardwareInfo {
    cpu: {
        cores: number;
        threads: number;
        architecture: string;
    };
    memory: {
        total: string;
        available: string;
    };
    gpu: {
        vendor: string;
        renderer: string;
    };
    browser: {
        name: string;
        version: string;
        userAgent: string;
    };
    platform: {
        os: string;
        type: string;
    };
    screen: {
        resolution: string;
        colorDepth: number;
        pixelRatio: number;
    };
    network: {
        effectiveType: string;
        downlink: string;
        rtt: string;
    };
}

/**
 * Detects CPU information using browser APIs
 */
function detectCPU(): HardwareInfo['cpu'] {
    const cores = navigator.hardwareConcurrency || 0;
    
    // Detect architecture from user agent
    let architecture = 'Unknown';
    const ua = navigator.userAgent.toLowerCase();
    if (ua.includes('x64') || ua.includes('x86_64') || ua.includes('amd64')) {
        architecture = 'x86_64';
    } else if (ua.includes('arm64') || ua.includes('aarch64')) {
        architecture = 'ARM64';
    } else if (ua.includes('arm')) {
        architecture = 'ARM';
    } else if (ua.includes('x86')) {
        architecture = 'x86';
    }
    
    return {
        cores,
        threads: cores, // In browser context, this is the same
        architecture
    };
}

/**
 * Estimates memory information
 */
function detectMemory(): HardwareInfo['memory'] {
    // @ts-ignore - deviceMemory is not in standard types yet
    const deviceMemory = navigator.deviceMemory;
    
    if (deviceMemory) {
        return {
            total: `~${deviceMemory} GB`,
            available: 'Unknown'
        };
    }
    
    return {
        total: 'Unknown',
        available: 'Unknown'
    };
}

/**
 * Detects GPU information using WebGL
 */
function detectGPU(): HardwareInfo['gpu'] {
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        
        if (gl && gl instanceof WebGLRenderingContext) {
            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            if (debugInfo) {
                const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                return {
                    vendor: vendor || 'Unknown',
                    renderer: renderer || 'Unknown'
                };
            }
        }
    } catch (e) {
        console.warn('Could not detect GPU info:', e);
    }
    
    return {
        vendor: 'Unknown',
        renderer: 'Unknown'
    };
}

/**
 * Parses browser information from user agent
 */
function detectBrowser(): HardwareInfo['browser'] {
    const ua = navigator.userAgent;
    let name = 'Unknown';
    let version = 'Unknown';
    
    // Detect browser
    if (ua.includes('Firefox/')) {
        name = 'Firefox';
        version = ua.split('Firefox/')[1].split(' ')[0];
    } else if (ua.includes('Edg/')) {
        name = 'Edge';
        version = ua.split('Edg/')[1].split(' ')[0];
    } else if (ua.includes('Chrome/')) {
        name = 'Chrome';
        version = ua.split('Chrome/')[1].split(' ')[0];
    } else if (ua.includes('Safari/') && !ua.includes('Chrome')) {
        name = 'Safari';
        version = ua.split('Version/')[1]?.split(' ')[0] || 'Unknown';
    } else if (ua.includes('Opera/') || ua.includes('OPR/')) {
        name = 'Opera';
        version = ua.split('OPR/')[1]?.split(' ')[0] || ua.split('Opera/')[1]?.split(' ')[0] || 'Unknown';
    }
    
    return {
        name,
        version,
        userAgent: ua
    };
}

/**
 * Detects platform/OS information
 */
function detectPlatform(): HardwareInfo['platform'] {
    const ua = navigator.userAgent;
    const platform = navigator.platform;
    let os = 'Unknown';
    let type = 'Desktop';
    
    if (ua.includes('Win')) {
        os = 'Windows';
        if (ua.includes('Windows NT 10.0')) os = 'Windows 10/11';
        else if (ua.includes('Windows NT 6.3')) os = 'Windows 8.1';
        else if (ua.includes('Windows NT 6.2')) os = 'Windows 8';
        else if (ua.includes('Windows NT 6.1')) os = 'Windows 7';
    } else if (ua.includes('Mac')) {
        os = 'macOS';
        type = 'Desktop';
    } else if (ua.includes('Linux')) {
        os = 'Linux';
    } else if (ua.includes('Android')) {
        os = 'Android';
        type = 'Mobile';
    } else if (ua.includes('iOS') || ua.includes('iPhone') || ua.includes('iPad')) {
        os = 'iOS';
        type = ua.includes('iPad') ? 'Tablet' : 'Mobile';
    }
    
    return { os, type };
}

/**
 * Detects screen information
 */
function detectScreen(): HardwareInfo['screen'] {
    return {
        resolution: `${screen.width}x${screen.height}`,
        colorDepth: screen.colorDepth,
        pixelRatio: window.devicePixelRatio || 1
    };
}

/**
 * Detects network information
 */
function detectNetwork(): HardwareInfo['network'] {
    // @ts-ignore - connection is not in standard types yet
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    
    if (connection) {
        return {
            effectiveType: connection.effectiveType || 'Unknown',
            downlink: connection.downlink ? `${connection.downlink} Mbps` : 'Unknown',
            rtt: connection.rtt ? `${connection.rtt} ms` : 'Unknown'
        };
    }
    
    return {
        effectiveType: 'Unknown',
        downlink: 'Unknown',
        rtt: 'Unknown'
    };
}

/**
 * Gathers all hardware information
 */
export function getHardwareInfo(): HardwareInfo {
    return {
        cpu: detectCPU(),
        memory: detectMemory(),
        gpu: detectGPU(),
        browser: detectBrowser(),
        platform: detectPlatform(),
        screen: detectScreen(),
        network: detectNetwork()
    };
}

/**
 * Formats hardware info as a readable string for AI context
 */
export function formatHardwareInfoForPrompt(info: HardwareInfo): string {
    return `
## System Information (CPU-Z style)

**CPU:**
- Cores/Threads: ${info.cpu.cores} cores / ${info.cpu.threads} threads
- Architecture: ${info.cpu.architecture}

**Memory:**
- Total RAM: ${info.memory.total}
- Available: ${info.memory.available}

**GPU:**
- Vendor: ${info.gpu.vendor}
- Renderer: ${info.gpu.renderer}

**Platform:**
- OS: ${info.platform.os}
- Type: ${info.platform.type}

**Browser:**
- Name: ${info.browser.name}
- Version: ${info.browser.version}

**Display:**
- Resolution: ${info.screen.resolution}
- Color Depth: ${info.screen.colorDepth}-bit
- Pixel Ratio: ${info.screen.pixelRatio}x

**Network:**
- Type: ${info.network.effectiveType}
- Downlink: ${info.network.downlink}
- RTT: ${info.network.rtt}
`.trim();
}
