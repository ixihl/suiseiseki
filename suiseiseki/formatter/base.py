import os
import logging
import importlib
import requests

logger = logging.getLogger("suiseiseki")

class BaseFormatter(object):
    __name__ = "base_formatter"
    __configuration_keys__ = set()
    __optional_configuration_keys__ = set()
    def __init__(self, session, *args, **kwargs):
        if not session:
            session = requests.Session()
            session.headers.update({
                'User-Agent':'Ixihl\'s Discord Bot (v0.0.2) <ixihl@hime.watch>'
            })
        self.session = session
        self.config = self.get_config()
    def get_config(self):
        config = {}
        errors = set()
        for key in self.__configuration_keys__:
            try:
                config[key] = os.environ[key]
            except KeyError as e:
                errors.update({key})
        if len(errors) != 0:
            raise KeyError(f"[{self.__name__}][config] Couldn't obtain {len(errors)} keys: {", ".join(errors)}.")
        for key in self.__optional_configuration_keys__:
            config[key] = os.environ.get(key, None)
        logger.info(f"[{self.__name__}][config] got {len(config)} configuration options.")
        return config
    def should_post(self, post, reason):
        return NotImplemented
    def format(self, post, reason):
        return NotImplemented
    def post(self, post, reason):
        return NotImplemented
