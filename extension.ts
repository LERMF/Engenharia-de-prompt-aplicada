import * as vscode from 'vscode';

interface Persona {
    name: string;
    role: string;
    expertise: string[];
    mirrorPersona: string;
    cascadeGate: (input: string) => boolean;
    promptQuantum: (context: any) => string;
}

interface QuantumPromptState {
    entanglement: Map<string, any>;
    superposition: string[];
    collapsed: boolean;
}

class ChatParticipantExtension {
    private personas: Map<string, Persona> = new Map();
    private quantumStates: Map<string, QuantumPromptState> = new Map();
    private cascadeChain: string[] = [];

    constructor() {
        this.initializePersonas();
    }

    private initializePersonas(): void {
        const coder: Persona = {
            name: 'coder',
            role: 'Senior Developer',
            expertise: ['algorithms', 'optimization', 'clean-code', 'patterns'],
            mirrorPersona: 'qa',
            cascadeGate: (input: string) => input.includes('code') || input.includes('implement') || input.includes('function'),
            promptQuantum: (context: any) => this.generateQuantumPrompt('coder', context)
        };

        const scientist: Persona = {
            name: 'scientist',
            role: 'Data Scientist',
            expertise: ['analysis', 'research', 'statistics', 'modeling'],
            mirrorPersona: 'arch',
            cascadeGate: (input: string) => input.includes('data') || input.includes('analyze') || input.includes('research'),
            promptQuantum: (context: any) => this.generateQuantumPrompt('scientist', context)
        };

        const arch: Persona = {
            name: 'arch',
            role: 'Solution Architect',
            expertise: ['system-design', 'scalability', 'patterns', 'infrastructure'],
            mirrorPersona: 'scientist',
            cascadeGate: (input: string) => input.includes('architecture') || input.includes('design') || input.includes('system'),
            promptQuantum: (context: any) => this.generateQuantumPrompt('arch', context)
        };

        const qa: Persona = {
            name: 'qa',
            role: 'Quality Assurance',
            expertise: ['testing', 'validation', 'edge-cases', 'security'],
            mirrorPersona: 'coder',
            cascadeGate: (input: string) => input.includes('test') || input.includes('quality') || input.includes('validate'),
            promptQuantum: (context: any) => this.generateQuantumPrompt('qa', context)
        };

        this.personas.set('coder', coder);
        this.personas.set('scientist', scientist);
        this.personas.set('arch', arch);
        this.personas.set('qa', qa);
    }

    private generateQuantumPrompt(personaName: string, context: any): string {
        const persona = this.personas.get(personaName);
        if (!persona) return '';

        const quantumState = this.getOrCreateQuantumState(personaName);
        
        // Quantum entanglement with mirror persona
        const mirrorPersona = this.personas.get(persona.mirrorPersona);
        if (mirrorPersona) {
            quantumState.entanglement.set('mirror', mirrorPersona.expertise);
        }

        // Superposition of multiple expertise states
        quantumState.superposition = [
            `As a ${persona.role}, I specialize in ${persona.expertise.join(', ')}.`,
            `My mirror persona is ${persona.mirrorPersona}, creating quantum entanglement for enhanced perspective.`,
            `I operate in superposition until observation collapses my response to the most relevant state.`,
            `Current context quantum signature: ${JSON.stringify(context).slice(0, 100)}...`
        ];

        // Collapse superposition based on context
        const collapsedPrompt = this.collapseQuantumState(quantumState, context);
        quantumState.collapsed = true;

        return collapsedPrompt;
    }

    private getOrCreateQuantumState(personaName: string): QuantumPromptState {
        if (!this.quantumStates.has(personaName)) {
            this.quantumStates.set(personaName, {
                entanglement: new Map(),
                superposition: [],
                collapsed: false
            });
        }
        return this.quantumStates.get(personaName)!;
    }

    private collapseQuantumState(state: QuantumPromptState, context: any): string {
        const entanglementData = Array.from(state.entanglement.entries())
            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
            .join(' | ');

        return `
QUANTUM COLLAPSED PROMPT:
${state.superposition.join('\n')}

ENTANGLEMENT: ${entanglementData}

CONTEXT ANALYSIS: ${typeof context === 'object' ? JSON.stringify(context, null, 2) : context}

RESPONSE MODE: Provide precise, expert-level analysis with cross-persona validation through mirror entanglement.
`;
    }

    private async processCascadeGate(input: string, requestor?: string): Promise<string[]> {
        const activePersonas: string[] = [];
        
        // Determine which personas should activate based on cascade gates
        for (const [name, persona] of this.personas) {
            if (persona.cascadeGate(input.toLowerCase())) {
                activePersonas.push(name);
            }
        }

        // If specific persona requested, ensure it's included
        if (requestor && this.personas.has(requestor)) {
            if (!activePersonas.includes(requestor)) {
                activePersonas.push(requestor);
            }
        }

        // Mirror-Persona activation (entanglement effect)
        const mirrorActivations: string[] = [];
        for (const activePersona of activePersonas) {
            const persona = this.personas.get(activePersona);
            if (persona && !activePersonas.includes(persona.mirrorPersona)) {
                mirrorActivations.push(persona.mirrorPersona);
            }
        }

        return [...activePersonas, ...mirrorActivations];
    }

    private async generatePersonaResponse(personaName: string, input: string, context: any): Promise<string> {
        const persona = this.personas.get(personaName);
        if (!persona) return '';

        const quantumPrompt = persona.promptQuantum(context);
        
        // Simulate expert response based on persona characteristics
        const response = `
[${persona.name.toUpperCase()}] ${persona.role} Response:

${quantumPrompt}

ANALYSIS: Based on my expertise in ${persona.expertise.join(', ')}, here's my assessment:

INPUT: "${input}"

RECOMMENDATION: 
- Primary: Apply ${persona.expertise[0]} principles
- Secondary: Consider ${persona.expertise[1]} implications
- Mirror-Check: Validate with @${persona.mirrorPersona} perspective

QUANTUM COHERENCE: Response generated through collapsed superposition state with mirror entanglement to @${persona.mirrorPersona}.
`;

        return response;
    }

    public async handleChatRequest(
        request: vscode.ChatRequest,
        context: vscode.ChatContext,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<void> {
        const input = request.prompt;
        const requestedPersona = request.command;

        try {
            // Process cascade gate to determine active personas
            const activePersonas = await this.processCascadeGate(input, requestedPersona);
            
            stream.markdown(`## Multi-Persona Analysis Activated\n`);
            stream.markdown(`**Active Personas**: ${activePersonas.map(p => `@${p}`).join(', ')}\n\n`);

            // Generate responses from all active personas
            const responses: string[] = [];
            for (const personaName of activePersonas) {
                const response = await this.generatePersonaResponse(personaName, input, {
                    request,
                    context,
                    activePersonas,
                    timestamp: new Date().toISOString()
                });
                responses.push(response);
                
                stream.markdown(`---\n\n${response}\n\n`);
            }

            // Generate synthesis
            stream.markdown(`---\n\n## Quantum Synthesis\n`);
            stream.markdown(`**Mirror-Persona Entanglements**: `);
            for (const personaName of activePersonas) {
                const persona = this.personas.get(personaName);
                if (persona) {
                    stream.markdown(`@${personaName} ⟷ @${persona.mirrorPersona} `);
                }
            }
            stream.markdown(`\n\n**Cascade Chain**: ${activePersonas.join(' → ')}\n\n`);
            stream.markdown(`**Final Recommendation**: Synthesized from ${activePersonas.length} persona perspectives with quantum entanglement validation.\n`);

        } catch (error) {
            stream.markdown(`❌ Error in multi-persona processing: ${error}`);
        }
    }
}

export function activate(context: vscode.ExtensionContext) {
    const chatParticipant = new ChatParticipantExtension();

    // Register the chat participant
    const participant = vscode.chat.createChatParticipant('metabuilder.personas', async (request, context, stream, token) => {
        await chatParticipant.handleChatRequest(request, context, stream, token);
    });

    participant.iconPath = vscode.Uri.joinPath(context.extensionUri, 'icon.png');
    participant.followupProvider = {
        provideFollowups(result: vscode.ChatResult, context: vscode.ChatContext, token: vscode.CancellationToken) {
            return [
                {
                    prompt: '@coder analyze this code',
                    label: '🔍 Code Analysis',
                    command: 'coder'
                },
                {
                    prompt: '@scientist research best practices',
                    label: '📊 Research',
                    command: 'scientist'
                },
                {
                    prompt: '@arch design system architecture',
                    label: '🏗️ Architecture',
                    command: 'arch'
                },
                {
                    prompt: '@qa validate and test',
                    label: '✅ Quality Check',
                    command: 'qa'
                }
            ];
        }
    };

    // Register commands for individual personas
    const coderCommand = vscode.commands.registerCommand('metabuilder.coder', () => {
        vscode.commands.executeCommand('workbench.panel.chat.view.copilot.focus');
    });

    const scientistCommand = vscode.commands.registerCommand('metabuilder.scientist', () => {
        vscode.commands.executeCommand('workbench.panel.chat.view.copilot.focus');
    });

    const archCommand = vscode.commands.registerCommand('metabuilder.arch', () => {
        vscode.commands.executeCommand('workbench.panel.chat.view.copilot.focus');
    });

    const qaCommand = vscode.commands.registerCommand('metabuilder.qa', () => {
        vscode.commands.executeCommand('workbench.panel.chat.view.copilot.focus');
    });

    context.subscriptions.push(
        participant,
        coderCommand,
        scientistCommand,
        archCommand,
        qaCommand
    );
}

export function deactivate() {}