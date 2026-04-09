# Stage 1: Build React app with Vite
FROM amazonlinux:2023 AS builder

# Install Node.js (AL2023 ships Node 18 LTS — fully compatible with Vite)
RUN dnf install -y nodejs npm && dnf clean all

WORKDIR /build

# Install dependencies first (cached layer)
COPY frontend-new/package*.json ./
RUN npm ci --silent

# Copy source and build
# Override outDir so the output stays inside /build/dist
# (the repo's vite.config.js points to ../frontend/dist which doesn't exist here)
COPY frontend-new/ ./
RUN npx vite build --outDir ./dist --emptyOutDir

# Stage 2: Serve with Nginx on Amazon Linux 2023
FROM amazonlinux:2023

RUN dnf install -y nginx && dnf clean all

COPY --from=builder /build/dist /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
