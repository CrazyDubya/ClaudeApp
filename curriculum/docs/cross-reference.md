# Curriculum Cross-Reference

This document provides a comprehensive cross-reference between curriculum nodes, showing how concepts connect and build upon each other.

---

## Quick Navigation

| Category | Nodes |
|----------|-------|
| [Fundamentals](#fundamentals) | sdk-setup, api-keys, first-message, model-selection |
| [Messaging](#messaging) | message-structure, system-prompts, streaming, multi-turn, context-management, vision |
| [Tools](#tools) | tool-basics, tool-schemas, tool-execution, multi-tool, tool-error-handling |
| [Agents](#agents) | agent-loop, agent-state, agent-planning, multi-agent |
| [Advanced](#advanced) | error-handling, rate-limiting, caching, monitoring, security, testing |

---

## Fundamentals

### sdk-setup
**Path:** `nodes/fundamentals/sdk-setup/`

| Aspect | Details |
|--------|---------|
| Prerequisites | None |
| Leads to | api-keys |
| Related concepts | Installation, environment setup |
| Used in blueprints | All blueprints |

**Key concepts introduced:**
- SDK installation (pip/npm)
- Client initialization
- Version checking

---

### api-keys
**Path:** `nodes/fundamentals/api-keys/`

| Aspect | Details |
|--------|---------|
| Prerequisites | sdk-setup |
| Leads to | first-message |
| Related concepts | Security, environment variables |
| Used in blueprints | All blueprints |

**Key concepts introduced:**
- Environment variable management
- Key security best practices
- .env file usage

**Cross-references:**
- See also: [security](#security) for production key management
- See also: [monitoring](#monitoring) for key usage tracking

---

### first-message
**Path:** `nodes/fundamentals/first-message/`

| Aspect | Details |
|--------|---------|
| Prerequisites | api-keys |
| Leads to | model-selection, message-structure |
| Related concepts | API basics, response handling |
| Used in blueprints | All blueprints |

**Key concepts introduced:**
- messages.create() API
- Response object structure
- Token usage

**Cross-references:**
- Builds on: api-keys (client creation)
- Extends to: streaming (async responses)
- Extends to: multi-turn (conversation context)

---

### model-selection
**Path:** `nodes/fundamentals/model-selection/`

| Aspect | Details |
|--------|---------|
| Prerequisites | first-message |
| Leads to | message-structure (or any messaging node) |
| Related concepts | Cost optimization, performance |
| Used in blueprints | All blueprints |

**Key concepts introduced:**
- Model tiers (Haiku, Sonnet, Opus)
- Model routing
- Cost-performance tradeoffs

**Cross-references:**
- See also: [caching](#caching) for cost optimization
- See also: [rate-limiting](#rate-limiting) for usage management

---

## Messaging

### message-structure
**Path:** `nodes/messaging/message-structure/`

| Aspect | Details |
|--------|---------|
| Prerequisites | first-message |
| Leads to | system-prompts, streaming, multi-turn, vision |
| Related concepts | Content blocks, roles |
| Used in blueprints | All blueprints |

**Key concepts introduced:**
- Message roles (user, assistant)
- Content block types
- Response structure parsing

**Cross-references:**
- Builds on: first-message (basic requests)
- Required for: tool-basics (tool_use blocks)
- Required for: vision (image blocks)

---

### system-prompts
**Path:** `nodes/messaging/system-prompts/`

| Aspect | Details |
|--------|---------|
| Prerequisites | message-structure |
| Leads to | multi-turn, context-management |
| Related concepts | Prompt engineering, behavior control |
| Used in blueprints | conversational-assistant, document-processor |

**Key concepts introduced:**
- System prompt structure
- Role definition
- Behavior constraints

**Cross-references:**
- Builds on: message-structure (message formatting)
- See also: [security](#security) for prompt injection defense
- Used heavily in: agent-planning (agent instructions)

---

### streaming
**Path:** `nodes/messaging/streaming/`

| Aspect | Details |
|--------|---------|
| Prerequisites | message-structure |
| Leads to | error-handling (for stream errors) |
| Related concepts | Real-time output, UX |
| Used in blueprints | conversational-assistant |

**Key concepts introduced:**
- Stream context manager
- Text chunk processing
- Time-to-first-token

**Cross-references:**
- Builds on: message-structure (response handling)
- See also: [error-handling](#error-handling) for stream recovery
- See also: [monitoring](#monitoring) for latency tracking

---

### multi-turn
**Path:** `nodes/messaging/multi-turn/`

| Aspect | Details |
|--------|---------|
| Prerequisites | message-structure |
| Leads to | context-management, agent-loop |
| Related concepts | Conversation state, memory |
| Used in blueprints | conversational-assistant |

**Key concepts introduced:**
- Conversation history management
- State persistence
- Session handling

**Cross-references:**
- Builds on: message-structure (message arrays)
- Extends to: context-management (token limits)
- Required for: agent-loop (iterative processing)

---

### context-management
**Path:** `nodes/messaging/context-management/`

| Aspect | Details |
|--------|---------|
| Prerequisites | multi-turn |
| Leads to | caching, agent-state |
| Related concepts | Token optimization, document processing |
| Used in blueprints | document-processor |

**Key concepts introduced:**
- Token counting and estimation
- History trimming strategies
- Document chunking
- Summarization

**Cross-references:**
- Builds on: multi-turn (conversation history)
- Extends to: caching (prompt caching)
- See also: model-selection (context window sizes)

---

### vision
**Path:** `nodes/messaging/vision/`

| Aspect | Details |
|--------|---------|
| Prerequisites | message-structure |
| Leads to | document-processor blueprint |
| Related concepts | Image analysis, multimodal |
| Used in blueprints | document-processor |

**Key concepts introduced:**
- Base64 image encoding
- Image content blocks
- Visual analysis prompts

**Cross-references:**
- Builds on: message-structure (content blocks)
- Used in: document-processor (document images)
- See also: [testing](#testing) for image test fixtures

---

## Concept Index

### By Topic

| Topic | Relevant Nodes |
|-------|---------------|
| Getting Started | sdk-setup → api-keys → first-message |
| Conversations | message-structure → multi-turn → context-management |
| Performance | model-selection, streaming, caching |
| Security | api-keys, security |
| Production | error-handling, rate-limiting, monitoring |
| Agents | multi-turn → agent-loop → agent-state → agent-planning |

### By Blueprint

| Blueprint | Required Nodes | Recommended Nodes |
|-----------|---------------|-------------------|
| conversational-assistant | first-message, streaming, multi-turn, system-prompts | context-management, error-handling |
| document-processor | first-message, system-prompts, tool-basics, tool-execution | vision, streaming, context-management |

---

## Learning Paths

### Path 1: Quick Start (30 minutes)
1. sdk-setup (15 min)
2. api-keys (10 min)
3. first-message (15 min)

### Path 2: Chatbot Developer (2 hours)
1. Quick Start path
2. message-structure (25 min)
3. system-prompts (45 min)
4. streaming (30 min)
5. multi-turn (40 min)

### Path 3: Document Processing (2.5 hours)
1. Quick Start path
2. message-structure (25 min)
3. system-prompts (45 min)
4. vision (35 min)
5. context-management (60 min)

### Path 4: Agent Developer (4+ hours)
1. Chatbot Developer path
2. context-management (60 min)
3. tool-basics (45 min)
4. tool-execution (50 min)
5. agent-loop (90 min)
6. agent-state (60 min)

---

## Version Compatibility

| Node | Min SDK Version | Tested SDK Version |
|------|-----------------|-------------------|
| All fundamentals | 0.18.0 | 0.40.0+ |
| All messaging | 0.18.0 | 0.40.0+ |
| vision | 0.20.0 | 0.40.0+ |
| streaming | 0.18.0 | 0.40.0+ |

---

*Last updated: December 2025*
