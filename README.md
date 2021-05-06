# impfalert

Small script that parses available vaccination slots in Berlin vaccination centers (via doctolib.de API).
Alerts can be configured to be sent via Telegram bot or via Slack webhooks.

## How to use

1. [Create a Telegram bot](https://core.telegram.org/bots#3-how-do-i-create-a-bot) or [add a Slack webhook](https://api.slack.com/tutorials/slack-apps-hello-world).
2. Set up environment variables (depending on the preferred alert type):

```
export TELEGRAM_BOT_TOKEN=
export TELEGRAM_BOT_CHAT_ID=
export SLACK_WEBHOOK_URL=
```

3. Run `python main.py` somewhere. No external packages required, plain Python 3 code.
4. (optional) You can add `HEALTHCHECK_TOKEN` (https://healthchecks.io/) to ensure that your script is up and running.
