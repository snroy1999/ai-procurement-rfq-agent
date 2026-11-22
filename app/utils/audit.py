import json
import logging
import time
from pathlib import Path

LOG_FILE = Path("audit.log")

_logger = logging.getLogger("audit")
_logger.setLevel(logging.INFO)
if not _logger.handlers:
    handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(handler)


def log_event(**fields):
    record = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), **fields}
    _logger.info(json.dumps(record, ensure_ascii=False))