# 📁 Complete File Structure

## Overview

Here's the complete file structure with descriptions of where each file goes and what it does.

```
ai-agent-security-demo/
│
├── 📄 README.md                           # Main documentation (50+ pages)
├── 📄 QUICKSTART.md                       # 5-minute setup guide
├── 📄 WINDOWS_GUIDE.md                    # ⭐ NEW: Windows-specific guide
├── 📄 GETTING_STARTED.md                  # Visual step-by-step guide
├── 📄 ARCHITECTURE.md                     # System design & diagrams
├── 📄 TEST_SCENARIOS.md                   # Test cases & examples
├── 📄 PROJECT_SUMMARY.md                  # Project overview
├── 📄 requirements.txt                    # Python dependencies
│
├── 🪟 start_demo.bat                      # ⭐ NEW: Windows launcher (CLICK TO START)
├── 🪟 stop_demo.bat                       # ⭐ NEW: Windows stopper (CLICK TO STOP)
├── 🐧 start_demo.sh                       # Linux/Mac launcher
├── 🐧 stop_demo.sh                        # Linux/Mac stopper
├── 🐧 run_tests.sh                        # Automated test suite
│
├── 🤖 ai_agent/                           # AI Agent Component
│   ├── agent_app.py                       # Main AI agent (Python)
│   │                                      # - Connects to Ollama
│   │                                      # - Processes prompts
│   │                                      # - Executes tools
│   │                                      # - Demonstrates vulnerability
│   │
│   ├── tools.py                           # Tool implementations
│   │                                      # - http_request()
│   │                                      # - file_operation()
│   │                                      # - database_query()
│   │                                      # - All simulated for safety
│   │
│   └── config.json                        # Agent configuration
│                                          # - Model: llama3
│                                          # - Temperature: 0.7
│                                          # - Available tools
│
├── 🛡️ security/                           # Security Middleware Layer
│   ├── security_proxy.py                  # Main security middleware (Flask)
│   │                                      # - Port 5001
│   │                                      # - Validates all requests
│   │                                      # - Pattern matching
│   │                                      # - URL validation
│   │                                      # - Action filtering
│   │                                      # - Endpoints:
│   │                                      #   POST /secure/agent
│   │                                      #   POST /secure/n8n
│   │                                      #   POST /validate
│   │                                      #   GET  /rules
│   │
│   ├── logger.py                          # Logging API server (Flask)
│   │                                      # - Port 5002
│   │                                      # - Stores events to logs.json
│   │                                      # - Endpoints:
│   │                                      #   GET /logs
│   │                                      #   GET /logs/recent
│   │                                      #   GET /alerts
│   │                                      #   GET /stats
│   │
│   ├── rules.json                         # Security rules (EDITABLE)
│   │                                      # - Blocked keywords
│   │                                      # - Suspicious patterns (regex)
│   │                                      # - Dangerous actions
│   │                                      # - Allowed domains
│   │                                      # - Severity levels
│   │
│   └── logs.json                          # Event log (AUTO-GENERATED)
│                                          # - All requests logged here
│                                          # - JSON format
│                                          # - Read by dashboard
│
├── 📊 dashboard/                          # Web Dashboard (Frontend)
│   ├── index.html                         # Main dashboard page
│   │                                      # - Statistics cards
│   │                                      # - Recent alerts panel
│   │                                      # - Activity log
│   │                                      # - Severity breakdown
│   │                                      # - Auto-refresh every 3s
│   │
│   ├── input.html                         # ⭐ NEW: Input submission page
│   │                                      # - Select target (AI/n8n)
│   │                                      # - Enter prompt
│   │                                      # - Submit direct or secure
│   │                                      # - Example prompts
│   │                                      # - Live result display
│   │
│   ├── style.css                          # Dashboard styling
│   │                                      # - Dark theme
│   │                                      # - Responsive design
│   │                                      # - Beautiful cards
│   │                                      # - Animations
│   │
│   └── script.js                          # Dashboard logic
│                                          # - Fetches from API
│                                          # - Updates UI
│                                          # - Auto-refresh
│                                          # - Toast notifications
│
├── ⚡ n8n/                                # n8n Workflow Demo
│   ├── workflow.json                      # Importable n8n workflow
│   │                                      # - Webhook trigger
│   │                                      # - AI decision node
│   │                                      # - HTTP request node
│   │                                      # - Demonstrates vulnerability
│   │
│   └── README.md                          # n8n setup instructions
│                                          # - Docker commands
│                                          # - Import workflow
│                                          # - Test scenarios
│
└── 📁 logs/                               # Log files (AUTO-CREATED)
    ├── security_proxy.log                 # Security middleware output
    ├── logger.log                         # Logger API output
    └── dashboard.log                      # Dashboard server output
```

## 🎯 Key Files Explained

### Windows Launcher Files (⭐ NEW)

```
start_demo.bat
├─ Checks Python installed
├─ Checks Ollama running
├─ Creates logs/ folder
├─ Starts security_proxy.py (minimized window)
├─ Starts logger.py (minimized window)
├─ Starts dashboard HTTP server (minimized window)
├─ Opens browser to http://localhost:8000
└─ Waits (Ctrl+C to stop)

stop_demo.bat
├─ Kills all running demo services
├─ Closes minimized windows
└─ Cleans up processes
```

### Dashboard Files

```
dashboard/index.html
├─ Main monitoring interface
├─ Shows statistics
├─ Displays alerts
├─ Activity log
└─ Auto-refreshes

dashboard/input.html (⭐ NEW)
├─ User input interface
├─ Target selection (AI Agent / n8n)
├─ Prompt entry
├─ Example prompts
├─ Submit buttons (direct/secure)
└─ Result display
```

### Security Layer

```
security/security_proxy.py
├─ Main Flask application
├─ Validates incoming requests
├─ Checks against rules.json
├─ Logs to logs.json (via logger.py)
└─ Returns 200 OK or 403 Forbidden

security/logger.py
├─ Separate Flask API
├─ Writes to logs.json
├─ Provides read endpoints
└─ Calculates statistics

security/rules.json
├─ Configurable security rules
├─ Edit to customize detection
└─ Supports regex patterns

security/logs.json
├─ JSON array of events
├─ Each event has:
│   ├─ timestamp
│   ├─ source (ai_agent/n8n)
│   ├─ prompt
│   ├─ action (allowed/blocked)
│   ├─ reason
│   ├─ severity
│   └─ metadata
└─ Auto-managed (keep last 1000)
```

## 🔄 Data Flow

```
1. User Input
   └─> dashboard/input.html

2. User submits prompt
   ├─> Direct: Shows warning (simulation)
   └─> Secure: POST to security/security_proxy.py

3. Security validation
   ├─> Reads security/rules.json
   ├─> Analyzes prompt
   └─> Writes to security/logs.json

4. Dashboard updates
   └─> dashboard/script.js polls security/logger.py

5. Display results
   ├─> dashboard/index.html (monitoring)
   └─> dashboard/input.html (immediate result)
```

## 📍 Where to Put New Files

### Adding New Dashboard Pages
```
dashboard/
├── index.html          (existing - main dashboard)
├── input.html          (existing - input page)
└── your-page.html      (add here)
```

### Adding New Security Rules
```
security/
├── rules.json          (edit this file)
└── custom-rules.json   (or create new)
```

### Adding New AI Tools
```
ai_agent/
├── tools.py            (add functions here)
└── custom_tools.py     (or create new module)
```

### Adding New Scripts
```
Root directory:
├── start_demo.bat      (Windows launcher)
├── start_demo.sh       (Linux/Mac launcher)
└── your-script.bat     (add custom scripts)
```

## 🔧 Configuration Files

### Editable Configuration
```
security/rules.json         ← Customize security rules
ai_agent/config.json        ← Adjust AI agent settings
n8n/workflow.json           ← Modify workflow behavior
```

### Auto-Generated (Don't Edit Manually)
```
security/logs.json          ← Written by logger.py
logs/*.log                  ← Service output logs
```

## 🚀 Entry Points

### For Windows Users
```
1. Double-click: start_demo.bat
2. Open browser: http://localhost:8000/input.html
3. Press Ctrl+C to stop
```

### For Linux/Mac Users
```
1. Run: ./start_demo.sh
2. Open browser: http://localhost:8000/input.html
3. Press Ctrl+C or run: ./stop_demo.sh
```

## 📦 Dependencies

### Python Packages (requirements.txt)
```
flask==3.0.0            ← Web framework
flask-cors==4.0.0       ← Cross-origin requests
requests==2.31.0        ← HTTP library
ollama==0.1.6           ← Ollama client
python-dotenv==1.0.0    ← Environment variables
```

### External Services
```
Ollama                  ← LLM runtime (localhost:11434)
Docker (optional)       ← For n8n (localhost:5678)
```

## 🎯 URLs & Ports

```
Service               URL                              File
─────────────────────────────────────────────────────────────
Dashboard            http://localhost:8000            dashboard/index.html
Input Page           http://localhost:8000/input.html dashboard/input.html
Security Proxy       http://localhost:5001            security/security_proxy.py
Logger API           http://localhost:5002            security/logger.py
Ollama               http://localhost:11434           (external)
n8n (optional)       http://localhost:5678            (Docker)
```

## 📊 Log Locations

```
Service Logs:
├── logs/security_proxy.log    ← Security middleware output
├── logs/logger.log             ← Logger API output
└── logs/dashboard.log          ← Dashboard server output

Event Logs:
└── security/logs.json          ← All security events (JSON)
```

## ✅ File Checklist

When setting up, you should have:

```
✅ start_demo.bat           (Windows)
✅ stop_demo.bat            (Windows)
✅ start_demo.sh            (Linux/Mac)
✅ stop_demo.sh             (Linux/Mac)
✅ dashboard/input.html     (New input page)
✅ WINDOWS_GUIDE.md         (Windows documentation)
✅ All Python files
✅ All JSON config files
✅ All documentation files
```

---

**File structure complete! All files are in their proper locations.** 🎯