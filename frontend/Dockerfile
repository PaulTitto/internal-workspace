# Multi-stage Dockerfile for Frontend Vue 3 + Vite
# Stage 1: Build static assets
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package descriptors
COPY package*.json ./

# Install dependencies cleanly
RUN npm ci || npm install

# Copy source code
COPY . .

# Build argument for backend API URL (default: /api/v1 for reverse proxy or direct host)
ARG VITE_FLASK_API_URL=http://localhost:5001/api/v1
ENV VITE_FLASK_API_URL=${VITE_FLASK_API_URL}

# Build production bundle
RUN npm run build

# Stage 2: Serve with lightweight Nginx
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
