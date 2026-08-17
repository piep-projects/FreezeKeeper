#!/usr/bin/env python3
"""Deploy the FreezeKeeper custom integration to a Home Assistant test instance.

SFTPs ``custom_components/freezekeeper/`` to the HA config dir and restarts HA core.
Used for the ha-test1 dev loop (panel/card cache-bust on each manifest version bump).

Credentials are **never** committed. They are read, in order of precedence, from:
  1. environment variables (HA_DEPLOY_HOST / _PORT / _USER / _PASSWORD / _REMOTE)
  2. a git-ignored ``scripts/deploy.local.env`` (simple ``KEY=VALUE`` lines)
  3. the defaults below (LAN-local host/user; password has no default)

Copy ``scripts/deploy.local.env.example`` → ``scripts/deploy.local.env`` and set
``HA_DEPLOY_PASSWORD`` (and override host etc. if your instance differs).

Usage:
  python3 scripts/deploy.py                # sync + restart HA core
  python3 scripts/deploy.py --no-restart   # sync only
  python3 scripts/deploy.py --no-check     # skip `ha core check`

Requires ``paramiko`` (``pip install paramiko``).
"""
from __future__ import annotations

import argparse
import os
import posixpath
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCAL_DEFAULT = REPO_ROOT / "custom_components" / "freezekeeper"

DEFAULTS = {
    "HA_DEPLOY_HOST": "192.168.178.98",
    "HA_DEPLOY_PORT": "22",
    "HA_DEPLOY_USER": "root",
    "HA_DEPLOY_PASSWORD": "",  # no default — must be provided
    "HA_DEPLOY_REMOTE": "/config/custom_components/freezekeeper",
}


def _load_local_env() -> dict[str, str]:
    """Read ``scripts/deploy.local.env`` (KEY=VALUE, ``#`` comments) if present."""
    path = Path(__file__).resolve().parent / "deploy.local.env"
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def _cfg(key: str, file_env: dict[str, str]) -> str:
    return os.environ.get(key) or file_env.get(key) or DEFAULTS[key]


def main() -> int:
    ap = argparse.ArgumentParser(description="Deploy FreezeKeeper to the HA test instance.")
    ap.add_argument("--no-restart", action="store_true", help="sync files only, don't restart HA")
    ap.add_argument("--no-check", action="store_true", help="skip `ha core check` before restart")
    ap.add_argument("--local", default=str(LOCAL_DEFAULT), help="local integration dir to upload")
    args = ap.parse_args()

    try:
        import paramiko
    except ImportError:
        print("error: paramiko not installed — `pip install paramiko`", file=sys.stderr)
        return 2

    file_env = _load_local_env()
    host = _cfg("HA_DEPLOY_HOST", file_env)
    port = int(_cfg("HA_DEPLOY_PORT", file_env))
    user = _cfg("HA_DEPLOY_USER", file_env)
    pwd = _cfg("HA_DEPLOY_PASSWORD", file_env)
    remote = _cfg("HA_DEPLOY_REMOTE", file_env)
    local = Path(args.local).resolve()

    if not pwd:
        print(
            "error: no password — set HA_DEPLOY_PASSWORD or scripts/deploy.local.env "
            "(see scripts/deploy.local.env.example)",
            file=sys.stderr,
        )
        return 2
    if not local.is_dir():
        print(f"error: local dir not found: {local}", file=sys.stderr)
        return 2

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting {user}@{host}:{port} …")
    ssh.connect(host, port=port, username=user, password=pwd, timeout=15)
    sftp = ssh.open_sftp()

    def mkdirs(path: str) -> None:
        cur = ""
        for part in path.strip("/").split("/"):
            cur += "/" + part
            try:
                sftp.stat(cur)
            except FileNotFoundError:
                sftp.mkdir(cur)

    count = 0
    for root, _dirs, files in os.walk(local):
        if "__pycache__" in root:
            continue
        rel = os.path.relpath(root, local)
        rdir = remote if rel == "." else posixpath.join(remote, rel.replace(os.sep, "/"))
        mkdirs(rdir)
        for fname in files:
            # skip build cruft / macOS AppleDouble sidecars (samba mount leaves these)
            if fname.endswith(".pyc") or fname.startswith("._") or fname == ".DS_Store":
                continue
            sftp.put(os.path.join(root, fname), posixpath.join(rdir, fname))
            count += 1
            print(f"  → {posixpath.join(rdir, fname)}")
    sftp.close()
    print(f"Uploaded {count} files to {remote}.")

    rc = 0
    if not args.no_check:
        print("ha core check …")
        _i, out, _e = ssh.exec_command("ha core check 2>&1")
        print(out.read().decode().strip()[-500:])

    if args.no_restart:
        print("Skipping restart (--no-restart).")
    else:
        print("Restarting HA core (~60s) …")
        _i, out, _e = ssh.exec_command("ha core restart 2>&1")
        rc = out.channel.recv_exit_status()
        print("restart exit:", rc, out.read().decode().strip()[-300:])
    ssh.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
