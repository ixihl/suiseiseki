import requests
from urllib.parse import urlencode
import os
import time
import json
import logging
import logging.config
from keydb import KeyDB

PROFILE = os.environ.get('BSKY_PROFILE_DID') or ""
BSKY_PROFILE_URL =  "https://bsky.app/profile/{handle}"
BSKY_POST_URL = "https://bsky.app/profile/{handle}/post/{id}"
BSKY_APP_URL = "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed"
BSKY_FILTER = os.environ.get('BSKY_FILTER') or "posts_no_replies"
BSKY_UPDATE_TIME = int(os.environ.get('BSKY_UPDATE_TIME', 5*60))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL') or ""
DISCORD_SLEEP_TIME = 0.3
KEYDB_HOST = os.environ.get('KEYDB_HOST') or "localhost"
KEYDB_PORT = int(os.environ.get('KEYDB_PORT', 6379))
KEYDB_PASSWD = os.environ.get('KEYDB_PASSWD') or None
KEYDB_EXPIRE_TIME = int(os.environ.get('KEYDB_EXPIRE_TIME', 60*60*24*7*4*2)) # aprox 2 months of seconds
INFO_USERNAME = os.environ.get('INFO_USERNAME') or "Suiseiseki"
INFO_AVATARURL = os.environ.get('INFO_AVATARURL') or ''
LOGGING_CONFIG = os.environ.get('LOGGING_CONFIG') or ''

if LOGGING_CONFIG == "":
    raise ValueError("LOGGING_CONFIG must be set")

if PROFILE == "":
    raise ValueError("BSKY_PROFILE_DID must be set")

if WEBHOOK_URL == "":
    raise ValueError("WEBHOOK_URL must be set")

with open(LOGGING_CONFIG, "r") as f:
    config = json.load(f)

logger = logging.getLogger("suiseiseki")
logging.config.dictConfig(config)

s = requests.Session()
s.headers.update({
    'User-Agent':'Ixihl\'s Discord Bot (v0.0.1) <ixihl@hime.watch>'
})

# Suiseiseki's info
DEFAULT_INFO = {
    "username": INFO_USERNAME,
    "avatar_url": INFO_AVATARURL,
    "content": ""
}

def get_feed():
    qs = urlencode({
        "actor": PROFILE,
        "filter": BSKY_FILTER
    })
    req = s.get("{APP_URL}?{qs}".format(APP_URL=BSKY_APP_URL, qs=qs))
    try:
        req.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logging.error("Error querying BlueSky API", e)
        return [] # XXX: Fail silently here, maybe not a good idea?
    feed = req.json().get("feed")
    return feed

def embed_post(p):
    info = DEFAULT_INFO.copy()
    # please don't look too hard at my shame
    info["embeds"] = [{
        "author": {
            "name": "{name} - @{handle}".format(name=p.get("author").get("displayName"),handle=p.get("author").get("handle")),
            "url": BSKY_PROFILE_URL.format(handle=p.get("author").get("handle")),
            "icon_url": p.get("author").get("avatar"),
        },
        "title": "{handle} posted.".format(handle=p.get("author").get("handle")),
        "description": p.get("record").get("text", ""),
        "url": BSKY_POST_URL.format(handle=p.get("author").get("handle"), id=p.get("uri").split("/")[-1]),
        "timestamp": p.get("record").get("createdAt")
    }]
    if p.get("record").get("embed", {}).get("$type", "") == "app.bsky.embed.video":
        info["embeds"][0]["fields"] = [{
            "name": "{name} posted a video. Click the link to view it.".format(name=p.get("author").get("displayName")),
            "value": ""
        }]
        info["embeds"][0]["image"] = {
            "url": p.get("embed").get("thumbnail")
        }
    if p.get("record").get("embed", {}).get("$type", "") == "app.bsky.embed.images":
        # Assume only one, oh god
        info["embeds"][0]["image"] = {
            "url": p.get("embed").get("images")[0].get("fullsize")
        }
    req = s.post(WEBHOOK_URL, json=info)
    try:
        req.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logging.error("Error posting to discord", e)

if __name__ == '__main__':
    logging.info("Suiseiseki starting")
    logging.info("KeyDB init")
    db = KeyDB(host=KEYDB_HOST, port=KEYDB_PORT)
    posts = set()
    if db.smembers("posted_ids"):
        posts.update(db.smembers("posted_ids"))
    while True:
        feed = get_feed()
        ids = set(map(lambda x: x.get("post").get("cid").encode("utf8"), feed))
        feed_object = {x.get("post").get("cid").encode("utf8"): x.get("post") for x in feed}
        unposted = posts.symmetric_difference(ids)
        # making a reasonable assumption that the id only increments
        # this doesn't affect much but i want the bot 
        # to post in as chronological an order as possible
        # XXX: Make this do as much of the posting in one go as possible
        # this is limited to batches of 10 iirc
        for p in sorted(unposted):
            logging.info("Posting post with cid {}".format(p))
            embed_post(feed_object[p])
            db.sadd("posted_ids", p)
            db.expiremember("posted_ids", p, KEYDB_EXPIRE_TIME)
            time.sleep(DISCORD_SLEEP_TIME)
        posts.update(db.smembers("posted_ids"))
        time.sleep(BSKY_UPDATE_TIME)
