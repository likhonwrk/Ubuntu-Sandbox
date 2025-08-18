#!/bin/bash

# Ubuntu Sandbox Initialization Script
echo "🐧 Initializing Ubuntu Sandbox..."

# Set up environment
export DEBIAN_FRONTEND=noninteractive
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# Create necessary directories
mkdir -p /home/sandbox/projects
mkdir -p /home/sandbox/tools
mkdir -p /home/sandbox/.jupyter

# Set up Git configuration (if not exists)
if [ ! -f /home/sandbox/.gitconfig ]; then
    git config --global user.name "Sandbox User"
    git config --global user.email "sandbox@example.com"
    git config --global init.defaultBranch main
    git config --global --add safe.directory '*'
fi

# Create useful aliases
cat > /home/sandbox/.bash_aliases << 'EOF'
# Custom aliases for sandbox
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Development shortcuts
alias py='python3'
alias pip='pip3'
alias serve='python3 -m http.server 8000'
alias jlab='jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root'

# System monitoring
alias ports='netstat -tuln'
alias processes='ps aux'
alias memory='free -h'
alias disk='df -h'
EOF

# Create Jupyter configuration
cat > /home/sandbox/.jupyter/jupyter_lab_config.py << 'EOF'
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.allow_root = True
c.ServerApp.token = ''
c.ServerApp.password = ''
c.ServerApp.allow_origin = '*'
c.ServerApp.disable_check_xsrf = True
EOF

# Create a sample project structure
if [ ! -d "/home/sandbox/projects/sample-project" ]; then
    mkdir -p /home/sandbox/projects/sample-project
    cd /home/sandbox/projects/sample-project
    
    # Create a simple Python web app
    cat > app.py << 'EOF'
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Sandbox Web App", version="1.0.0")

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Ubuntu Sandbox</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 600px; margin: 0 auto; }
                .header { color: #2c3e50; }
                .info { background: #ecf0f1; padding: 20px; border-radius: 8px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="header">🐧 Ubuntu Sandbox</h1>
                <div class="info">
                    <p><strong>Welcome to your Ubuntu development sandbox!</strong></p>
                    <p>This is a containerized Ubuntu environment with:</p>
                    <ul>
                        <li>Python 3.10+ with FastAPI</li>
                        <li>Node.js 18+ with npm</li>
                        <li>Development tools (git, vim, etc.)</li>
                        <li>Jupyter Lab available on port 8888</li>
                    </ul>
                    <p>Start building your projects in <code>/home/sandbox/projects</code>!</p>
                </div>
                <p><a href="/docs">📚 API Documentation</a></p>
            </div>
        </body>
    </html>
    """

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Ubuntu Sandbox is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

    # Create requirements.txt
    cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
pandas==2.1.3
numpy==1.25.2
matplotlib==3.8.2
seaborn==0.13.0
jupyterlab==4.0.8
EOF

    # Create package.json for Node.js projects
    cat > package.json << 'EOF'
{
  "name": "sandbox-project",
  "version": "1.0.0",
  "description": "Sample project in Ubuntu sandbox",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
EOF

    # Create a simple Express server
    cat > server.js << 'EOF'
const express = require('express');
const app = express();
const port = 3000;

app.use(express.json());
app.use(express.static('public'));

app.get('/', (req, res) => {
    res.send(`
        <html>
            <head><title>Node.js Sandbox</title></head>
            <body style="font-family: Arial, sans-serif; margin: 40px;">
                <h1>🚀 Node.js Server Running</h1>
                <p>This is your Node.js server in the Ubuntu sandbox!</p>
                <p>Server running on port ${port}</p>
            </body>
        </html>
    `);
});

app.get('/api/status', (req, res) => {
    res.json({ 
        status: 'running', 
        port: port,
        message: 'Node.js server is healthy!' 
    });
});

app.listen(port, '0.0.0.0', () => {
    console.log(`🚀 Server running at http://0.0.0.0:${port}`);
});
EOF
fi

# Install Python packages if requirements.txt exists
if [ -f "/home/sandbox/projects/sample-project/requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    cd /home/sandbox/projects/sample-project
    pip3 install -r requirements.txt --user
fi

# Set proper permissions
chown -R sandbox:sandbox /home/sandbox/

# Display welcome message
echo ""
echo "✅ Ubuntu Sandbox initialized successfully!"
echo ""
echo "📁 Available directories:"
echo "   - /home/sandbox/projects (your code goes here)"
echo "   - /home/sandbox/tools (custom tools and utilities)"
echo ""
echo "🚀 Quick start commands:"
echo "   - cd /home/sandbox/projects/sample-project"
echo "   - python3 app.py  (start FastAPI server on port 8000)"
echo "   - npm start       (start Node.js server on port 3000)"
echo "   - jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root"
echo ""
echo "🔧 System info:"
echo "   - Python: $(python3 --version)"
echo "   - Node.js: $(node --version 2>/dev/null || echo 'Not available')"
echo "   - Git: $(git --version)"
echo ""
echo "Happy coding! 🎉"
