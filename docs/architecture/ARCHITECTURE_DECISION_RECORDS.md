# Architecture Decision Records (ADRs)

## ADR-001: Clean Architecture with DDD

**Status**: APPROVED  
**Date**: 2026-07-05  
**Deciders**: Architecture Team

### Context
HyperMind needs to scale from a monolithic chatbot to an enterprise AI operating system supporting multiple business domains, multi-tenancy, and complex integrations.

### Decision
Adopt **Clean Architecture** layers combined with **Domain-Driven Design (DDD)** principles.

### Rationale
1. **Separation of Concerns**: Each layer has distinct responsibilities
   - Domain Layer: Pure business logic (no frameworks)
   - Application Layer: Use cases and orchestration
   - Presentation Layer: API controllers and DTOs
   - Infrastructure Layer: Database, external services, implementations

2. **Scalability**: Domain logic is framework-agnostic, allowing:
   - Easy migration between frameworks
   - Parallel team development on different domains
   - Simple unit testing without mocks

3. **DDD Benefits**:
   - Bounded contexts prevent model bloat
   - Ubiquitous language across code and documentation
   - Business logic lives in domain entities, not databases
   - Easier to understand and modify

4. **Testability**: 
   - Domain layer can be tested without database or web framework
   - Application layer tests are isolated from infrastructure
   - Integration tests can mock external services

### Consequences
- **Positive**: Code is more maintainable, scalable, testable, and aligned with business
- **Positive**: Easier to onboard new developers with clear architectural patterns
- **Negative**: Initial setup is more complex than a monolith
- **Negative**: Requires discipline to enforce layer boundaries

### Implementation
- Backend organized into: `presentation/`, `application/`, `domain/`, `infrastructure/`
- Each module has its own bounded context
- Repository pattern used for all data access
- Dependency Injection for loose coupling

---

## ADR-002: Multi-Tenancy Strategy - Schema Isolation

**Status**: APPROVED  
**Date**: 2026-07-05  
**Deciders**: Architecture Team

### Context
HyperMind is a SaaS platform serving multiple organizations. Need to decide how to isolate tenant data.

### Decision
Use **PostgreSQL schema-per-tenant** approach with shared public schema for system-wide data.

### Architecture
```
postgres_database/
├── public schema        # Shared across all tenants
│   ├── tenants         # Organization records
│   ├── users           # System users
│   ├── roles           # RBAC definitions
│   ├── permissions     # Permission matrix
│   └── audit_logs      # System-wide audit
│
└── tenant_<uuid> schema # One per organization
    ├── companies       # Organization data
    ├── employees       # HR records
    ├── crm_*          # CRM entities
    ├── workflows      # Business processes
    └── [all business tables]
```

### Rationale
1. **Data Isolation**: Complete database schema isolation per tenant
   - Maximum security - different schemas mean no accidental cross-tenant queries
   - Backup/restore per tenant possible
   - GDPR compliance easier (delete entire schema)

2. **Performance**: 
   - Schema indexes don't clash
   - Query planner optimizes per tenant
   - Connection pooling per tenant possible

3. **Operational**: 
   - Scale tenants independently
   - Run analytics per tenant easily
   - Migrate tenants to different databases

4. **Compliance**: 
   - Clear audit trail (public.audit_logs)
   - Data deletion compliance (drop schema)
   - Access control at schema level

### Consequences
- **Positive**: Maximum security and compliance
- **Positive**: Easy to implement GDPR right-to-delete
- **Negative**: More complex schema migrations (run per tenant)
- **Negative**: Difficult to run cross-tenant queries (need UNION approach)

### Implementation
1. Middleware sets tenant context from JWT token
2. All queries automatically scoped to tenant schema
3. Migrations run per-tenant
4. Audit logs centralized in public schema

---

## ADR-003: Event-Driven Architecture

**Status**: APPROVED  
**Date**: 2026-07-05  
**Deciders**: Architecture Team

### Context
HyperMind needs:
- Audit trail of all system events
- Asynchronous processing of heavy operations
- Scalability through message queues
- Eventual consistency between bounded contexts

### Decision
Implement **event-driven architecture** using:
- Domain events for all state changes
- Event bus (RabbitMQ/Kafka) for asynchronous processing
- Event sourcing for critical operations
- Message-driven integration between modules

### Architecture
```
Event Flow:
1. User action in presentation layer
2. Application use case executes
3. Domain event created (UserCreated, PaymentProcessed, etc.)
4. Event published to event bus
5. Event handlers subscribe (via message queue)
6. Async processors execute side effects
7. Event stored in audit log
```

### Rationale
1. **Decoupling**: Modules communicate via events, not direct calls
2. **Scalability**: Heavy operations (email, notifications) async
3. **Auditability**: Complete event log for compliance
4. **Resilience**: Retry failed operations, dead-letter queues
5. **Debugging**: Event replays help troubleshoot issues

### Event Types
```python
# Domain Events (critical business events)
- UserRegistered
- CompanyCreated
- EmployeeHired
- PaymentProcessed
- WorkflowCompleted

# Integration Events (cross-module)
- ContactCreated → triggers CRM, notification, analytics
- OrderPlaced → triggers payment, notification, inventory

# System Events (infrastructure)
- ServiceStarted
- ConfigurationChanged
- SecurityAlertTriggered
```

### Consequences
- **Positive**: Highly scalable and resilient
- **Positive**: Complete audit trail for compliance
- **Positive**: Easy to add new features without modifying existing code
- **Negative**: Eventual consistency (complex to reason about)
- **Negative**: Requires message queue infrastructure
- **Negative**: Harder to debug distributed systems

### Implementation
1. All domain aggregates publish events
2. Event bus publishes events to RabbitMQ/Kafka
3. Async handlers subscribe to events
4. Event sourcing for payment and contract modules
5. Dead-letter queues for failed events

---

## ADR-004: API Versioning Strategy

**Status**: APPROVED  
**Date**: 2026-07-05  
**Deciders**: Architecture Team

### Context
HyperMind API will evolve over time. Need strategy for backward compatibility.

### Decision
Use **URL path versioning** with support for multiple major versions.

### Architecture
```
/api/v1/users           # Version 1 (current)
/api/v2/users           # Version 2 (future)
/api/v3/users           # Version 3 (future)

Each version can have different:
- Request/response schemas
- Behavior/business logic
- Database queries
```

### Rationale
1. **Explicit Versioning**: Easy to see which version is being used
2. **Clear Support Window**: Can deprecate old versions
3. **Parallel Development**: New features in v2 while supporting v1
4. **Migration Path**: Clients can upgrade at their own pace

### Versioning Strategy
- **v1**: Stable, long-term support (minimum 12 months)
- **v2**: New features, breaking changes allowed
- **Sunset Process**: Deprecate oldest version quarterly

### Consequences
- **Positive**: Clear client expectations
- **Positive**: Easy backward compatibility
- **Negative**: Code duplication for DTOs/handlers
- **Negative**: Increased maintenance burden

---

## ADR-005: Authentication - JWT + Refresh Tokens

**Status**: APPROVED  
**Date**: 2026-07-05  
**Deciders**: Security Team

### Context
HyperMind needs stateless authentication for scalability, but also needs security best practices.

### Decision
Use **JWT (JSON Web Tokens)** with separate refresh tokens and secure HTTP-only cookies.

### Token Strategy
```
Access Token (JWT):
- Issued on login
- Expiry: 15 minutes
- Contains: user_id, tenant_id, roles, permissions
- Stored: HTTP-only, Secure, SameSite=Strict cookie
- Sent with: Authorization: Bearer <token> header

Refresh Token:
- Issued on login
- Expiry: 7 days (configurable)
- Stored: Secure HTTP-only cookie
- Single use: After refresh, new refresh token issued
- Blacklisted on logout
```

### Rationale
1. **Stateless**: No server-side session storage needed
2. **Scalability**: Works across multiple backend instances
3. **Security**: 
   - Short-lived access tokens limit damage
   - HTTP-only cookies prevent XSS token theft
   - Refresh token rotation prevents token fixation
4. **Multi-device**: Each device gets separate refresh token
5. **Compliance**: Matches OAuth 2.0 best practices

### Consequences
- **Positive**: Highly scalable
- **Positive**: Good security posture
- **Negative**: Can't invalidate access tokens until expiry
- **Negative**: Refresh token storage complexity

---

## ADR-006: Authorization - Role-Based Access Control (RBAC)

**Status**: APPROVED  
**Date**: 2026-07-05  
**Deciders**: Security Team

### Context
Need fine-grained access control for multi-tenant SaaS with complex user hierarchies.

### Decision
Implement **RBAC with three levels**:
1. Tenant level (organization)
2. Role level (admin, manager, employee, guest)
3. Resource level (specific user, company, report)

### RBAC Hierarchy
```
Tenant (Organization)
    ├── Role: Admin
    │   └── Permissions: All
    ├── Role: Manager
    │   └── Permissions: Create/Read/Update employees, view reports
    ├── Role: Employee
    │   └── Permissions: Create/Read own profile, view assigned cases
    └── Role: Guest
        └── Permissions: Read-only public information

Permission Model:
- create_user
- read_user
- update_user
- delete_user
- create_company
- manage_workflows
- access_analytics
- etc.
```

### Implementation
```
JWT token includes:
{
  "user_id": "...",
  "tenant_id": "...",
  "roles": ["manager", "employee"],
  "permissions": ["create_user", "read_user", "create_case", ...]
}

Guard decorator:
@requires_permission("create_user")
def create_user(user: User):
    # Only users with create_user permission can execute
```

### Consequences
- **Positive**: Flexible permission model
- **Positive**: Works across all modules
- **Negative**: Requires careful permission planning
- **Negative**: Tokens can get large if many permissions

---

## ADR-007: Deployment Strategy - Kubernetes

**Status**: APPROVED  
**Date**: 2026-07-05  
**Deciders**: DevOps Team

### Context
HyperMind needs enterprise-grade deployment with high availability, scalability, and easy rollback.

### Decision
Use **Kubernetes** for production deployment with:
- Multi-replica deployments for high availability
- Horizontal pod autoscaling based on CPU/memory
- Health checks for automatic recovery
- Rolling updates for zero-downtime deployments

### Architecture
```
Kubernetes Cluster:
├── Namespace: hypermind-prod
│   ├── Backend Deployment (3+ replicas)
│   ├── Frontend Deployment (2+ replicas)
│   ├── Worker Deployment (2+ replicas)
│   ├── Ingress Controller
│   └── ConfigMaps/Secrets
│
├── Namespace: hypermind-staging
│   └── [Same structure for staging]
│
└── External Services:
    ├── RDS (PostgreSQL) - managed service
    ├── ElastiCache (Redis) - managed service
    ├── Qdrant - self-hosted or managed
    └── RabbitMQ - StatefulSet
```

### Rationale
1. **High Availability**: Pod replicas, automatic failover
2. **Scalability**: Horizontal scaling based on metrics
3. **Resilience**: Health checks, liveness probes, restart policies
4. **Updates**: Rolling updates, canary deployments
5. **Multi-region**: Easy to replicate across regions

### Consequences
- **Positive**: Enterprise-grade reliability
- **Positive**: Easy horizontal scaling
- **Negative**: Kubernetes learning curve
- **Negative**: Additional operational complexity

---

## ADR-008: Database Strategy - PostgreSQL with Read Replicas

**Status**: APPROVED  
**Date**: 2026-07-05  
**Deciders**: Database Team

### Context
Single PostgreSQL instance becomes bottleneck as system scales. Need read scaling without sacrificing consistency.

### Decision
Use **PostgreSQL primary-replica architecture**:
- Primary instance: All writes
- Replica 1: Analytics queries, reporting
- Replica 2: Search indexing, Elasticsearch sync

### Architecture
```
Client Connections:
├── Write: Primary DB
│   └── Users, payments, critical operations
├── Read (application): Replicas with 1-2 second lag
│   └── User profiles, company data
└── Read (analytics): Replica 2 with configurable lag
    └── Analytics queries, report generation

Failover:
Primary failure → Replica 1 promoted automatically
```

### Rationale
1. **Read Scaling**: Replicas handle read traffic
2. **Consistency**: Writes go to primary (strong consistency)
3. **Analytics**: Separate replica doesn't impact application
4. **Backup**: Replica can be used for backups
5. **Disaster Recovery**: Quick failover with minimal data loss

### Consequences
- **Positive**: Improved read performance
- **Positive**: Analytics don't slow down app
- **Negative**: Replication lag (eventual consistency for reads)
- **Negative**: Increased infrastructure cost

---

## ADR-009: Search Strategy - PostgreSQL Full-Text Search + Elasticsearch

**Status**: APPROVED  
**Date**: 2026-07-05  
**Deciders**: Search Team

### Context
Need powerful search across:
- User profiles and companies (structured)
- Documents and conversations (unstructured)
- Audit logs (compliance search)

### Decision
**Two-tier search strategy**:
1. **PostgreSQL Full-Text Search**: Primary, built-in
   - User, company, employee searches
   - Quick migrations, no external dependency
2. **Elasticsearch (optional)**: Advanced search
   - Document search with fuzzy matching
   - Analytics and audit log search
   - Faceted search and aggregations

### Rationale
1. **PostgreSQL FTS**: Sufficient for 95% of use cases
2. **Elasticsearch**: Only when needed for complex search
3. **Separation**: Audit logs in Elasticsearch separately (compliance)
4. **Cost**: Start with PostgreSQL, scale to Elasticsearch later

### Implementation
```
Search Flow:
User search request
  ├── Simple search (name, email) → PostgreSQL FTS
  ├── Complex search (document content) → Elasticsearch
  └── Compliance search (audit logs) → Elasticsearch

Indexing:
- PostgreSQL: Automatic (tsvector columns)
- Elasticsearch: Async via event bus
```

### Consequences
- **Positive**: Flexible scaling of search
- **Positive**: Simple to start, complex to scale
- **Negative**: Two search engines to maintain
- **Negative**: Elasticsearch adds operational overhead

---

## ADR-010: Observability Strategy - OpenTelemetry

**Status**: APPROVED  
**Date**: 2026-07-05  
**Deciders**: Ops Team

### Context
Distributed system needs unified observability across logs, metrics, and traces.

### Decision
Use **OpenTelemetry** as unified instrumentation framework:
- Structured logging (JSON logs)
- Distributed tracing (end-to-end request tracking)
- Metrics collection (Prometheus-compatible)

### Three Pillars

**1. Logging**
```
All logs as JSON to stdout:
{
  "timestamp": "2026-07-05T10:30:00Z",
  "level": "info",
  "service": "backend",
  "trace_id": "abc123def456",
  "user_id": "user123",
  "tenant_id": "tenant456",
  "message": "User login successful",
  "duration_ms": 123
}
```

**2. Metrics**
```
prometheus_client.Counter: http_requests_total
prometheus_client.Histogram: http_request_duration_seconds
prometheus_client.Gauge: active_connections

Export to Prometheus, scrape every 15s
```

**3. Traces**
```
Distributed tracing via OpenTelemetry:
  POST /api/v1/users
    ├── Create user use case (50ms)
    ├── Save to database (20ms)
    ├── Publish event (10ms)
    ├── Send verification email (100ms async)
    └── Return response (5ms)
```

### Consequences
- **Positive**: Unified observability across stack
- **Positive**: Easy to debug distributed issues
- **Negative**: Requires instrumentation in all code
- **Negative**: Storage and retention costs

---

## ADR-011: Caching Strategy - Redis with TTL

**Status**: APPROVED  
**Date**: 2026-07-05  
**Deciders**: Performance Team

### Context
Database queries becoming bottleneck. Need caching without sacrificing consistency.

### Decision
Use **Redis cache** with intelligent TTL strategies and cache invalidation.

### Cache Layers
```
1. Application Cache (in-memory)
   - Fast, no network overhead
   - Limited to single instance
   - TTL: 5 minutes

2. Redis Cache (distributed)
   - Shared across all instances
   - Network overhead
   - TTL: 15 minutes (user data), 1 hour (system data)

3. Database
   - Source of truth
   - Invalidation source
```

### Cache Keys Strategy
```
user:<user_id>              # TTL 15 min
user:<user_id>:permissions # TTL 5 min
company:<company_id>       # TTL 1 hour
company:<company_id>:settings # TTL 1 hour
```

### Invalidation Strategy
```
When user is updated:
1. Update database
2. Publish UserUpdated event
3. Event handler invalidates:
   - user:<user_id>
   - user:<user_id>:permissions
```

### Consequences
- **Positive**: Massive performance improvement
- **Positive**: Reduced database load
- **Negative**: Complexity of invalidation
- **Negative**: Potential stale data (mitigated by TTL)

---

## ADR-012: Encryption Strategy - AES-256 at Rest, TLS in Transit

**Status**: APPROVED  
**Date**: 2026-07-05  
**Deciders**: Security Team

### Context
GDPR/LGPD requires encryption of personally identifiable information (PII).

### Decision
Implement **layered encryption**:
1. **In Transit**: TLS 1.3 for all connections
2. **At Rest**: AES-256 for sensitive data
3. **Key Management**: AWS KMS or vault

### Sensitive Fields (Encrypted)
```
PII:
- Emails
- Phone numbers
- Social security numbers
- Addresses
- Bank account details

Business:
- API keys
- Credentials
- Payment information
```

### Implementation
```
1. Application-level encryption:
   plaintext → AES-256 → ciphertext → PostgreSQL

2. Column encryption (built-in):
   Some PostgreSQL pgcrypto functions

3. Envelope encryption:
   - Data key: Random per record
   - Master key: AWS KMS (rotated yearly)
```

### Consequences
- **Positive**: GDPR compliance
- **Positive**: Maximum data security
- **Negative**: Performance overhead (~10%)
- **Negative**: Key management complexity

---

## Review & Approval

All ADRs have been approved by the Architecture Review Board.

**Next Steps**: 
- Share with development team
- Use as reference during implementation
- Update as new decisions are made

