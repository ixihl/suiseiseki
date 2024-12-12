import logging
import importlib
import pkgutil

def load_formatters():
    # Default formatters
    names = [name for _, name, _ in pkgutil.iter_modules(['suiseiseki/formatter'])]
    formatters = {}
    for name in names:
        formatter = importlib.import_module(f'suiseiseki.formatter.{name}')
        if formatter.__dict__.get("__formatter__"):
            formatters[name] = formatter.__formatter__
    logging.info(f"[formatter] Loaded {len(formatters)} formatter{"s" if formatters else ""}: {", ".join(formatters.keys())}.")
    return formatters
