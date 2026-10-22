"""Host-local cycle stamps. Keys never belong in a repository.

Readers trust only the fixed account key at ~/.config/open-bfme/cycle_key.
The in-process test seam is never populated from CLI arguments or environment.
"""
import hashlib
import hmac
import json
import os
from pathlib import Path
import stat
import subprocess

STAMP = "host_stamp.json"
SCHEMA = "bfme1-cycle-host-stamp/1"
# Resolve the account home independently of worker-controlled HOME on POSIX.
try:
    import pwd
    _ACCOUNT_HOME = Path(pwd.getpwuid(os.getuid()).pw_dir)
except ImportError:  # Windows has no pwd database.
    _ACCOUNT_HOME = Path.home()
DEFAULT_KEY = _ACCOUNT_HOME / ".config/open-bfme/cycle_key"
_reader_key_for_tests = None  # Tests monkeypatch this; no production setter.


class KeyError(ValueError):
    pass


def key_path(path):
    path = Path(path).expanduser().absolute()
    resolved = path.resolve()
    for parent in resolved.parents:
        if (parent / ".git").exists():
            raise KeyError("host key must be outside every git worktree")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    got = subprocess.run(["git", "-C", str(resolved.parent), "rev-parse", "--git-dir"],
                         capture_output=True, env=env)
    if got.returncode == 0:
        raise KeyError("host key must be outside every git repository")
    return path


def read_key(path):
    path = key_path(path)
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        st = os.fstat(fd)
        # Validate the opened inode, including aliases and a parent swapped
        # between pathname validation and open. Linux exposes its actual path.
        opened = Path(f"/proc/self/fd/{fd}")
        key_path(opened.resolve(strict=True) if opened.exists() else path)
        current = path.stat(follow_symlinks=False)
        if (st.st_dev, st.st_ino) != (current.st_dev, current.st_ino):
            raise KeyError("host key changed while opening")
        if st.st_nlink != 1:
            raise KeyError("host key must have exactly one hardlink")
        if path.is_symlink() or not stat.S_ISREG(st.st_mode) or stat.S_IMODE(st.st_mode) != 0o600:
            raise KeyError("host key must be a regular file with mode 0600")
        if hasattr(os, "getuid") and st.st_uid != os.getuid():
            raise KeyError("host key belongs to another user")
        key = os.read(fd, 4097)
        if not 32 <= len(key) <= 4096:
            raise KeyError("host key must contain 32..4096 secret bytes")
        return key
    finally:
        os.close(fd)


def keygen(path=DEFAULT_KEY):
    path = Path(path).expanduser().absolute()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = key_path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(os.urandom(32))
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return path


def configured_keys():
    return [DEFAULT_KEY if _reader_key_for_tests is None else _reader_key_for_tests]


def verify(directory):
    """Return refusal sub_reason, or None for a valid stamp under a trusted key."""
    directory = Path(directory)
    path = directory / STAMP
    if not path.exists():
        return "unstamped"
    try:
        if path.is_symlink() or not path.is_file():
            return "bad-stamp"
        doc = json.loads(path.read_bytes())
        digest = hashlib.sha256((directory / "manifest.json").read_bytes()).hexdigest()
        if doc.get("schema") != SCHEMA or doc.get("manifest_sha256") != digest:
            return "bad-stamp"
        keys = []
        for p in configured_keys():
            if p.exists():
                keys.append(read_key(p))
        if not keys:
            return "unstamped"
        for key in keys:
            if doc.get("key_id") == hashlib.sha256(key).hexdigest() and hmac.compare_digest(
                    doc.get("hmac_sha256", ""), hmac.new(key, bytes.fromhex(digest), hashlib.sha256).hexdigest()):
                return None
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return "bad-stamp"
