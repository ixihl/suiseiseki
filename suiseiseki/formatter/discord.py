import time
from suiseiseki.formatter.base import BaseFormatter

class DiscordFormatter(BaseFormatter):
    __name__ = "discord"
    __configuration_keys__ = {"BSKY_PROFILE_URL", "BSKY_POST_URL", "DISCORD_WEBHOOK_URL"}
    __optional_configuration_keys__ = {"INFO_USERNAME", "INFO_AVATARURL", "DISCORD_PING_ROLE", "DISCORD_PING_ON_REPOST", "DISCORD_SLEEP_TIME"}
    def should_post(self, post, reason):
        return True
    def format(self, post, reason):
        body = {
            "username": self.config.get("INFO_USERNAME", ""),
            "avatar_url": self.config.get("INFO_AVATARURL", ""),
            "content": "",
            "embeds": []
        }
        body["embeds"][0] = {
            "author": {
                "name": f"{post.get("author").get("displayName")} - @{post.get("author").get("handle")}",
                "url": self.config.get("BSKY_PROFILE_URL").format(handle=post.get("author").get("handle")),
                "icon_url": post.get("author").get("avatar", "")
            },
            "title": f"{post.get("author").get("handle")} posted.",
            "description": post.get("record").get("text", ""),
            "url": self.config.get("BSKY_POST_URL").format(handle=post.get("author").get("handle"), id=post.get("uri").split("/")[-1]),
            "timestamp": post.get("record").get("createdAt")
        }
        # Repost check
        repost = (reason and reason.get("$type") == "app.bsky.feed.defs#reasonRepost")
        if repost:
            body["embeds"][0]["title"] = f"{reason.get("by").get("handle")} reposted."
        # Image embed
        if post.get("record").get("embed", {}).get("$type", "") == "app.bsky.embed.images":
            # Assume only one, oh god
            body["embeds"][0]["image"] = {
                "url": post.get("embed").get("images")[0].get("fullsize")
            }
        # Video embed
        if post.get("record").get("embed", {}).get("$type", "") == "app.bsky.embed.video":
            body["embeds"][0]["fields"] = [{
                "name": f"{post.get("author").get("displayName")} posted a video. Click the link to view it.",
                "value": ""
            }]
            body["embeds"][0]["image"] = {
                "url": post.get("embed").get("thumbnail")
            }
        # there's records, there's embeds, and then there's records with embeds
        if post.get("record").get("embed", {}).get("$type", "") == "app.bsky.embed.recordWithMedia":
            rec_type = post.get("record").get("embed").get("media").get("$type")
            if rec_type == "app.bsky.embed.images":
                body["embeds"][0]["image"] = {
                    "url": post.get("embed").get("images")[0].get("fullsize")
                }
            if rec_type == "app.bsky.embed.video":
                body["embeds"][0]["fields"] = [{
                    "name": f"{post.get("author").get("displayName")} posted a video. Click the link to view it.",
                    "value": ""
                }]
                # XXX: Why is this different? What corner-case am I missing here exactly?
                body["embeds"][0]["image"] = {
                    "url": post.get("embed").get("media").get("thumbnail")
                }
        # To ping or not to ping
        if self.config.get("DISCORD_PING_ROLE"):
            if not repost or self.config.get("DISCORD_PING_ON_REPOST"):
                body["content"] = f"<@&{self.config.get("DISCORD_PING_ROLE")}>"
        return body
    def post(self, post, reason):
        body = self.format(post, body)
        req = self.session.post(self.config.get("DISCORD_WEBHOOK_URL"), json=info)
        req.raise_for_status()
        time.sleep(self.config.get("DISCORD_SLEEP_TIME", 0.5))
        return req.text

__formatter__ = DiscordFormatter
