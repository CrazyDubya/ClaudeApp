# API Key Management

**Category:** Fundamentals
**Difficulty:** 1/5
**Estimated Time:** 20 minutes
**Prerequisites:** [SDK Setup](../sdk-setup/)

---

## Learning Objectives

By the end of this node, you will:
- Understand secure API key handling practices
- Configure environment variables for API keys
- Avoid common security mistakes with credentials

---

## Concept Overview

Your Anthropic API key is a secret credential that grants access to Claude. Proper key management is essential for security and is a prerequisite for all Claude development.

### Key Principles

1. **Never hardcode keys** in source code
2. **Never commit keys** to version control
3. **Use environment variables** for local development
4. **Use secrets managers** for production deployments

---

## Key Patterns

### Environment Variables (Recommended)

```bash
# Set in your shell profile (~/.bashrc, ~/.zshrc, etc.)
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Python: Using Environment Variables

```python
import os
from anthropic import Anthropic

# The SDK reads ANTHROPIC_API_KEY automatically
client = Anthropic()

# Or explicitly read from environment
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set")
client = Anthropic(api_key=api_key)
```

### TypeScript: Using Environment Variables

```typescript
import Anthropic from '@anthropic-ai/sdk';

// The SDK reads ANTHROPIC_API_KEY automatically
const client = new Anthropic();

// Or explicitly read from environment
const apiKey = process.env.ANTHROPIC_API_KEY;
if (!apiKey) {
    throw new Error('ANTHROPIC_API_KEY environment variable not set');
}
const client = new Anthropic({ apiKey });
```

### Using .env Files (Development Only)

For local development, you can use `.env` files with libraries like `python-dotenv`:

```python
# .env file (add to .gitignore!)
ANTHROPIC_API_KEY=sk-ant-...
```

```python
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()  # Load variables from .env
client = Anthropic()
```

---

## Security Best Practices

### 1. Add to .gitignore

```gitignore
# API keys and secrets
.env
.env.local
*.pem
secrets/
```

### 2. Use Different Keys per Environment

- **Development**: Personal development key with lower rate limits
- **Staging**: Shared team key for testing
- **Production**: Production key managed via secrets manager

### 3. Rotate Keys Regularly

- Rotate keys periodically (e.g., quarterly)
- Rotate immediately if a key may have been exposed
- Use the Anthropic Console to manage key lifecycle

### 4. Production Secrets Management

For production, use your cloud provider's secrets manager:

- **AWS**: Secrets Manager or Parameter Store
- **GCP**: Secret Manager
- **Azure**: Key Vault
- **Kubernetes**: Secrets or external-secrets

---

## Common Pitfalls

1. **Committing keys to git**: Always check `git status` before committing
2. **Logging API keys**: Never log the full key; mask it if needed
3. **Sharing keys**: Each developer should have their own development key
4. **Hardcoding in tests**: Use mock clients or test fixtures instead

---

## Exercises

1. **Environment Setup** (`exercises/01_env_setup.py`): Configure your environment variable
2. **Key Validation** (`exercises/02_key_validation.py`): Verify your key is working
3. **Secure Loading** (`exercises/03_secure_loading.py`): Implement secure key loading with fallbacks

---

## Next Steps

After completing this node, proceed to:
- [Your First Message](../first-message/) - Send your first message to Claude
