# Suiseiseki

Suiseiseki is a self-hosted bot to post status updates from BlueSky to a Discord webhook, to allow for people to share their BlueSky statuses to discord automatically.

## Setup
This bot is intended to run inside a docker instance.
To build the container:
`docker build . -t suiseiseki-bot`
Then copy and edit both the keydb conf and logger json (if you are unsure about the settings, they can be left as is).
Copy and edit the docker-compose-example.yml file, save it as docker-compose.yml, and run `docker compose up` on it. Alternatively, you can use the .yml as the input for a stack in portainer.

## Environmental variables
Suiseiseki uses environmental variables for configuration. Here's our current list:
- `BSKY_PROFILE_DID` - The distributed ID for the account you're trying to follow (Hint: Go to their profile, add a `/rss` at the end of it, and then copy the string the handle has become in the URL). The program will explode if you don't set this.
- `BSKY_FILTER` - The filter for what bluesky posts to include. Defaults to `posts_no_replies`. Possible values: `posts_with_replies`, `posts_no_replies`, `posts_with_media`, `posts_and_author_threads`.
- `BSKY_UPDATE_TIME` - The time, in seconds, between each refresh of the BlueSky feed. Default is 300 seconds, or 5 minutes.
- `WEBHOOK_URL` - The Discord webhook URL that the program will post to. The program will explode if you don't set this. Note: This doesn't have to be a Discord webhook, but the formatting is currently setup so that it utilizes Discord rich embeds, and may not behave with other services.
- `INFO_USERNAME` - The display name to go post the updates under. Defaults to "Suiseiseki". Setting this to a blank string will use the name given by the webhook.
- `INFO_AVATARURL` - The URL of the image that will be the bot's avatar. Defaults to nothing. Setting this to a blank string will use the image given by the webhook.
- `LOGGING_CONFIG` - ***⚠ HIGHLY IMPORTANT ⚠*** The location on disk where the logging configuration is stored. This is a [dictConfig](https://docs.python.org/3/library/logging.config.html#logging-config-dictschema) to configure python's logging.
- `KEYDB_HOST` - The KeyDB hostname, generally either `localhost` or `keydb`, if hosting it locally or using docker respectively.
- `KEYDB_PORT` - The KeyDB port number, set to a non-standard number by default (7089) because it didn't conflict with Windows' default port blocking.
- `KEYDB_PASSWD` - The KeyDB password, by default null. Probably don't need this if you're containerized.
- `KEYDB_EXPIRE_TIME` - Each ID that KeyDB stores is set to expire after this amount of time in seconds. The default is 4838400 seconds, or approximately 2 months.
- `DISCORD_PING_ROLE` - The Discord Role ID that'll be pinged in the message. Can be found by setting discord into Developer mode, right clicking on a user's role, and selecting "Copy Role ID".
- `DISCORD_PING_ON_REPOST` - Ping the discord role on reposts. `true` if you want it on, `false` or nothing if you want it off.

## Notes
- Currently the bot is *only* made to post update from *one* account's bluesky page to *one* webhook that takes *discords* rich embed formatting only. Maybe that'll change in the future, maybe not.
- When you first run the bot, it will attempt to post every single entry it can. Eventually I'll update it to instead grab all IDs and then post *whats posted after*.
