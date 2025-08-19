#!/usr/bin/env python3
"""
Ubuntu Sandbox Startup Server
Keeps the container running and provides a web interface for Hugging Face Spaces
"""

import os
import sys
import json
import subprocess
import threading
import time
from pathlib import Path

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Ubuntu Sandbox",
    description="Interactive Ubuntu development environment",
    version="1.0.0"
)

# Global variables to track services
services = {}
sandbox_config = {}

def load_sandbox_config():
    """Load sandbox configuration from files"""
    global sandbox_config
    
    # Load sandbox.yml (simplified parsing)
    sandbox_yml_path = Path("/home/sandbox/sandbox.yml")
    if sandbox_yml_path.exists():
        # For simplicity, we'll extract key info without full YAML parsing
        with open(sandbox_yml_path, 'r') as f:
            content = f.read()
            sandbox_config['yml_content'] = content
    
    # Load tools.json
    tools_json_path = Path("/home/sandbox/tools.json")
    if tools_json_path.exists():
        with open(tools_json_path, 'r') as f:
            sandbox_config['tools'] = json.load(f)
    
    print("✅ Sandbox configuration loaded")

def run_command(command, background=False):
    """Run a shell command"""
    try:
        if background:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return process
        else:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
    except subprocess.TimeoutExpired:
        return {'error': 'Command timed out'}
    except Exception as e:
        return {'error': str(e)}

@app.get("/", response_class=HTMLResponse)
async def home():
    """Main sandbox interface"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🐧 Ubuntu Sandbox</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255,255,255,0.95);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 2px solid #eee;
            }
            .header h1 {
                font-size: 2.5em;
                color: #2c3e50;
                margin-bottom: 10px;
            }
            .header p {
                font-size: 1.2em;
                color: #7f8c8d;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 25px;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                border-radius: 10px;
                padding: 25px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                border-left: 4px solid #3498db;
                transition: transform 0.2s;
            }
            .card:hover {
                transform: translateY(-5px);
            }
            .card h3 {
                color: #2c3e50;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            .card ul {
                list-style: none;
                padding-left: 0;
            }
            .card li {
                padding: 8px 0;
                border-bottom: 1px solid #ecf0f1;
                display: flex;
                align-items: center;
            }
            .card li:last-child {
                border-bottom: none;
            }
            .status-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8em;
                font-weight: bold;
                margin-left: auto;
            }
            .status-running { background: #2ecc71; color: white; }
            .status-stopped { background: #95a5a6; color: white; }
            .status-error { background: #e74c3c; color: white; }
            .action-buttons {
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                margin-top: 30px;
                justify-content: center;
            }
            .btn {
                padding: 12px 25px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                font-weight: bold;
                transition: all 0.2s;
                text-align: center;
            }
            .btn-primary {
                background: #3498db;
                color: white;
            }
            .btn-primary:hover {
                background: #2980b9;
            }
            .btn-success {
                background: #2ecc71;
                color: white;
            }
            .btn-success:hover {
                background: #27ae60;
            }
            .btn-warning {
                background: #f39c12;
                color: white;
            }
            .btn-warning:hover {
                background: #d68910;
            }
            .btn-info {
                background: #17a2b8;
                color: white;
            }
            .btn-info:hover {
                background: #138496;
            }
            .terminal-section {
                margin-top: 30px;
                background: #2c3e50;
                border-radius: 10px;
                padding: 20px;
                color: #ecf0f1;
            }
            .terminal-header {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 1px solid #34495e;
            }
            .terminal-dots {
                display: flex;
                gap: 8px;
                margin-right: 15px;
            }
            .dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
            }
            .dot.red { background: #e74c3c; }
            .dot.yellow { background: #f1c40f; }
            .dot.green { background: #2ecc71; }
            #command-output {
                background: #1a252f;
                border-radius: 5px;
                padding: 15px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                line-height: 1.4;
                max-height: 300px;
                overflow-y: auto;
                white-space: pre-wrap;
            }
            .command-input {
                display: flex;
                gap: 10px;
                margin-top: 15px;
            }
            #command {
                flex: 1;
                padding: 10px;
                border: 1px solid #34495e;
                border-radius: 5px;
                background: #34495e;
                color: #ecf0f1;
                font-family: 'Courier New', monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🐧 Ubuntu Sandbox</h1>
                <p>Your containerized Ubuntu development environment</p>
            </div>

            <div class="grid">
                <div class="card">
                    <h3>🛠️ System Information</h3>
                    <ul>
                        <li>OS: Ubuntu 22.04 LTS <span class="status-badge status-running">Active</span></li>
                        <li>Python: 3.10+ <span class="status-badge status-running">Available</span></li>
                        <li>Node.js: 18+ <span class="status-badge status-running">Available</span></li>
                        <li>Git: Latest <span class="status-badge status-running">Ready</span></li>
                    </ul>
                </div>

                <div class="card">
                    <h3>🌐 Available Ports</h3>
                    <ul>
                        <li>Port 8000: Web Server <span class="status-badge status-running">Active</span></li>
                        <li>Port 8888: Jupyter Lab <span class="status-badge status-stopped" id="jupyter-status">Stopped</span></li>
                        <li>Port 3000: Dev Server <span class="status-badge status-stopped" id="dev-status">Stopped</span></li>
                    </ul>
                </div>

                <div class="card">
                    <h3>📁 Project Structure</h3>
                    <ul>
                        <li>/app/projects <span class="status-badge status-running">Ready</span></li>
                        <li>/app/tools <span class="status-badge status-running">Ready</span></li>
                        <li>Sample projects <span class="status-badge status-running">Created</span></li>
                    </ul>
                </div>

                <div class="card">
                    <h3>⚡ Quick Actions</h3>
                    <ul>
                        <li>
                            <button class="btn btn-success" onclick="startJupyter()">Start Jupyter Lab</button>
                        </li>
                        <li>
                            <button class="btn btn-primary" onclick="runSampleApp()">Run Python App</button>
                        </li>
                        <li>
                            <button class="btn btn-warning" onclick="runNodeServer()">Run Node.js Server</button>
                        </li>
                        <li>
                            <button class="btn btn-info" onclick="runDataAnalysis()">Run Data Analysis</button>
                        </li>
                    </ul>
                </div>
            </div>

            <div class="action-buttons">
                <button class="btn btn-primary" onclick="getSystemInfo()">System Info</button>
                <button class="btn btn-primary" onclick="listProjects()">List Projects</button>
                <button class="btn btn-primary" onclick="checkPorts()">Check Ports</button>
                <button class="btn btn-success" onclick="installPackage()">Install Package</button>
            </div>

            <div class="terminal-section">
                <div class="terminal-header">
                    <div class="terminal-dots">
                        <div class="dot red"></div>
                        <div class="dot yellow"></div>
                        <div class="dot green"></div>
                    </div>
                    <span>sandbox@ubuntu:~$</span>
                </div>
                <div id="command-output">Welcome to Ubuntu Sandbox! 🐧
System initialized and ready for development.

Available commands:
- System info, project management, package installation
- Use the buttons above or type commands below

Type 'help' for available commands.
</div>
                <div class="command-input">
                    <input type="text" id="command" placeholder="Enter command..." onkeypress="handleEnter(event)">
                    <button class="btn btn-primary" onclick="runCommand()">Run</button>
                </div>
            </div>
        </div>

        <script>
            function appendOutput(text) {
                const output = document.getElementById('command-output');
                output.textContent += '\\n' + text;
                output.scrollTop = output.scrollHeight;
            }

            function runCommand() {
                const input = document.getElementById('command');
                const command = input.value.trim();
                if (!command) return;

                appendOutput('$ ' + command);
                input.value = '';

                fetch('/api/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: command })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.stdout) appendOutput(data.stdout);
                    if (data.stderr) appendOutput('ERROR: ' + data.stderr);
                    if (data.error) appendOutput('ERROR: ' + data.error);
                })
                .catch(error => appendOutput('Network error: ' + error));
            }

            function handleEnter(event) {
                if (event.key === 'Enter') {
                    runCommand();
                }
            }

            function getSystemInfo() {
                runSpecificCommand('uname -a && python3 --version && node --version && df -h');
            }

            function listProjects() {
                runSpecificCommand('ls -la /app/projects/');
            }

            function checkPorts() {
                runSpecificCommand('netstat -tuln | grep -E ":(8000|8888|3000)"');
            }

            function startJupyter() {
                appendOutput('$ Starting Jupyter Lab...');
                fetch('/api/start-jupyter', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    appendOutput(data.message);
                    if (data.status === 'started') {
                        document.getElementById('jupyter-status').textContent = 'Running';
                        document.getElementById('jupyter-status').className = 'status-badge status-running';
                    }
                });
            }

            function runSampleApp() {
                appendOutput('$ Starting sample Python app...');
                runSpecificCommand('cd /app/projects/sample-project && python3 app.py &');
            }

            function runNodeServer() {
                appendOutput('$ Starting Node.js server...');
                runSpecificCommand('cd /app/projects/sample-project && node server.js &');
            }

            function runDataAnalysis() {
                appendOutput('$ Running data analysis script...');
                runSpecificCommand('python3 /app/projects/data-analysis-project/analyze_data.py');
            }

            function installPackage() {
                const pkg = prompt('Enter package name to install (pip3 install [package]):');
                if (pkg) {
                    runSpecificCommand('pip3 install ' + pkg);
                }
            }

            function runSpecificCommand(cmd) {
                appendOutput('$ ' + cmd);
                fetch('/api/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: cmd })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.stdout) appendOutput(data.stdout);
                    if (data.stderr) appendOutput('ERROR: ' + data.stderr);
                    if (data.error) appendOutput('ERROR: ' + data.error);
                })
                .catch(error => appendOutput('Network error: ' + error));
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/command")
async def execute_command(request: Request):
    """Execute a shell command"""
    try:
        data = await request.json()
        command = data.get('command', '')
        
        if not command:
            return JSONResponse({'error': 'No command provided'})
        
        # Security: block some dangerous commands
        dangerous_commands = ['rm -rf', 'sudo rm', 'mkfs', 'dd if=', 'shutdown', 'reboot']
        if any(dangerous in command.lower() for dangerous in dangerous_commands):
            return JSONResponse({'error': 'Command not allowed for security reasons'})
        
        result = run_command(command)
        return JSONResponse(result)
    
    except Exception as e:
        return JSONResponse({'error': str(e)})

@app.post("/api/start-jupyter")
async def start_jupyter():
    """Start Jupyter Lab service"""
    try:
        # Check if Jupyter is already running
        check_cmd = "pgrep -f 'jupyter-lab'"
        check_result = run_command(check_cmd)
        
        if check_result.get('returncode') == 0:
            return JSONResponse({
                'status': 'already_running',
                'message': 'Jupyter Lab is already running on port 8888'
            })
        
        # Start Jupyter Lab in background
        jupyter_cmd = "cd /home/sandbox && nohup jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root > jupyter.log 2>&1 &"
        result = run_command(jupyter_cmd)
        
        return JSONResponse({
            'status': 'started',
            'message': 'Jupyter Lab started on port 8888'
        })
    
    except Exception as e:
        return JSONResponse({
            'status': 'error',
            'message': f'Failed to start Jupyter: {str(e)}'
        })

@app.get("/api/status")
async def get_status():
    """Get sandbox status"""
    status = {
        'sandbox': 'running',
        'python': 'available',
        'nodejs': 'available',
        'git': 'available',
        'ports': {
            '8000': 'active',
            '8888': 'inactive',
            '3000': 'inactive'
        }
    }
    
    # Check if services are running
    jupyter_check = run_command("pgrep -f 'jupyter-lab'")
    if jupyter_check.get('returncode') == 0:
        status['ports']['8888'] = 'active'
    
    return JSONResponse(status)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        'status': 'healthy',
        'message': 'Ubuntu Sandbox is running',
        'timestamp': time.time()
    })

def main():
    """Main application entry point"""
    print("🐧 Starting Ubuntu Sandbox...")
    
    # Load configuration
    load_sandbox_config()
    
    # Create necessary directories
    os.makedirs("/home/sandbox/projects", exist_ok=True)
    os.makedirs("/home/sandbox/tools", exist_ok=True)
    
    print(f"✅ Sandbox server starting on port 8000")
    print(f"🌐 Open your browser to access the sandbox interface")
    print(f"📝 API documentation available at /docs")
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main()
