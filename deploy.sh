#!/bin/bash
# ============================================================
# AI Web Chat App — EC2 Deployment Script
# Host OS : RHEL 9 (Red Hat Enterprise Linux 9)
# Docker images: amazonlinux:2023 (pulled from Docker Hub)
# Usage: bash deploy.sh
# ============================================================
set -e

echo ""
echo "============================================"
echo " AI Web Chat App — EC2 Deployment"
echo "============================================"
echo ""

# ── 1. Install Docker CE on RHEL 9 ───────────────────────────
# RHEL 9 does not ship Docker in its default repos.
# We add the official Docker CE repo (supports RHEL 9).
if ! command -v docker &>/dev/null; then
    echo "[1/5] Installing Docker CE on RHEL 9..."
    sudo dnf update -y

    # Remove any old/conflicting packages (podman, etc.)
    sudo dnf remove -y docker docker-client docker-client-latest \
        docker-common docker-latest docker-latest-logrotate \
        docker-logrotate docker-engine podman runc 2>/dev/null || true

    # Add Docker CE repo for RHEL
    sudo dnf install -y yum-utils
    sudo yum-config-manager --add-repo \
        https://download.docker.com/linux/rhel/docker-ce.repo

    # Install Docker CE + Compose plugin
    sudo dnf install -y \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin

    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker "$USER"
    echo "      Docker CE installed."
else
    echo "[1/5] Docker already installed: $(docker --version)"
fi

# ── 2. Ensure Docker Compose plugin is present ────────────────
if ! docker compose version &>/dev/null; then
    echo "[2/5] Installing Docker Compose plugin..."
    sudo dnf install -y docker-compose-plugin 2>/dev/null || \
    sudo curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
         -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose
else
    echo "[2/5] Docker Compose already installed: $(docker compose version)"
fi

# ── 3. Make sure Docker daemon is running ─────────────────────
if ! docker info &>/dev/null; then
    echo "      Starting Docker daemon..."
    sudo systemctl start docker
    # Temporary socket permission so current session can use docker immediately
    # (without needing logout/login for group change to take effect)
    sudo chmod 666 /var/run/docker.sock 2>/dev/null || true
fi

# ── 4. Locate the app directory ───────────────────────────────
echo "[3/5] Locating application..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "      Working directory: $SCRIPT_DIR"

if [ ! -f "docker-compose.yml" ]; then
    echo "ERROR: docker-compose.yml not found in $SCRIPT_DIR"
    echo "       Run this script from the ai-web-chat-app root directory."
    exit 1
fi

# ── 5. Pre-flight reminder ────────────────────────────────────
echo ""
echo "[4/5] Pre-flight checklist"
echo "──────────────────────────────────────────────"
echo " Before launching, verify the following:"
echo ""
echo " 1. EC2 IAM Role has these permissions:"
echo "    - bedrock:InvokeModel"
echo "    - bedrock:InvokeModelWithResponseStream"
echo "    - rekognition:DetectLabels / DetectText"
echo "    - textract:DetectDocumentText"
echo "    - sts:GetCallerIdentity"
echo "    Tip: Attach AmazonBedrockFullAccess +"
echo "         AmazonRekognitionFullAccess +"
echo "         AmazonTextractFullAccess"
echo ""
echo " 2. Security Group / firewall allows inbound TCP 8080"
echo "    from your internal network (e.g. 172.16.0.0/12)"
echo ""
echo " 3. docker-compose.yml SECRET_KEY is changed"
echo "    (current value: change_me_to_a_long_random_string_before_deploying)"
echo ""
read -rp " Press Enter to continue (Ctrl+C to abort)..."

# ── 6. Build and launch ───────────────────────────────────────
echo ""
echo "[5/5] Building and launching containers..."
echo "      (First build takes ~5 minutes — it compiles React and installs Python deps)"
echo ""

docker compose up -d --build

echo ""
echo "──────────────────────────────────────────────"
echo " Container status:"
docker compose ps
echo ""

PRIVATE_IP=$(hostname -I | awk '{print $1}')

echo "============================================"
echo " DEPLOYMENT COMPLETE"
echo "============================================"
echo ""
echo " App URL:     http://$PRIVATE_IP:8080"
echo " Admin login: admin / admin123"
echo ""
echo " IMPORTANT: Change the admin password after first login!"
echo ""
echo " Useful commands:"
echo "   docker compose logs -f backend   # backend logs"
echo "   docker compose logs -f nginx     # nginx logs"
echo "   docker compose ps               # container status"
echo "   docker compose restart          # restart all"
echo "   docker compose down             # stop (keeps DB)"
echo "   git pull && docker compose up -d --build  # update"
echo "============================================"
