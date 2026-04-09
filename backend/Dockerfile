FROM amazonlinux:2023

# Install Python 3.11, pip, curl (healthcheck), and antiword (.doc extraction)
# antiword is not in AL2023 default repos — install fails silently, app handles it gracefully
RUN dnf update -y && \
    dnf install -y python3.11 python3.11-pip curl && \
    dnf install -y antiword 2>/dev/null || true && \
    dnf clean all

# Make python3 / pip3 point to 3.11
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/pip3.11   /usr/bin/pip3

WORKDIR /app

# Install Python dependencies first (cached layer)
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p uploads data

# Make entrypoint executable
RUN chmod +x entrypoint.sh

EXPOSE 5001
ENTRYPOINT ["/app/entrypoint.sh"]
