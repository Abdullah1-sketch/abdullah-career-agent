# Abdullah Career Agent

Agent to improve Abdullah's chances of reaching data analyst interviews in Saudi Arabia.

Phase 1 goal: find strong entry-level data analyst opportunities, rank them, suggest the best outreach path, and notify Abdullah on Telegram without exposing secrets.

## Safety Rules

- Do not commit Telegram tokens, API keys, CV files, or personal data.
- Store all secrets in GitHub Secrets or local environment variables.
- The agent may draft outreach messages, but it must not send anything on Abdullah's behalf without approval.

## Local Environment Variables

```bash
export TELEGRAM_BOT_TOKEN="your-token"
export TELEGRAM_CHAT_ID="your-chat-id"
```

## First Test

```bash
python -m src.main --test-telegram
```

