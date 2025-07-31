from __future__ import annotations

"""Configuration loader for mcp_jira_server.

Loads YAML (or JSON) files containing connection details so that the JIRA MCP
server can start without explicit command-line arguments.

Priority order:
1. Explicit *--config* path passed via CLI.
2. Environment variable *MCP_JIRA_CONFIG* (path).
3. Default file ``mcp_jira_server.yaml`` in current working directory.

Supported keys (all optional except ``url``):

```
url: https://issues.example.com
username: myuser            # for password or token auth
password: mypass            # basic auth
token: myapitoken           # basic auth (with username)
bearer_token: abc123        # Personal Access Token (no username needed)
```
"""

from pathlib import Path
import os
import json
from typing import Any, Dict

import yaml  # PyYAML is already in project requirements

_CONFIG_ENV_VAR = "MCP_JIRA_CONFIG"
_DEFAULT_FILE = "mcp_jira_server.yaml"


class ConfigError(RuntimeError):
    """Raised when configuration is missing required fields."""


def _load_from_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}

    if path.suffix.lower() in {".json"}:
        return json.loads(path.read_text())

    # Fallback to YAML
    return yaml.safe_load(path.read_text()) or {}


def load_config(explicit_path: str | None = None) -> Dict[str, Any]:
    """Return configuration dictionary.

    *explicit_path* – path provided via CLI (*--config*).
    """

    if explicit_path:
        return _load_from_file(Path(explicit_path))

    env_path = os.environ.get(_CONFIG_ENV_VAR)
    if env_path:
        return _load_from_file(Path(env_path))

    return _load_from_file(Path(_DEFAULT_FILE))

# EOF
