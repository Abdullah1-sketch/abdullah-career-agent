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
export SERPAPI_KEY="your-serpapi-key"   # Google job search
```

In GitHub Actions these come from repository Secrets with the same names.

## Run

```bash
pip install -r requirements.txt

# Send today's job report to Telegram (same as the daily GitHub Action)
python main.py --test-telegram

# Compare the bot's scores with the replies you actually got
python main.py --review-applications applications.csv
```

`applications.csv` is ignored by git (personal data). Copy
`applications.example.csv` to start. Leave `bot_score` empty to let the bot
score the row; `status` accepts English or Arabic values
(تم التقديم / لا رد / رفض / اتصال / مقابلة).

## Tests

```bash
python -m unittest discover -s tests
```

`tests/test_scoring.py` holds realistic Saudi job postings with the expected
apply/skip verdict. Add a posting there whenever the bot gets one wrong.

## Tuning

All scoring lists and weights are in the "Job scoring settings" section of
`config.py`: titles, skills, entry-level and seniority words, locations, score
weights, thresholds, jobs per message, and `SEARCHES_PER_RUN` (paid searches
per day).
