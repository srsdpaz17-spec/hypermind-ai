# Deployment Architecture - HyperMind Enterprise AI OS

**Version**: 1.0  
**Date**: 2026-07-05  
**Environments**: Development, Staging, Production

---

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Local Development Setup](#local-development-setup)
3. [Docker Architecture](#docker-architecture)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [CI/CD Pipelines](#cicd-pipelines)
6. [Monitoring & Observability](#monitoring--observability)
7. [Disaster Recovery](#disaster-recovery)
8. [Scaling Strategy](#scaling-strategy)

---

## Deployment Overview

### Architecture Layers

```
┌──────────────────────────────────────────────────────────┐
│                   End Users                              │
│   (Web, Desktop, Mobile via Vercel CDN)                 │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│              Cloudflare / AWS Shield                     │
│         (DDoS Protection, WAF, Caching)                 │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│              API Gateway / Load Balancer                 │
│         (Request routing, Rate limiting, Auth)          │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│            Kubernetes Cluster (EKS/GKE)                 │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Namespace: hypermind-prod                        │ │
│  │  ├── Backend Deployment (3 replicas)             │ │
│  │  ├── Frontend Deployment (2 replicas)            │ │
│  │  ├── Worker Deployment (2 replicas)              │ │
│  │  ├── Ingress Controller                          │ │
│  │  ├── ConfigMaps & Secrets                        │ │
│  │  └── StatefulSets (RabbitMQ, Redis)             │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│            Managed Services (AWS / GCP)                  │
│  ├── RDS PostgreSQL (Multi-AZ)                         │
│  ├── ElastiCache Redis                                 │
│  ├── Qdrant Vector DB                                  │
│  ├── S3 Object Storage                                 │
│  └── SQS/SNS (Messaging)                               │
└──────────────────────────────────────────────────────────┘
```

---

## Local Development Setup

### Prerequisites

```bash
# Required tools
- Docker (v24+)
- Docker Compose (v2+)
- Python 3.11+
- Node.js 18+
- Git
- Bash/Shell

# Optional tools
- Postman (API testing)
- pgAdmin (Database management)
- Redis CLI (Cache inspection)
- Kind (local Kubernetes)
```

### Docker Compose Setup

```yaml
# docker-compose.dev.yml
version: '3.9'

services:
  # Backend (Python/FastAPI)
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/hypermind
      REDIS_URL: redis://redis:6379
      QDRANT_URL: http://qdrant:6333
      RABBITMQ_URL: amqp://rabbitmq:5672
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      JWT_SECRET: ${JWT_SECRET}
      ENV: development
    depends_on:
      - postgres
      - redis
      - qdrant
      - rabbitmq
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --reload

  # Frontend (Next.js)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api/v1
      NEXT_PUBLIC_ENV: development
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
    command: npm run dev

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: hypermind
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/migrations:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Qdrant Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    environment:
      QDRANT_API_ENABLE_CONSOLE: "true"
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  # RabbitMQ Message Queue
  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: user
      RABBITMQ_DEFAULT_PASS: password
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # pgAdmin (Database GUI)
  pgadmin:
    image: dpage/pgadmin4:latest
    ports:
      - "5050:80"
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin
    depends_on:
      - postgres

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
  rabbitmq_data:
```

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/hypermind-ai/hypermind-enterprise.git
cd hypermind-enterprise

# 2. Create .env file
cp .env.example .env.local

# 3. Add secrets
echo "OPENAI_API_KEY=sk-..." >> .env.local
echo "JWT_SECRET=$(openssl rand -base64 32)" >> .env.local

# 4. Start development environment
docker-compose -f docker-compose.dev.yml up -d

# 5. Run database migrations
docker-compose exec backend alembic upgrade head

# 6. Seed sample data
docker-compose exec backend python scripts/seed_data.py

# 7. Access applications
# Backend API: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
# RabbitMQ: http://localhost:15672 (user:password)
# pgAdmin: http://localhost:5050
```

---

## Docker Architecture

### Backend Dockerfile

```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Build Next.js app
ENV NEXT_PUBLIC_ENV=production
RUN npm run build

# Runtime stage
FROM node:18-alpine

WORKDIR /app

ENV NODE_ENV=production

# Copy dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy built application
COPY --from=builder /app/.next /app/.next
COPY --from=builder /app/public /app/public
COPY --from=builder /app/next.config.js /app/next.config.js

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
USER nextjs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

EXPOSE 3000

CMD ["npm", "start"]
```

---

## Kubernetes Deployment

### K8s Directory Structure

```
infrastructure/kubernetes/
├── base/
│   ├── kustomization.yaml
│   ├── namespace.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── worker-deployment.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   ├── rbac.yaml
│   ├── network-policy.yaml
│   ├── storage-class.yaml
│   └── ingress.yaml
│
└── overlays/
    ├── dev/
    │   ├── kustomization.yaml
    │   ├── replicas-patch.yaml
    │   └── resource-limits-patch.yaml
    ├── staging/
    │   ├── kustomization.yaml
    │   ├── replicas-patch.yaml
    │   └── resource-limits-patch.yaml
    └── prod/
        ├── kustomization.yaml
        ├── replicas-patch.yaml
        ├── resource-limits-patch.yaml
        ├── hpa.yaml
        └── pdb.yaml
```

### Backend Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: hypermind-prod
  labels:
    app: backend
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
        version: v1
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - backend
                topologyKey: kubernetes.io/hostname
      
      serviceAccountName: backend
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      
      initContainers:
        - name: migrate
          image: hypermind/backend:latest
          command: ["alembic", "upgrade", "head"]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: backend-secrets
                  key: database-url
      
      containers:
        - name: backend
          image: hypermind/backend:latest
          imagePullPolicy: IfNotPresent
          
          ports:
            - name: http
              containerPort: 8000
              protocol: TCP
          
          env:
            - name: ENV
              value: "production"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: backend-secrets
                  key: database-url
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: backend-config
                  key: redis-url
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: backend-secrets
                  key: openai-api-key
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: backend-secrets
                  key: jwt-secret
          
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 5
            failureThreshold: 3
          
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          
          securityContext:
            allowPrivilegeEscalation: false
            capabilities:
              drop:
                - ALL
            readOnlyRootFilesystem: true
          
          volumeMounts:
            - name: tmp
              mountPath: /tmp
            - name: cache
              mountPath: /app/.cache
      
      volumes:
        - name: tmp
          emptyDir: {}
        - name: cache
          emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: hypermind-prod
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
    - name: http
      port: 80
      targetPort: 8000
      protocol: TCP
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: hypermind-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 30
        - type: Pods
          value: 2
          periodSeconds: 30
      selectPolicy: Max
```

---

## CI/CD Pipelines

### GitHub Actions Workflow

```yaml
# .github/workflows/cd-backend.yml
name: Deploy Backend

on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'
      - 'infrastructure/kubernetes/**'

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements-dev.txt
      
      - name: Run linting
        run: |
          flake8 backend/ --count --show-source --statistics
          black backend/ --check
          isort backend/ --check-only
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
        run: |
          pytest backend/tests --cov --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/backend:latest
            ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure kubectl
        run: |
          mkdir -p $HOME/.kube
          echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > $HOME/.kube/config
      
      - name: Update image in K8s
        run: |
          kubectl set image deployment/backend \
            backend=ghcr.io/${{ github.repository }}/backend:${{ github.sha }} \
            -n hypermind-prod
      
      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/backend -n hypermind-prod --timeout=5m
      
      - name: Verify deployment
        run: |
          kubectl get pods -n hypermind-prod -l app=backend
          kubectl logs -n hypermind-prod -l app=backend --tail=50
```

---

## Monitoring & Observability

### Prometheus Metrics

```
# Backend metrics
hypermind_http_requests_total{method="GET",path="/users",status="200"}
hypermind_http_request_duration_seconds{method="GET",path="/users"}
hypermind_database_query_duration_seconds{query="select_users"}
hypermind_cache_hits_total
hypermind_cache_misses_total
hypermind_active_connections
hypermind_task_executions_total{status="success"}
hypermind_task_execution_duration_seconds
hypermind_ai_agent_processing_time
```

### Alert Rules

```yaml
groups:
  - name: hypermind
    rules:
      - alert: HighErrorRate
        expr: rate(hypermind_http_requests_total{status="5xx"}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
      
      - alert: HighLatency
        expr: histogram_quantile(0.99, hypermind_http_request_duration_seconds) > 1
        for: 5m
        annotations:
          summary: "P99 latency > 1 second"
      
      - alert: DatabaseConnectionPoolExhausted
        expr: hypermind_db_connections_used / hypermind_db_connections_max > 0.9
        for: 2m
        annotations:
          summary: "Database connection pool 90% full"
```

---

## Disaster Recovery

### Backup Strategy

```
PostgreSQL Backups:
├── Daily: Full backup
├── Hourly: Incremental WAL
├── Storage: S3 (multi-region)
├── Retention: 30 days
└── Recovery: RTO 30 min, RPO 1 hour

Redis Backups:
├── Hourly: RDB snapshot
├── Storage: S3
├── Retention: 7 days
└── Note: Cache, not critical

Database Recovery:
1. Restore latest full backup
2. Apply WAL logs (point-in-time recovery)
3. Validate data integrity
4. Run health checks
5. Failover to recovered instance
```

### Failover Procedures

```
RDS PostgreSQL Failover:
├── Trigger: Manual or automatic
├── Replica promoted: < 2 minutes
├── Client connections: Auto-reconnect
├── Data loss: Zero (synchronous replication)

Application Failover:
├── K8s controller detects pod failure
├── Pod automatically restarted
├── New pod joins load balancer
├── No manual intervention needed
```

---

## Scaling Strategy

### Horizontal Scaling

```
Auto-scaling Triggers:
├── CPU > 70%: Scale up (add 1-2 pods)
├── Memory > 80%: Scale up
├── CPU < 30% (5 min): Scale down
├── Minimum: 3 pods
├── Maximum: 10 pods

Time-based Scaling (future):
├── Peak hours (9-18): 8+ pods
├── Off-hours (18-9): 3-4 pods
└── Weekends: 3 pods
```

### Vertical Scaling

```
Resource Limits (per pod):
├── Backend CPU: 500m (request), 1000m (limit)
├── Backend Memory: 512Mi (request), 1Gi (limit)
├── Frontend CPU: 200m (request), 500m (limit)
├── Frontend Memory: 256Mi (request), 512Mi (limit)

Database Scaling:
├── Read replicas: Add for analytics
├── Connection pooling: PgBouncer
├── Caching: Redis for frequently accessed data
```

### Database Scaling

```
Query Optimization:
├── Indexing: Strategic indexes for common queries
├── Query plans: EXPLAIN ANALYZE
├── Partitioning: Large tables (e.g., audit logs)
├── Archiving: Move old data to cold storage

Read Scaling:
├── Primary: All writes
├── Replica 1: Application reads (1-2s lag)
├── Replica 2: Analytics (configurable lag)
└── Read-only endpoint load balancing
```

---

**Status**: ⏳ AWAITING DEVOPS TEAM REVIEW

