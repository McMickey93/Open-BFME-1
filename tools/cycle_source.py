"""Canonical source imports and executed-module evidence for cycle snapshots.

-B prevents writes, not reads. Compile source ourselves and audit its canonical
origin before execution, including imports made with spec_from_file_location.
The launcher owns the temporary audit directory; children never see its key.
"""
import ast
import hashlib
import importlib.machinery
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import threading
import uuid

AUDIT_ENV = "BFME_CYCLE_MODULE_AUDIT"


def declared_files(tools):
    tree = ast.parse((Path(tools) / "link_cycle_context.py").read_bytes())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MEASUREMENT_FILES"
                                               for t in node.targets):
            files = ast.literal_eval(node.value)
            if not isinstance(files, (tuple, list)) or not files or any(
                    not isinstance(n, str) or Path(n).name != n or not n.endswith(".py")
                    or not Path(n).stem.isidentifier() for n in files) or len(set(files)) != len(files):
                break
            return tuple(files)
    raise ValueError("snapshot has no canonical declared module set")


def reject_shadows(tools, files=None):
    tools = Path(tools)
    for name in declared_files(tools) if files is None else files:
        if (tools / Path(name).stem).is_dir():
            raise ValueError(f"snapshot package shadows declared module: {name}")
        path = tools / name
        if path.is_symlink() or not path.is_file() or path.resolve() != tools.resolve() / name:
            raise ValueError(f"snapshot module has non-canonical origin: {name}")


def reject_bytecode(root):
    for directory, dirs, files in os.walk(root, followlinks=False):
        if "__pycache__" in dirs or any(Path(n).suffix in (".pyc", ".pyo") for n in files):
            raise ValueError(f"snapshot contains Python bytecode/cache: {directory}")


def module_record(tools, path, raw):
    name = Path(path).relative_to(tools).as_posix()
    return name, {"origin": "tools/" + name, "sha256": hashlib.sha256(raw).hexdigest()}


def audit_modules(directory, *, require_complete=True, roots=None):
    """Union the records of every successful bootstrap, worker and helper.

    A process that exits abnormally has no completed record. Conflicting origins
    or bytes (including a file changed during a run) fail closed.
    """
    modules = {}
    paths = list(Path(directory).glob("*.json"))
    if not paths:
        raise ValueError("missing executed-module evidence")
    for path in paths:
        record = json.loads(path.read_bytes())
        if roots is not None and record.get("tools") not in {str(Path(p).resolve()) for p in roots}:
            raise ValueError("executed module origin outside snapshot tools")
        if require_complete and record.get("complete") is not True:
            raise ValueError("incomplete executed-module evidence")
        for name, entry in record["modules"].items():
            if name in modules and modules[name] != entry:
                raise ValueError(f"executed module changed across subprocesses: {name}")
            modules[name] = entry
    return dict(sorted(modules.items()))


def install(tools=None, *, bootstrap_raw=None):
    if not sys.flags.dont_write_bytecode:
        raise RuntimeError("source-only snapshot requires Python -B")
    sys.dont_write_bytecode = True
    tools = Path(tools or Path(__file__).parent).resolve()
    root = tools.parent
    audited = os.environ.get(AUDIT_ENV)
    declared = declared_files(tools) if audited else None
    if declared:
        reject_shadows(tools, declared)
    modules = {}
    log = Path(audited) / (uuid.uuid4().hex + ".json") if audited else None

    writer_lock = threading.RLock()

    def write(complete=False):
        if log:
            with writer_lock:
                temporary = log.with_suffix(".tmp")
                temporary.write_text(json.dumps({"complete": complete, "tools": str(tools),
                                                 "modules": modules}, sort_keys=True))
                os.replace(temporary, log)

    def record(path, fullname, raw):
        path = Path(path).absolute()
        # A local name may never resolve to a provider outside this tools tree.
        local_name = fullname.split(".")[0] + ".py"
        inside = path.is_relative_to(root) or path.resolve().is_relative_to(root)
        if inside or (tools / local_name).exists() or (declared and local_name in declared):
            canonical = tools / (fullname + ".py")
            if "." in fullname or path != canonical or path.resolve() != canonical or path.is_symlink():
                raise ImportError(f"non-canonical snapshot module origin: {fullname}: {path}")
            name, entry = module_record(tools, path, raw)
            if declared and name not in declared:
                raise ImportError(f"unexpected executed snapshot module: {name}")
            with writer_lock:
                if name in modules and modules[name] != entry:
                    raise ImportError(f"executed snapshot module changed: {name}")
                modules[name] = entry
                write()

    def source_code(loader, fullname):
        path = loader.get_filename(fullname)
        raw = loader.get_data(path)
        record(path, fullname, raw)
        return loader.source_to_code(raw, path)

    def refuse_bytecode(loader, fullname):
        raise ImportError(f"sourceless module refused in cycle snapshot: {fullname}")

    class CanonicalFinder:
        @staticmethod
        def find_spec(fullname, path=None, target=None):
            spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
            if spec is None:
                return None
            locations = spec.submodule_search_locations or ()
            origin = spec.origin
            local = ((tools / (fullname.split(".")[0] + ".py")).exists() or
                     (origin and Path(origin).resolve().is_relative_to(root)) or
                     any(Path(p).resolve().is_relative_to(root) for p in locations))
            if local and (locations or not origin or
                          type(spec.loader) is not importlib.machinery.SourceFileLoader or
                          Path(origin).absolute() != tools / (fullname + ".py")):
                raise ImportError(f"non-canonical snapshot module origin: {fullname}: {origin}")
            return spec

    original_native = importlib.machinery.ExtensionFileLoader.create_module

    def native_module(loader, spec):
        path = Path(loader.path).resolve()
        if path.is_relative_to(root) or (tools / (spec.name.split(".")[0] + ".py")).exists():
            raise ImportError(f"non-canonical snapshot module origin: {spec.name}: {path}")
        return original_native(loader, spec)

    importlib.machinery.ExtensionFileLoader.create_module = native_module
    importlib.machinery.SourceFileLoader.get_code = source_code
    importlib.machinery.SourcelessFileLoader.get_code = refuse_bytecode
    sys.meta_path.insert(0, CanonicalFinder())
    sys.path_importer_cache.clear()
    # The directly compiled bootstrap is itself an executed semantic module.
    record(tools / "cycle_source.py", "cycle_source",
           bootstrap_raw if bootstrap_raw is not None else (tools / "cycle_source.py").read_bytes())
    write()

    if audited:
        original_popen = subprocess.Popen

        def audited_popen(args, *positional, **kwargs):
            executable = (shutil.which(os.fspath(args[0])) if isinstance(args, (list, tuple)) and args else None)
            if executable and Path(executable).resolve() == Path(sys.executable).resolve():
                args = list(args)
                if not (len(args) > 4 and args[1:4] == ["-I", "-B", "-c"] and args[4] == BOOTSTRAP):
                    # Every Python helper must use the same bootstrap, including
                    # helpers launched by build/provider code through subprocess.
                    if len(args) < 2 or args[1].startswith("-"):
                        raise ValueError("unbootstrapped Python helper in cycle snapshot")
                    script = Path(args[1])
                    if not script.is_absolute():
                        script = Path(kwargs.get("cwd") or Path.cwd()) / script
                    if script.parent.resolve() != tools:
                        raise ValueError("Python helper outside snapshot tools")
                    args = script_command(script, *args[2:])
                env = dict(kwargs.get("env") or os.environ)
                env[AUDIT_ENV] = audited
                kwargs["env"] = env
            return original_popen(args, *positional, **kwargs)
        subprocess.Popen = audited_popen

    return record, write, declared


# Execute this .py directly before any snapshot import, including itself.
BOOTSTRAP = """import sys
from pathlib import Path
tools = Path(sys.argv.pop(1)).resolve()
import os
os.environ['LINK_CYCLE_ROOT'] = str(tools.parent)
program = sys.argv.pop(1)
bootstrap = tools / 'cycle_source.py'
namespace = {'__name__': 'cycle_source_bootstrap', '__file__': str(bootstrap)}
bootstrap_raw = bootstrap.read_bytes()
exec(compile(bootstrap_raw, str(bootstrap), 'exec'), namespace)
namespace['reject_bytecode'](tools.parent)
record, write, declared = namespace['install'](tools, bootstrap_raw=bootstrap_raw)
sys.path.insert(0, str(tools))
# Load the whole declared closure once, so optional paths cannot silently omit
# a provider from the executed set. Imports run definitions only, never CLIs.
if declared:
    import importlib
    for name in declared:
        importlib.import_module(Path(name).stem)
try:
    exec(program)
except SystemExit as error:
    if error.code not in (None, 0):
        raise
write(True)
"""


def command(tools, program, *args):
    return [sys.executable, "-I", "-B", "-c", BOOTSTRAP, str(tools), program, *map(str, args)]


def script_command(path, *args):
    path = Path(path)
    program = ("__file__ = sys.argv.pop(1); sys.argv[0] = __file__; "
               "raw = Path(__file__).read_bytes(); record(__file__, Path(__file__).stem, raw); "
               "exec(compile(raw, __file__, 'exec'))")
    return command(path.parent, program, path, *args)
