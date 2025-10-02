<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/drive/1om96wFUbdiiH1pSlWDH43MVtp3tyOQoy

## Features

### 🎯 Multimodal AI Interface
- Upload and process multiple file types (images, audio, video, documents)
- Send text prompts to Gemini AI
- Real-time file processing with progress indicators
- Drag-and-drop file support

### 💻 Hardware Detection (CPU-Z Style)
- Automatic system hardware detection on page load
- Displays CPU cores, architecture, RAM, GPU, OS, browser, and display information
- Optional checkbox to include hardware information in AI prompts
- Provides context to Gemini AI about your system configuration
- Uses browser APIs (no external dependencies)

Detected information includes:
- **CPU**: Cores, threads, and architecture
- **Memory**: Total RAM (estimated)
- **GPU**: Vendor and renderer (via WebGL)
- **Platform**: Operating system and device type
- **Browser**: Name and version
- **Display**: Resolution, color depth, and pixel ratio
- **Network**: Connection type and speed

## Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   `npm install`
2. Set the `GEMINI_API_KEY` in [.env.local](.env.local) to your Gemini API key
3. Run the app:
   `npm run dev`

## Usage

1. **Upload Files** (optional): Drag and drop files or click to browse
2. **Enter Prompt**: Type your question or instruction
3. **Include Hardware Info** (optional): Check the box to include system information in your prompt
4. **Send**: Click the Send button to get AI response
5. **Clear**: Reset the form to start over
