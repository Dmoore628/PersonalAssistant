# ADR 0001: Choose RabbitMQ for intra-agent messaging

Date: 2025-09-27

## Status
Accepted

## Context
We need reliable message delivery between agents (planning, execution, memory, etc.) with at-least-once semantics and simple work queue semantics.

## Decision
Use RabbitMQ (classic queues) for command/event patterns. Use durable queues, persistent messages, and prefetch=1.

## Consequences
- Pros: Mature, easy to operate locally (management UI), great for work queues.
- Cons: Not a log; replay/history requires additional storage. For analytics, we’ll rely on Neo4j and optional Elasticsearch later.
