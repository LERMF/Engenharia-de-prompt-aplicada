import * as vscode from 'vscode';
import * as net from 'net';
import { promisify } from 'util';
import * as fs from 'fs';

interface SwarmRequest {
    id: string;
    prompt: string;
    persona?: string;
    max_tokens?: number;
}

interface SwarmResponse {
    id: string;
    response: string;
    persona: string;
    latency_ms: number;
    consensus_score: number;
}

class ISOSwarmExtension {
    private socketPath = '/tmp/iso-swarm.sock';
    private daemonProcess: any = null;
    
    constructor(private context: vscode.ExtensionContext) {}
    
    async initialize(): Promise<void> {
        await this.startDaemon();
        await this.waitForDaemon();
    }
    
    private async startDaemon(): Promise<void> {
        const { spawn } = require('child_process');
        const daemonPath = vscode.Uri.joinPath(this.context.extensionUri, 'src', 'daemon', 'target', 'release', 'swarm-daemon');
        
        try {
            this.daemonProcess = spawn(daemonPath.fsPath, [], {
                stdio: ['ignore', 'pipe', 'pipe'],
                detached: false
            });
            
            this.daemonProcess.stdout?.on('data', (data: Buffer) => {
                console.log(`Swarm daemon: ${data.toString()}`);
            });
            
            this.daemonProcess.stderr?.on('data', (data: Buffer) => {
                console.error(`Swarm daemon error: ${data.toString()}`);
            });
            
            this.daemonProcess.on('close', (code: number) => {
                console.log(`Swarm daemon exited with code ${code}`);
            });
            
        } catch (error) {
            console.error('Failed to start swarm daemon:', error);
            throw error;
        }
    }
    
    private async waitForDaemon(): Promise<void> {
        const maxRetries = 30;
        let retries = 0;
        
        while (retries < maxRetries) {
            try {
                const exists = await fs.promises.access(this.socketPath, fs.constants.F_OK)
                    .then(() => true)
                    .catch(() => false);
                
                if (exists) {
                    console.log('Swarm daemon socket ready');
                    return;
                }
            } catch (error) {
                // Socket not ready yet
            }
            
            await new Promise(resolve => setTimeout(resolve, 1000));
            retries++;
        }
        
        throw new Error('Timeout waiting for swarm daemon to start');
    }
    
    async querySwarm(prompt: string, persona?: string): Promise<SwarmResponse> {
        return new Promise((resolve, reject) => {
            const client = net.createConnection(this.socketPath);
            
            const request: SwarmRequest = {
                id: Date.now().toString(),
                prompt,
                persona,
                max_tokens: 150
            };
            
            client.on('connect', () => {
                client.write(JSON.stringify(request));
            });
            
            client.on('data', (data) => {
                try {
                    const response: SwarmResponse = JSON.parse(data.toString());
                    resolve(response);
                } catch (error) {
                    reject(new Error(`Failed to parse response: ${error}`));
                }
                client.end();
            });
            
            client.on('error', (error) => {
                reject(error);
            });
            
            client.setTimeout(30000, () => {
                client.destroy();
                reject(new Error('Request timeout'));
            });
        });
    }
    
    async handleChatRequest(
        request: vscode.ChatRequest,
        context: vscode.ChatContext,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<void> {
        const input = request.prompt;
        const persona = request.command;
        
        stream.markdown(`## 🦾 ISO-SWARM Processing\\n`);
        stream.markdown(`**Input**: ${input}\\n`);
        stream.markdown(`**Target Persona**: ${persona || 'Auto-Select'}\\n\\n`);
        
        try {
            const startTime = Date.now();
            const response = await this.querySwarm(input, persona);
            const totalTime = Date.now() - startTime;
            
            stream.markdown(`### 🎯 Swarm Response\\n`);
            stream.markdown(`**Persona**: @${response.persona}\\n`);
            stream.markdown(`**Consensus Score**: ${(response.consensus_score * 100).toFixed(1)}%\\n`);
            stream.markdown(`**Latency**: ${response.latency_ms}ms (daemon) + ${totalTime - response.latency_ms}ms (transport)\\n\\n`);
            stream.markdown(`**Response**:\\n${response.response}\\n`);
            
            if (response.latency_ms > 150) {
                stream.markdown(`\\n⚠️ *Latency exceeded target 150ms*\\n`);
            }
            
        } catch (error) {
            stream.markdown(`❌ Swarm processing failed: ${error}\\n`);
            stream.markdown(`\\n💡 **Troubleshooting**:\\n`);
            stream.markdown(`- Check if swarm daemon is running\\n`);
            stream.markdown(`- Verify socket permissions: ${this.socketPath}\\n`);
            stream.markdown(`- Monitor memory usage (target: ≤1GB)\\n`);
        }
    }
    
    dispose(): void {
        if (this.daemonProcess) {
            this.daemonProcess.kill('SIGTERM');
        }
    }
}

export async function activate(context: vscode.ExtensionContext) {
    console.log('Activating ISO-SWARM extension...');
    
    const swarmExtension = new ISOSwarmExtension(context);
    
    try {
        await swarmExtension.initialize();
        
        const participant = vscode.chat.createChatParticipant('iso-swarm.personas', async (request, context, stream, token) => {
            await swarmExtension.handleChatRequest(request, context, stream, token);
        });
        
        participant.iconPath = vscode.Uri.joinPath(context.extensionUri, 'icon.png');
        participant.followupProvider = {
            provideFollowups(result: vscode.ChatResult, context: vscode.ChatContext, token: vscode.CancellationToken) {
                return [
                    {
                        prompt: '@swarm /coder optimize this algorithm',
                        label: '⚡ Code Optimization',
                        command: 'coder'
                    },
                    {
                        prompt: '@swarm /security analyze vulnerabilities',
                        label: '🔒 Security Analysis',
                        command: 'security'
                    },
                    {
                        prompt: '@swarm /architect design system',
                        label: '🏗️ System Architecture',
                        command: 'architect'
                    },
                    {
                        prompt: '@swarm /analyst process data',
                        label: '📊 Data Analysis',
                        command: 'analyst'
                    }
                ];
            }
        };
        
        // Auto-update weekly
        const updateTimer = setInterval(async () => {
            try {
                await vscode.commands.executeCommand('workbench.extensions.action.checkForUpdates');
            } catch (error) {
                console.error('Auto-update failed:', error);
            }
        }, 7 * 24 * 60 * 60 * 1000); // Weekly
        
        context.subscriptions.push(
            participant,
            { dispose: () => clearInterval(updateTimer) },
            { dispose: () => swarmExtension.dispose() }
        );
        
        console.log('ISO-SWARM extension activated successfully');
        
    } catch (error) {
        console.error('Failed to activate ISO-SWARM extension:', error);
        vscode.window.showErrorMessage(`ISO-SWARM activation failed: ${error}`);
    }
}

export function deactivate() {
    console.log('Deactivating ISO-SWARM extension...');
}