import requests
from urllib.parse import urlencode
import os
import time
import json
import logging
import logging.config
from keydb import KeyDB
import suiseiseki.formatter

BSKY_PROFILE_DID = os.environ.get('BSKY_PROFILE_DID') or ""
BSKY_APP_URL = "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed"
BSKY_FILTER = os.environ.get('BSKY_FILTER') or "posts_no_replies"
BSKY_UPDATE_TIME = int(os.environ.get('BSKY_UPDATE_TIME', 5*60))

KEYDB_HOST = os.environ.get('KEYDB_HOST') or "localhost"
KEYDB_PORT = int(os.environ.get('KEYDB_PORT', 6379))
KEYDB_PASSWD = os.environ.get('KEYDB_PASSWD') or None
KEYDB_EXPIRE_TIME = int(os.environ.get('KEYDB_EXPIRE_TIME', 60*60*24*7*4*2)) # aprox 2 months of seconds

LOGGING_CONFIG = os.environ.get('LOGGING_CONFIG') or ''
CONFIG_FILE = os.environ.get('CONFIG_FILE') or ''

if LOGGING_CONFIG == "":
    raise ValueError("LOGGING_CONFIG must be set.")

with open(LOGGING_CONFIG, "r") as f:
    logging_config = json.load(f)

logger = logging.getLogger("suiseiseki")
logging.config.dictConfig(logging_config)

if CONFIG_FILE == "":
    raise ValueError("CONFIG_FILE must be set.")

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

s = requests.Session()
s.headers.update({
    'User-Agent': config.get("useragent", 'Ixihl\'s Discord Bot (v0.0.2) <ixihl@hime.watch>')
})

formatters = {}
for name, cls in suiseiseki.formatter.load_formatters().items():
    formatters[name] = cls(s)

def get_feed():
    qs = urlencode({
        "actor": BSKY_PROFILE_DID,
        "filter": BSKY_FILTER
    })
    req = s.get(f"{BSKY_APP_URL}?{qs}")
    try:
        req.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error("Error querying BlueSky API", e)
        return [] # XXX: Fail silently here, maybe not a good idea?
    feed = req.json().get("feed")
    return feed

def embed_post(p):
    ...

if __name__ == '__main__':
    logger.info("Suiseiseki starting")
    logger.info("KeyDB init")
    db = KeyDB(host=KEYDB_HOST, port=KEYDB_PORT)
    posts = set()
    if db.smembers("posted_ids"):
        posts.update(db.smembers("posted_ids"))
    while True:
        feed = get_feed()
        ids = set(map(lambda x: x.get("post").get("cid").encode("utf8"), feed))
        feed_object = {x.get("post").get("cid").encode("utf8"): (x.get("post"), x.get("reason")) for x in feed}
        unposted = posts.symmetric_difference(ids)
        # making a reasonable assumption that the id only increments
        # this doesn't affect much but i want the bot
        # to post in as chronological an order as possible
        # XXX: Make this do as much of the posting in one go as possible
        # this is limited to batches of 10 iirc
        for p in sorted(unposted):
            logger.info(f"Posting post with cid `{p.decode()}`")
            for name, formatter in formatters.items():
                post, reason = feed_object[p]
                if formatter.should_post(post, reason):
                    try:
                        formatter.post(post, reason)
                    except requests.exceptions.RequestException as e:
                        logger.error(f"[formatter][{name}] Error when posting", e)
                        continue
            db.sadd("posted_ids", p)
            db.expiremember("posted_ids", p, KEYDB_EXPIRE_TIME)
        posts.update(db.smembers("posted_ids"))
        time.sleep(BSKY_UPDATE_TIME)
