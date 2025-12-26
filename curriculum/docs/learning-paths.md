# Learning Paths

Recommended paths through the curriculum based on your goals.

---

## Path Overview

```
                    ┌─────────────────┐
                    │   sdk-setup     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    api-keys     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  first-message  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼────┐  ┌──────▼──────┐  ┌────▼────────┐
     │model-select │  │msg-structure│  │  streaming  │
     └─────────────┘  └──────┬──────┘  └─────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
   ┌─────▼─────┐     ┌───────▼───────┐     ┌─────▼─────┐
   │sys-prompts│     │  multi-turn   │     │   vision  │
   └───────────┘     └───────┬───────┘     └───────────┘
                             │
                    ┌────────▼────────┐
                    │context-managemt │
                    └────────┬────────┘
                             │
                       ┌─────▼─────┐
                       │tool-basics│
                       └───────────┘
```

---

## Quick Start Path
**Time:** 30-45 minutes | **Goal:** Send your first message

Perfect for getting started immediately.

### Nodes
1. **sdk-setup** (15 min) - Install the SDK
2. **api-keys** (10 min) - Configure your API key
3. **first-message** (15 min) - Send your first message

### Outcome
You'll be able to send messages to Claude and receive responses.

### Next Steps
- Add **model-selection** to optimize for your use case
- Add **streaming** for real-time responses

---

## Chatbot Developer Path
**Time:** 2-3 hours | **Goal:** Build conversational applications

For developers building chatbots, assistants, or conversational interfaces.

### Nodes
1. Complete **Quick Start Path** (30 min)
2. **message-structure** (25 min) - Understand message formats
3. **system-prompts** (45 min) - Design bot personality
4. **streaming** (30 min) - Real-time responses
5. **multi-turn** (40 min) - Maintain conversation context

### Outcome
You'll be able to build a fully functional chatbot with:
- Custom personality via system prompts
- Real-time streaming responses
- Conversation memory across turns

### Ready for Blueprint
After completing this path, you're ready for the **Conversational Assistant** blueprint.

---

## Document Processor Path
**Time:** 2.5-3 hours | **Goal:** Analyze and process documents

For developers building document analysis, extraction, or transformation tools.

### Nodes
1. Complete **Quick Start Path** (30 min)
2. **message-structure** (25 min) - Understand content blocks
3. **system-prompts** (45 min) - Design analysis prompts
4. **vision** (35 min) - Process document images
5. **context-management** (60 min) - Handle large documents

### Outcome
You'll be able to:
- Analyze text and image documents
- Extract structured information
- Process documents larger than the context window

### Ready for Blueprint
After completing this path, you're ready for the **Document Processor** blueprint.

---

## Production Developer Path
**Time:** 4-5 hours | **Goal:** Build production-ready applications

For developers preparing applications for production deployment.

### Nodes
1. Complete **Chatbot Developer Path** (2 hours)
2. **model-selection** (30 min) - Optimize costs
3. **context-management** (60 min) - Handle token limits
4. **error-handling** (60 min) - Handle failures gracefully
5. **rate-limiting** (45 min) - Handle API limits
6. **monitoring** (60 min) - Add observability

### Outcome
You'll understand:
- Cost optimization strategies
- Error recovery patterns
- Rate limit handling
- Logging and monitoring

---

## Agent Developer Path
**Time:** 6-8 hours | **Goal:** Build autonomous agents

For developers building AI agents that can act autonomously.

### Nodes
1. Complete **Chatbot Developer Path** (2 hours)
2. **context-management** (60 min) - Long-running context
3. **tool-basics** (45 min) - Define tools
4. **tool-schemas** (40 min) - Design tool interfaces
5. **tool-execution** (50 min) - Execute tools safely
6. **multi-tool** (60 min) - Orchestrate multiple tools
7. **agent-loop** (90 min) - Build agent loops
8. **agent-state** (60 min) - Manage agent state

### Outcome
You'll be able to build agents that:
- Use tools to interact with external systems
- Loop until tasks are complete
- Maintain state across iterations
- Handle complex multi-step tasks

---

## Path Recommendations by Role

| Role | Recommended Path |
|------|------------------|
| Frontend Developer | Chatbot Developer |
| Backend Developer | Production Developer |
| ML Engineer | Agent Developer |
| Product Manager | Quick Start |
| DevOps Engineer | Production Developer |
| Data Scientist | Document Processor |

---

## Skill Level Progression

### Beginner (Difficulty 1-2)
- All Fundamentals nodes
- message-structure
- streaming
- vision

### Intermediate (Difficulty 3)
- system-prompts
- multi-turn
- tool-basics
- testing

### Advanced (Difficulty 4-5)
- context-management
- agent-loop
- agent-state
- agent-planning
- multi-agent

---

*See [cross-reference.md](./cross-reference.md) for detailed node relationships.*
