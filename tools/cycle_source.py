"""Canonical source imports and executed-module evidence for cycle snapshots.

-B prevents writes, not reads. Compile source ourselves and audit its canonical
origin before execution, including imports made with spec_from_file_location.
The launcher owns the temporary audit directory; children never see its key.
"""
import ast
import hashlib
import functools
import importlib.machinery
import importlib.util
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import sysconfig
import threading
import uuid

AUDIT_ENV = "BFME_CYCLE_MODULE_AUDIT"


# Installation files are an accepted same-account trust boundary, but changes
# must change rule identity. Never discover dependencies via site or caller paths.
DEPENDENCIES = ("pefile.py", "peutils.py", "ordlookup", "capstone")


def runtime_paths():
    stdlib = Path(sysconfig.get_path("stdlib")).resolve()
    prefix = Path(sys.executable).absolute().parent
    prefix = prefix.parent if prefix.name in ("bin", "Scripts") else prefix
    packages = prefix / ("Lib/site-packages" if os.name == "nt" else
                         f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages")
    native = Path(sys.base_prefix) / "DLLs" if os.name == "nt" else stdlib / "lib-dynload"
    return stdlib, native.resolve(), packages


def dependency_locations():
    stdlib, _, packages = runtime_paths()
    if os.name == "nt":
        import ctypes
        buffer = ctypes.create_unicode_buffer(32768)
        if ctypes.windll.shell32.SHGetFolderPathW(None, 0x0028, None, 0, buffer) != 0:
            raise OSError("cannot resolve account profile")
        user = Path(buffer.value) / f"AppData/Roaming/Python/Python{sys.version_info.major}{sys.version_info.minor}/site-packages"
    else:
        import pwd
        user = Path(pwd.getpwuid(os.getuid()).pw_dir) / f".local/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    # Fixed installation locations, never site.getsitepackages(), .pth or
    # sys.path. Only these individual providers can be imported from them.
    roots = (packages, user, stdlib / "site-packages", stdlib / "dist-packages")
    return {name: next((p / name for p in roots if (p / name).exists()), packages / name)
            for name in DEPENDENCIES}


@functools.lru_cache(maxsize=8192)
def _installed_hash(path, generation):
    # Memory only: every interpreter run must read its own installation bytes.
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def file_hash(path):
    path = Path(path)
    st = path.stat()
    return _installed_hash(str(path), (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns))


def runtime_identity():
    stdlib, native, packages = runtime_paths()
    files = {}
    # -B stops cache writes, not pre-bootstrap cache reads (notably encodings).
    # Resource files and test packages can also supply behavior. Bind every
    # file, including symlinked providers; only separately bound packages are
    # excluded. Refuse directory cycles rather than silently omitting inputs.
    def inventory(directory, prefix, ancestors=frozenset()):
        resolved = directory.resolve()
        if resolved in ancestors:
            raise ValueError(f"recursive interpreter installation: {directory}")
        for path in sorted(directory.iterdir()):
            name = prefix + path.name
            if path.is_dir():
                if path.name not in ("site-packages", "dist-packages"):
                    inventory(path, name + "/", ancestors | {resolved})
            elif path.is_file():
                files[name] = file_hash(path)

    inventory(stdlib, "stdlib/")
    for name, path in dependency_locations().items():
        candidates = path.rglob("*") if path.is_dir() else (path,)
        for item in candidates:
            if item.is_file() and "__pycache__" not in item.parts:
                files["packages/" + item.relative_to(path.parent).as_posix()] = file_hash(item)
    if not native.is_relative_to(stdlib) and native.is_dir():
        inventory(native, "native/")
    # Startup files are never executed, but installation changes remain visible.
    for path in sorted(packages.glob("*.pth")) + [packages / "sitecustomize.py", packages / "usercustomize.py",
                                                Path(sys.executable).absolute().parent.parent / "pyvenv.cfg"]:
        if path.is_file():
            files["startup/" + path.name] = file_hash(path)
    executable = Path(sys.executable).resolve()
    base_executable = Path(getattr(sys, "_base_executable", sys.executable)).resolve()
    files["runtime/base-executable"] = file_hash(base_executable)
    for directory in (executable.parent, base_executable.parent):
        for path in directory.glob("*._pth"):
            files["runtime/" + path.name] = file_hash(path)
    for path in Path(sys.base_prefix).glob("python*.dll"):
        files["runtime/" + path.name] = file_hash(path)
    for name in (sysconfig.get_config_var("LDLIBRARY"),):
        if name:
            library = Path(sysconfig.get_config_var("LIBDIR") or executable.parent) / name
            if library.is_file():
                files["runtime/" + name] = file_hash(library)
    return {"version": sys.version, "executable_sha256": file_hash(executable),
            "files_sha256": hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()}


def clean_environment(environment=None):
    # Fixed executable search and account home; loader variables, PYTHON*, Git
    # overrides, caller toolchain flags and working-tree settings cannot enter.
    clean = {"PATH": os.defpath, "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"}
    if os.name == "nt":
        import ctypes
        buffer = ctypes.create_unicode_buffer(32768)
        if not ctypes.windll.kernel32.GetWindowsDirectoryW(buffer, len(buffer)):
            raise OSError("cannot resolve Windows directory")
        clean.update(SystemRoot=buffer.value, WINDIR=buffer.value, PATH=str(Path(buffer.value) / "System32"))
        if ctypes.windll.shell32.SHGetFolderPathW(None, 0x0028, None, 0, buffer) != 0:
            raise OSError("cannot resolve account profile")
        clean.update(HOME=buffer.value, USERPROFILE=buffer.value)
    else:
        import pwd
        clean["HOME"] = pwd.getpwuid(os.getuid()).pw_dir
    supplied = os.environ if environment is None else environment
    # Only launcher-owned coordination fields survive recursive Python helpers.
    for name in (AUDIT_ENV, "BFME_CYCLE_EXPECTED_SEMANTIC", "LINK_CYCLE_ROOT", "GIT_CEILING_DIRECTORIES"):
        if name in supplied:
            clean[name] = supplied[name]
    clean["BFME_OBJSTORE"] = "off"
    return clean


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


def audit_modules(directory, *, require_complete=True, roots=None, runtime=False):
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
        if runtime and record.get("runtime_identity") != runtime_identity():
            raise ValueError("incompatible interpreter installation")
        for name, entry in record.get("runtime_modules" if runtime else "modules", {}).items():
            if name in modules and modules[name] != entry:
                raise ValueError(f"executed module changed across subprocesses: {name}")
            modules[name] = entry
    return dict(sorted(modules.items()))


def install(tools=None, *, bootstrap_raw=None, early=None):
    if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
        raise RuntimeError("source-only snapshot requires Python -I -S -B")
    sys.dont_write_bytecode = True
    tools = Path(tools or Path(__file__).parent).resolve()
    root = tools.parent
    audited = os.environ.get(AUDIT_ENV)
    declared = declared_files(tools) if audited else None
    if declared:
        reject_shadows(tools, declared)
    modules = {}
    runtime_modules = {}
    identity = runtime_identity()
    preloaded = tuple(sys.modules.items())
    log = Path(audited) / (uuid.uuid4().hex + ".json") if audited else None

    writer_lock = threading.RLock()
    failed = False

    def write(complete=False):
        if log:
            with writer_lock:
                temporary = log.with_suffix(".tmp")
                temporary.write_text(json.dumps({"complete": complete and not failed, "tools": str(tools),
                                                 "modules": modules, "runtime_modules": runtime_modules,
                                                 "runtime_identity": identity}, sort_keys=True))
                os.replace(temporary, log)

    def invalidate(*args):
        nonlocal failed
        failed = True
        write(False)

    def refuse(message):
        invalidate()
        raise ImportError(message)

    stdlib, native, packages = runtime_paths()
    dependencies = dependency_locations()
    sys.path[:] = [str(tools), str(stdlib), str(native)]

    def record(path, fullname, raw):
        path = Path(path).absolute()
        local_name = fullname.split(".")[0] + ".py"
        inside = path.is_relative_to(root) or path.resolve().is_relative_to(root)
        if inside or (tools / local_name).exists() or (declared and local_name in declared):
            canonical = tools / (fullname + ".py")
            if "." in fullname or path != canonical or path.resolve() != canonical or path.is_symlink():
                refuse(f"non-canonical snapshot module origin: {fullname}: {path}")
            name, entry = module_record(tools, path, raw)
            if declared and name not in declared:
                refuse(f"unexpected executed snapshot module: {name}")
            destination = modules
        else:
            resolved = path.resolve()
            dependency = dependencies.get(fullname.split(".")[0] + ".py") or dependencies.get(fullname.split(".")[0])
            if dependency is not None and (resolved == dependency.resolve() or
                    (dependency.is_dir() and resolved.is_relative_to(dependency.resolve()))):
                origin = "packages/" + resolved.relative_to(dependency.parent.resolve()).as_posix()
            elif resolved.is_relative_to(stdlib) and not {"site-packages", "dist-packages"}.intersection(resolved.parts):
                origin = "stdlib/" + resolved.relative_to(stdlib).as_posix()
            elif resolved.is_relative_to(native):
                origin = "native/" + resolved.relative_to(native).as_posix()
            else:
                refuse(f"non-canonical snapshot module origin: {fullname}: {path}")
            name, entry = fullname, {"origin": origin, "sha256": hashlib.sha256(raw).hexdigest()}
            destination = runtime_modules
        with writer_lock:
            if name in destination and destination[name] != entry:
                refuse(f"executed snapshot module changed: {name}")
            destination[name] = entry
            write()

    def source_code(loader, fullname):
        path = loader.get_filename(fullname)
        raw = loader.get_data(path)
        record(path, fullname, raw)
        return loader.source_to_code(raw, path)

    # Include modules loaded by CPython before BOOTSTRAP, as well as imports
    # needed to install this recorder. Their bytecode/data is bound by identity
    # even when __spec__.origin reports the corresponding source file.
    for name, module in preloaded:
        spec = getattr(module, "__spec__", None)
        origin = getattr(spec, "origin", None)
        path = getattr(module, "__file__", None)
        if origin in ("built-in", "frozen") or not path:
            runtime_modules[name] = {"origin": (origin or "interpreter") + ":" + name,
                                     "sha256": identity["executable_sha256"]}
        else:
            record(path, name, Path(path).read_bytes())

    def refuse_bytecode(loader, fullname):
        refuse(f"sourceless module refused in cycle snapshot: {fullname}")

    class CanonicalFinder:
        @staticmethod
        def find_spec(fullname, path=None, target=None):
            dependency = dependencies.get(fullname + ".py") or dependencies.get(fullname)
            if dependency is not None and dependency.exists():
                source = dependency / "__init__.py" if dependency.is_dir() else dependency
                spec = importlib.util.spec_from_file_location(fullname, source)
            else:
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
                refuse(f"non-canonical snapshot module origin: {fullname}: {origin}")
            return spec

    original_native = importlib.machinery.ExtensionFileLoader.create_module

    def native_module(loader, spec):
        path = Path(loader.path).resolve()
        if path.is_relative_to(root) or (tools / (spec.name.split(".")[0] + ".py")).exists():
            refuse(f"non-canonical snapshot module origin: {spec.name}: {path}")
        record(loader.path, spec.name, Path(loader.path).read_bytes())
        return original_native(loader, spec)

    importlib.machinery.ExtensionFileLoader.create_module = native_module
    importlib.machinery.SourceFileLoader.get_code = source_code
    importlib.machinery.SourcelessFileLoader.get_code = refuse_bytecode
    sys.meta_path.insert(0, CanonicalFinder())
    if early is not None:
        early["meta_path"] = tuple(sys.meta_path)
        early["paths"] = frozenset(sys.path)
        early["record"] = record
        early["invalidate"] = invalidate
        def special(name, origin):
            runtime_modules[name] = {"origin": origin + ":" + name,
                                     "sha256": identity["executable_sha256"]}
            write()
        early["special"] = special
        for fullname, path, raw in early["pending"]:
            record(path, fullname, raw)
        early["pending"].clear()

    def native_library(event, args):
        if event != "ctypes.dlopen" or args[0] is None:
            return
        path = Path(os.fsdecode(args[0]))
        # In particular, capstone must never fall through to its cwd or
        # environment library search. Its exact native provider is evidence too.
        if not path.is_absolute():
            refuse(f"non-canonical snapshot module origin: native library: {path}")
        provider = next((name.removesuffix(".py") for name, location in dependencies.items()
                         if location.is_dir() and path.resolve().is_relative_to(location.resolve())), None)
        if provider is None:
            refuse(f"non-canonical snapshot module origin: native library: {path}")
        record(path, provider + ".__native__." + path.name, path.read_bytes())

    if os.name == "nt":
        # Resolve/cache only the fixed account/system API DLL handles before
        # enforcing package-only ctypes providers for measurement code.
        clean_environment({})
    sys.addaudithook(native_library)
    sys.path_importer_cache.clear()
    # The directly compiled bootstrap is itself an executed semantic module.
    record(tools / "cycle_source.py", "cycle_source",
           bootstrap_raw if bootstrap_raw is not None else (tools / "cycle_source.py").read_bytes())
    write()

    if audited:
        original_popen = subprocess.Popen

        def audited_popen(args, *positional, **kwargs):
            if not isinstance(args, (list, tuple)) or kwargs.get("shell") or kwargs.get("executable"):
                invalidate()
                raise ValueError("unbootstrapped subprocess command in cycle snapshot")
            executable = (shutil.which(os.fspath(args[0])) if isinstance(args, (list, tuple)) and args else None)
            python = executable and Path(executable).resolve() == Path(sys.executable).resolve()
            if executable and Path(executable).name.lower().startswith(("python", "pypy")) and not python:
                invalidate()
                raise ValueError("unbootstrapped Python interpreter in cycle snapshot")
            if executable and Path(executable).suffix == ".py":
                args = [sys.executable, executable, *args[1:]]
                python = True
            if python:
                args = list(args)
                if not (len(args) > 5 and args[1:5] == ["-I", "-S", "-B", "-c"] and args[5] == BOOTSTRAP):
                    # Every Python helper must use the same bootstrap, including
                    # helpers launched by build/provider code through subprocess.
                    if len(args) < 2 or args[1].startswith("-"):
                        invalidate()
                        raise ValueError("unbootstrapped Python helper in cycle snapshot")
                    script = Path(args[1])
                    if not script.is_absolute():
                        script = Path(kwargs.get("cwd") or Path.cwd()) / script
                    if script.parent.resolve() != tools:
                        invalidate()
                        raise ValueError("Python helper outside snapshot tools")
                    args = script_command(script, *args[2:])
                env = clean_environment(kwargs.get("env"))
                env[AUDIT_ENV] = audited
                kwargs["env"] = env
            return original_popen(args, *positional, **kwargs)
        subprocess.Popen = audited_popen

        # ProcessPoolExecutor's spawn transport bypasses subprocess.Popen on
        # both platforms. Cover its workers and POSIX resource tracker too.
        import multiprocessing.spawn as spawn
        import multiprocessing.util as mp_util
        import multiprocessing.resource_tracker as tracker
        original_command = spawn.get_command_line

        def isolated_spawn_command(args):
            executable = os.fsdecode(args[0])
            environment = dict(os.environ)
            # cycle() sets this after clean_environment has filtered callers.
            # It controls scheduling only; never preserve it from caller envs.
            workers = environment.pop("BUILD_POOL", None)
            if Path(executable).resolve() != Path(sys.executable).resolve() \
                    or environment != clean_environment() \
                    or (workers is not None and (not workers.isascii() or not workers.isdecimal()
                                                or int(workers) < 1)):
                invalidate()
                raise ValueError("unbootstrapped multiprocessing environment")
            args = [os.fsdecode(a) for a in args]
            if args[1:5] == ["-I", "-S", "-B", "-c"] and args[5] == BOOTSTRAP:
                return args
            index = args.index("-c")
            program = args[index + 1]
            if not program.startswith(("from multiprocessing.spawn import spawn_main;",
                                       "from multiprocessing.resource_tracker import main;")):
                invalidate()
                raise ValueError("unbootstrapped multiprocessing program")
            return command(tools, program, *args[index + 2:])

        def spawn_command(**kwargs):
            return isolated_spawn_command(original_command(**kwargs))

        spawn.get_command_line = spawn_command
        if os.name != "nt":
            original_spawnv = mp_util.spawnv_passfds

            def spawnv(path, args, passfds):
                args = isolated_spawn_command(args)
                return original_spawnv(os.fsencode(sys.executable), args, passfds)

            mp_util.spawnv_passfds = spawnv

        def finish_helpers():
            # All pools have joined at measurement exit. Wait for the tracker
            # as well, so no Python child can execute after audit completion.
            if tracker._resource_tracker._pid is not None:
                tracker._resource_tracker._stop()

        early["finish_helpers"] = finish_helpers

    return record, write, declared


# Execute this .py directly before any snapshot import, including itself.
BOOTSTRAP = """import sys
# CPython has already imported startup modules such as encodings. Their
# installation bytes and origins are bound by install(); -B does not stop reads.
# From here on, record and validate imports before executing them.
_boot = sys.modules['_frozen_importlib']
_external = sys.modules['_frozen_importlib_external']
_early = {'pending': [], 'meta_path': tuple(sys.meta_path)}
_early['path_hooks'] = tuple(sys.path_hooks)
_find_spec = _boot._find_spec
_module_from_spec = _boot.module_from_spec
_native_create = _external.ExtensionFileLoader.create_module

def _refuse(message):
    if 'invalidate' in _early:
        _early['invalidate'](False)
    raise ImportError('non-canonical snapshot module origin: ' + message)

def _validate(spec):
    if spec is not None and spec.loader not in (_boot.BuiltinImporter, _boot.FrozenImporter) and type(spec.loader) not in (_external.SourceFileLoader, _external.ExtensionFileLoader):
        _refuse(str(spec.origin))
    if spec is not None and spec.origin in ('built-in', 'frozen') and 'special' in _early:
        _early['special'](spec.name, spec.origin)
    return spec

def _guard_find(name, path, target=None):
    if len(sys.meta_path) != len(_early['meta_path']) or any(a is not b for a, b in zip(sys.meta_path, _early['meta_path'])):
        _refuse('custom meta-path loader')
    if len(sys.path_hooks) != len(_early['path_hooks']) or any(a is not b for a, b in zip(sys.path_hooks, _early['path_hooks'])):
        _refuse('custom path loader')
    if 'paths' in _early and any(type(p) is not str or p not in _early['paths'] for p in sys.path):
        _refuse('path outside isolated interpreter')
    if 'paths' in _early and any(type(f) is not _external.FileFinder for f in sys.path_importer_cache.values() if f is not None):
        _refuse('custom cached path loader')
    return _validate(_find_spec(name, path, target))

def _guard_module(spec):
    _validate(spec)
    return _module_from_spec(spec)

def _record_raw(name, path, raw):
    if 'record' in _early:
        _early['record'](path, name, raw)
    else:
        _early['pending'].append((name, path, raw))

def _guard_source(loader, name):
    raw = loader.get_data(loader.path)
    _record_raw(name, loader.path, raw)
    return loader.source_to_code(raw, loader.path)

def _guard_native(loader, spec):
    with open(loader.path, 'rb') as stream:
        _record_raw(spec.name, loader.path, stream.read())
    return _native_create(loader, spec)

_boot._find_spec = _guard_find
_boot.module_from_spec = _guard_module
_external.SourceFileLoader.get_code = _guard_source
_external.ExtensionFileLoader.create_module = _guard_native
# Discard the optional stdlib zip entry too: file loaders only.
sys.path[:] = [p for p in sys.path if not p.endswith('.zip')]
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
record, write, declared = namespace['install'](tools, bootstrap_raw=bootstrap_raw, early=_early)
if declared:
    import importlib
    for name in declared:
        importlib.import_module(Path(name).stem)
try:
    exec(program)
except SystemExit as error:
    if error.code not in (None, 0):
        raise
if 'finish_helpers' in _early:
    _early['finish_helpers']()
write(True)
"""


def command(tools, program, *args):
    return [sys.executable, "-I", "-S", "-B", "-c", BOOTSTRAP, str(tools), program, *map(str, args)]


def script_command(path, *args):
    path = Path(path)
    program = ("__file__ = sys.argv.pop(1); sys.argv[0] = __file__; "
               "raw = Path(__file__).read_bytes(); record(__file__, Path(__file__).stem, raw); "
               "exec(compile(raw, __file__, 'exec'))")
    return command(path.parent, program, path, *args)
