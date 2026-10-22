"""Source-only Python subprocesses for immutable cycle snapshots.

-B prevents writes, not reads. Reject exported caches and bypass cached code in
SourceFileLoader even if a cache appears after export. Sourceless imports fail.
This module is part of the measured semantic dependency set.
"""
import importlib.machinery
import os
from pathlib import Path
import sys


def reject_bytecode(root):
    for directory, dirs, files in os.walk(root, followlinks=False):
        if "__pycache__" in dirs or any(Path(n).suffix in (".pyc", ".pyo") for n in files):
            raise ValueError(f"snapshot contains Python bytecode/cache: {directory}")


def install():
    if not sys.flags.dont_write_bytecode:
        raise RuntimeError("source-only snapshot requires Python -B")
    sys.dont_write_bytecode = True

    def source_code(loader, fullname):
        path = loader.get_filename(fullname)
        return loader.source_to_code(loader.get_data(path), path)

    def refuse_bytecode(loader, fullname):
        raise ImportError(f"sourceless module refused in cycle snapshot: {fullname}")

    importlib.machinery.SourceFileLoader.get_code = source_code
    importlib.machinery.SourcelessFileLoader.get_code = refuse_bytecode
    sys.path_importer_cache.clear()


# Execute this module's .py directly before any snapshot import, including itself.
# The tools were hashed by the launcher before the bootstrap is started.
BOOTSTRAP = """import sys
from pathlib import Path
tools = Path(sys.argv.pop(1)).resolve()
program = sys.argv.pop(1)
bootstrap = tools / 'cycle_source.py'
namespace = {'__name__': 'cycle_source_bootstrap', '__file__': str(bootstrap)}
exec(compile(bootstrap.read_bytes(), str(bootstrap), 'exec'), namespace)
namespace['reject_bytecode'](tools.parent)
namespace['install']()
sys.path.insert(0, str(tools))
exec(program)
"""


def command(tools, program, *args):
    return [sys.executable, "-I", "-B", "-c", BOOTSTRAP, str(tools), program, *map(str, args)]


def script_command(path, *args):
    path = Path(path)
    program = ("__file__ = sys.argv.pop(1); sys.argv[0] = __file__; "
               "exec(compile(Path(__file__).read_bytes(), __file__, 'exec'))")
    return command(path.parent, program, path, *args)
