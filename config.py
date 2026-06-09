import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

VAULT_ROOT = Path(os.environ["VAULT_ROOT"])
ACTIVE_STATUSES = {"active"}
MAX_FILE_SIZE_KB = 50