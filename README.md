# AI Web Chat App

A full-stack AI assistant platform powered by AWS Bedrock. Supports multiple AI models, real-time streaming responses, document analysis, image generation, and image analysis — with full user authentication and activity logging.

---

## Features

- **AI Chatbot** — Streaming chat with model selection
- **Coding Assistant** — Syntax-highlighted code responses with language hints
- **Document Analyzer** — Upload and analyze TXT, PDF, DOCX files
- **Image Generator** — Text-to-image via Titan Image Generator
- **Image Analyzer** — AWS Rekognition + Textract OCR
- **User Authentication** — Register, login, sessions, admin panel
- **Activity Logging** — Full history of queries, actions, and logins

## Available Models (all via AWS Bedrock)

| Model | Key |
|---|---|
| Claude Sonnet 4.5 | `claude-sonnet-4-5` |
| Claude Opus 4.5 | `claude-opus-4-5` |
| Llama 3 70B | `llama3-70b` |
| Llama 3 8B | `llama3-8b` |
| Titan Text Premier | `titan-text` |

---

## Option 1 — Docker (recommended for EC2 / servers)

### Prerequisites

- Docker and Docker Compose installed
- EC2 IAM role with the following policies attached:
  - `AmazonBedrockFullAccess`
  - `AmazonRekognitionFullAccess`
  - `AmazonTextractFullAccess`

No AWS keys needed — credentials come automatically from the EC2 IAM role.

### Quick deploy on EC2 (RHEL 9)

```bash
git clone <your-repo-url> ai-web-chat-app
cd ai-web-chat-app

# Edit SECRET_KEY in docker-compose.yml before launching
nano docker-compose.yml

bash deploy.sh
```

`deploy.sh` installs Docker CE, builds the images, and starts all containers.

### Manual Docker commands

```bash
# Build and start
docker compose up -d --build

# View logs
docker compose logs -f backend
docker compose logs -f nginx

# Check status
docker compose ps

# Stop (database is preserved in Docker volume)
docker compose down

# Update after code changes
git pull
docker compose up -d --build
```

### Access

```
http://<private-ip>:8080
```

Open port **8080** in your EC2 Security Group (inbound, TCP).

### Configuration (docker-compose.yml)

```yaml
environment:
  AWS_DEFAULT_REGION: us-east-1           # your Bedrock region
  SECRET_KEY: change_me_to_random_string  # change this
  DEFAULT_CHAT_MODEL: claude-sonnet-4-5
  DEFAULT_CODE_MODEL: claude-sonnet-4-5
  MAX_TOKENS: "2048"
```

### Architecture

```
:8080
  Nginx  →  /api/*  →  Flask :5001 (internal)
         →  /*      →  React SPA (static)
                          ↓
                    AWS Bedrock / Rekognition / Textract
                          ↓
                    sqlite_data (Docker named volume on EBS)
```

---

## Option 2 — Local (without Docker)

### Prerequisites

- Python 3.11+
- Node.js 18+
- AWS CLI configured (`aws configure`)
- AWS credentials with Bedrock access

### 1. Backend setup

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template.new .env
# Edit .env — set at minimum:
#   AWS_DEFAULT_REGION=us-east-1
#   SECRET_KEY=any-random-string

# Initialize database (creates admin user)
python init_db.py

# Start backend
python app.py
```

Backend runs on `http://localhost:5001`.

### 2. Frontend setup

```bash
cd frontend-new

# Install dependencies
npm install

# Start dev server (with hot reload, proxies /api to localhost:5001)
npm run dev
```

Frontend dev server runs on `http://localhost:5173`.

Alternatively, build and serve the static files:

```bash
npm run build           # outputs to frontend/dist/
cd ../frontend/dist
python3 -m http.server 8000
# access at http://localhost:8000
```

### 3. Or use the start script

```bash
chmod +x start.sh
./start.sh
```

This installs dependencies, builds the frontend, starts the backend, and serves the built app on port 8000.

### AWS credentials (local)

```bash
# Configure default profile
aws configure

# Or use a named profile
aws configure --profile myprofile
# then set in backend/.env:
# AWS_PROFILE=myprofile
```

Verify setup:

```bash
python test_aws_credentials.py
```

---

## Default Admin Account

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `admin123` |

**Change the password immediately after first login.**

To reset admin credentials:

```bash
# Local
cd backend && python reset_admin.py

# Docker
docker compose exec backend python reset_admin.py
```

---

## Project Structure

```
ai-web-chat-app/
├── docker-compose.yml          # Docker orchestration
├── deploy.sh                   # EC2 one-shot deploy script (RHEL 9)
├── start.sh                    # Local start script
│
├── backend/
│   ├── Dockerfile
│   ├── entrypoint.sh           # DB init + gunicorn start
│   ├── app.py                  # Flask app, streaming endpoints
│   ├── config.py               # Model registry, config
│   ├── models.py               # SQLAlchemy models
│   ├── auth.py                 # Auth routes
│   ├── logs.py                 # Logging routes
│   ├── admin.py                # Admin routes
│   ├── aws_credentials.py      # Secure AWS credential manager
│   ├── requirements.txt        # Pinned Python dependencies
│   └── init_db.py              # DB init + default admin
│
├── frontend-new/               # React + Vite source
│   ├── src/
│   │   ├── components/         # Chat, Code, Auth, Admin, History, ...
│   │   ├── hooks/              # useStream, useAuth, useToast
│   │   └── api/client.js       # API wrapper
│   └── package.json
│
├── nginx/
│   ├── Dockerfile              # Multi-stage: node build + nginx serve
│   └── nginx.conf              # SPA routing + /api proxy + SSE headers
│
└── frontend/dist/              # Built React app (generated, not committed)
```

---

## API Endpoints

### Auth
| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/check` | Check session |
| GET | `/api/auth/profile` | Get profile |
| POST | `/api/auth/change-password` | Change password |

### AI (all require login, all stream SSE)
| Method | Path | Description |
|---|---|---|
| POST | `/api/chat` | Chat — body: `{message, model}` |
| POST | `/api/code-chat` | Coding assistant — body: `{message, model}` |
| POST | `/api/document-analyze` | Document analysis — multipart file |
| POST | `/api/generate-image` | Image generation — body: `{prompt}` |
| POST | `/api/analyze-image` | Image analysis — multipart file |
| GET | `/api/models` | List available models |

### Logs
| Method | Path | Description |
|---|---|---|
| GET | `/api/logs/searches` | Search history |
| GET | `/api/logs/actions` | Action history |
| GET | `/api/logs/logins` | Login history |
| GET | `/api/logs/stats` | Usage stats |
| GET | `/api/logs/export` | Export all data as JSON |

### System
| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/aws-status` | AWS credential status |

---

## Troubleshooting

**Bedrock access denied**
- Ensure models are enabled in AWS Console → Bedrock → Model access
- Check IAM role/user has `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream`
- Run `python test_aws_credentials.py` to verify

**Streaming not working behind a proxy / load balancer**
- Ensure proxy has `proxy_buffering off` and long read timeouts (nginx.conf already set to 300s)

**Docker: backend stays unhealthy**
```bash
docker compose logs backend   # check for startup errors
```

**Local: frontend can't reach backend**
- Ensure backend is running on port 5001
- In dev mode (`npm run dev`) the Vite proxy handles `/api` automatically
- In built mode, ensure backend CORS allows the frontend origin

**File upload fails**
- Max size is 16 MB
- Supported: `.txt`, `.md`, `.pdf`, `.doc`, `.docx`, `.png`, `.jpg`, `.jpeg`, `.gif`
