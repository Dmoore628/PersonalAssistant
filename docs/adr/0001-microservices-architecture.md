# ADR-0001: Microservices Architecture for AI Agents

## Status
**Accepted**

**Date:** 2025-01-15
**Deciders:** System Architecture Team
**Technical Story:** Implementation of multi-agent AI system for Archi Digital Twin

## Context
The Archi AI Digital Twin system requires a sophisticated multi-agent architecture capable of:
- Running six specialized AI agents independently
- Enabling inter-agent communication and orchestration
- Supporting independent scaling and deployment
- Maintaining fault tolerance and resilience
- Allowing for incremental development and testing

We needed to choose between:
1. Monolithic architecture with all agents in single process
2. Microservices architecture with independent agent services
3. Hybrid approach with some agents grouped together

## Decision
We chose a **microservices architecture** where each of the six AI agents runs as an independent service:
- Planning Agent (port 8011)
- Execution Agent (port 8012) 
- Memory Agent (port 8013)
- Security Agent (port 8014)
- Tool Creation Agent (port 8015)
- Learning Agent (port 8016)

Each service:
- Exposes REST APIs via FastAPI
- Communicates via RabbitMQ message bus
- Shares common schemas via `archi_core` library
- Runs in Docker containers for isolation
- Has independent health monitoring and logging

## Consequences

### Positive
- **Independent Scaling:** Each agent can be scaled based on its specific load patterns
- **Fault Isolation:** Failure of one agent doesn't bring down the entire system
- **Development Velocity:** Teams can work on different agents independently
- **Technology Flexibility:** Each agent can use optimal libraries and approaches
- **Deployment Flexibility:** Agents can be deployed to different environments
- **Testing Isolation:** Agents can be tested independently and in integration

### Negative
- **Increased Complexity:** More moving parts to monitor and manage
- **Network Latency:** Inter-service communication adds latency overhead
- **Data Consistency:** Requires careful design for cross-agent data consistency
- **Operational Overhead:** More services to deploy, monitor, and maintain
- **Development Complexity:** Requires distributed systems expertise

### Neutral
- **Message Queue Dependency:** All agents depend on RabbitMQ for communication
- **Shared Library:** Common schemas managed in `archi_core` library
- **Container Runtime:** All services run in Docker for consistency

## Implementation
- FastAPI framework for REST APIs and automatic OpenAPI documentation
- RabbitMQ for asynchronous message passing between agents
- Docker Compose for local development orchestration
- Shared `archi_core` library for common schemas and utilities
- Consistent health check endpoints across all services
- Structured logging with correlation IDs for distributed tracing

## Compliance
- **REQ-ARCH-001:** Microservices architecture with secure message queues ✅
- **REQ-ARCH-002:** Asynchronous agents with event-driven communication ✅
- **REQ-ARCH-003:** Separation of concerns between UI, business logic, and data ✅
- **REQ-AGENT-002:** Async message passing with guaranteed delivery ✅
- **REQ-AGENT-003:** Health monitoring and automatic restart capabilities ✅

## Links
- [Technical Requirements Document](../../archi-technicalrequirement.md#2-system-architecture)
- [Docker Compose Configuration](../../infra/docker-compose.yml)
- [Agent Implementation PRs](https://github.com/Dmoore628/PersonalAssistant/pulls)