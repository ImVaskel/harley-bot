# Harley Bot

## Info
See [run](run) on how to run the bot.
## Run

To run the bot, cp `config-template.json` to `config.json`, and fill it out. Then make a `.env` file with the variable `pg_password` set to the same inside your config.

Replace the emojis in `emojis.json`, these emojis are roughly the same as the discord defaults for pagination.

```json
{
    "arrow_left" :  "⬅️",
    "arrow_right" : "➡️",
    "stop" : "⏹️",
    "double_backward" : "⏪",
    "double_forward" : "⏩",
    "information" : "ℹ️",
    "x-mark" : "❎",
    "checkmark" : "✅"
}
```

Then run `docker compose up`.
Alternatively, you can install poetry and just run `poetry install`, then `poetry run python main.py` if you do 
not want to use docker.

# **NOTE**
This bot is unfinished, and chances are it'll stay that way. Open a PR if you want anything finished and I'll look at it.

## **Licensing**
The bot is under an AGPL-3 license. So please follow that.