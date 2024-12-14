import logging
import importlib
import pkgutil

logger = logging.getLogger("suiseiseki")

def load_formatters():
    # Default formatters
    names = [name for _, name, _ in pkgutil.iter_modules(['suiseiseki/formatter'])]
    formatters = {}
    for name in names:
        formatter = importlib.import_module(f'suiseiseki.formatter.{name}')
        if formatter.__dict__.get("__formatter__"):
            formatters[name] = formatter.__formatter__
    logger.info(f"[formatter] Loaded {len(formatters)} formatter{"" if len(formatters) == 1 else "s"}: {", ".join(formatters.keys())}.")
    return formatters
