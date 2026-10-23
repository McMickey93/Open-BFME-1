"""Canonical source imports and executed-module evidence for cycle snapshots.

-B prevents writes, not reads. Compile source ourselves and audit its canonical
origin before execution, including imports made with spec_from_file_location.
The launcher owns the temporary audit directory; children never see its key.
"""
import ast
import hashlib
import functools
import errno
import importlib.machinery
import importlib.util
import json
import os
import shutil
import stat
import time
import zipimport
from pathlib import Path
import subprocess
import sys
import sysconfig
import threading
import uuid

AUDIT_ENV = "BFME_CYCLE_MODULE_AUDIT"

# This is the first code run by every measurement/helper, before pathlib or
# any installed provider is imported. Startup files read by CPython itself are
# covered by runtime_inventory. Keep the recorder independent of import hooks.
IO_BOOTSTRAP = r'''import sys
_cycle_io = {'events': {}, 'reads': {}, 'read_errors': set(), 'directories': {},
             'errors': [], 'paused': set(), 'ignored_inputs': set()}
sys._bfme_cycle_io = _cycle_io
_io_os = None
_io_pending = []
def _cycle_open_audit(event, args):
    if event not in ('open', 'os.listdir', 'os.scandir'):
        return
    if _io_os is None:
        _io_pending.append((event, args))
        return
    tid = _io_thread.get_ident()
    if tid in _cycle_io['paused']:
        return
    _cycle_io['paused'].add(tid)
    try:
        path = args[0] if args else '.'
        descriptor = None
        if path is None:
            path = '.'
        if isinstance(path, int):
            if _io_os.name == 'posix':
                descriptor = _io_os.fstat(path)
                if descriptor.st_mode & 0o170000 != 0o100000:
                    return
                path = _io_os.readlink('/proc/self/fd/' + str(path))
                resolved = _io_os.stat(path)
                if (resolved.st_dev, resolved.st_ino) != (descriptor.st_dev, descriptor.st_ino):
                    raise ValueError('cannot resolve audited file descriptor')
            else:
                import ctypes, msvcrt
                kernel = ctypes.windll.kernel32
                handle = ctypes.c_void_p(msvcrt.get_osfhandle(path))
                # Subprocess pipes have no regular-file identity.
                kind = kernel.GetFileType(handle)
                if not kind:
                    raise ValueError('cannot classify audited file descriptor')
                if kind != 1:
                    return
                buffer = ctypes.create_unicode_buffer(32768)
                length = kernel.GetFinalPathNameByHandleW(handle, buffer, len(buffer), 0)
                if not length or length >= len(buffer):
                    raise ValueError('cannot resolve audited file descriptor')
                path = buffer.value
                # Match ordinary resolved snapshot paths, including UNC paths.
                if path.startswith(chr(92) * 2 + '?' + chr(92)):
                    path = path[4:]
                    if path.startswith('UNC' + chr(92)):
                        path = chr(92) * 2 + path[4:]
        path = _io_os.path.realpath(_io_os.fsdecode(path))
        try:
            st = _io_os.stat(path)
            generation = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)
        except FileNotFoundError:
            generation = None
        if descriptor is not None and generation != (descriptor.st_dev, descriptor.st_ino,
                descriptor.st_size, descriptor.st_mtime_ns, descriptor.st_ctime_ns):
            raise ValueError('cannot resolve audited file descriptor generation')
        previous = _cycle_io['events'].setdefault(path, generation)
        if previous != generation:
            _cycle_io['errors'].append(path)
        # The audit fires before open. Hash a readable regular file immediately,
        # retaining both content and inode generation, independently of rule
        # classification. Writes are not consumption of their previous bytes.
        flags = args[2] if event == 'open' and len(args) > 2 else 0
        readable = event == 'open' and not flags & _io_write_flags
        if readable and generation is not None and st.st_mode & 0o170000 == 0o100000:
            if not any(path == top or path.startswith(top + _io_os.sep)
                       for top in _cycle_io['ignored_inputs']):
                previous = _cycle_io['reads'].get(path)
                if previous is None:
                    import hashlib
                    with open(path, 'rb') as stream:
                        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
                        end = _io_fstat(stream.fileno())
                    if (end.st_dev, end.st_ino, end.st_size, end.st_mtime_ns, end.st_ctime_ns) != generation:
                        _cycle_io['read_errors'].add(path)
                    _cycle_io['reads'][path] = {'generation': generation, 'sha256': digest}
                elif tuple(previous['generation']) != generation:
                    _cycle_io['read_errors'].add(path)
        if event != 'open':
            entries = tuple(sorted(_io_os.listdir(path)))
            previous = _cycle_io['directories'].setdefault(path, entries)
            if previous != entries:
                _cycle_io['errors'].append(path)
    except OSError:
        # Failed opens/listings do not supply bytes. If the file subsequently
        # appears, the saved absent generation above makes that fail closed.
        if event == 'open' and args and isinstance(args[0], int):
            _cycle_io['read_errors'].add('<unresolved descriptor>')
        elif event == 'open':
            _cycle_io['read_errors'].add(path)
    finally:
        _cycle_io['paused'].remove(tid)
sys.addaudithook(_cycle_open_audit)
import _thread as _io_thread
import os as _io_os
_io_write_flags = _io_os.O_WRONLY | _io_os.O_TRUNC
_io_fstat = _io_os.fstat
for _event, _args in _io_pending:
    _cycle_open_audit(_event, _args)
_io_pending.clear()
# os.open's audit event omits dir_fd and runs before success. Suppress that
# ambiguous event and observe the descriptor actually returned by the kernel.
_cycle_os_open = _io_os.open
def _cycle_descriptor_open(*args, **kwargs):
    tid = _io_thread.get_ident()
    if tid in _cycle_io['paused']:
        return _cycle_os_open(*args, **kwargs)
    _cycle_io['paused'].add(tid)
    try:
        fd = _cycle_os_open(*args, **kwargs)
    finally:
        _cycle_io['paused'].remove(tid)
    flags = args[1] if len(args) > 1 else kwargs['flags']
    # Fresh exclusive/truncated outputs do not supply previous file bytes.
    if flags & (_io_os.O_WRONLY | _io_os.O_TRUNC) or (flags & _io_os.O_CREAT and flags & _io_os.O_EXCL):
        return fd
    try:
        _cycle_open_audit('open', (fd, None, flags))
    except BaseException:
        _cycle_io['read_errors'].add('<unresolved descriptor>')
        _io_os.close(fd)
        raise
    return fd
sys._bfme_cycle_descriptor_open = _cycle_descriptor_open
'''


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


def dependency_roots():
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
    return packages, user, stdlib / "site-packages", stdlib / "dist-packages"


def dependency_locations():
    roots = dependency_roots()
    packages = roots[0]
    return {name: next((p / name for p in roots if (p / name).exists()), packages / name)
            for name in DEPENDENCIES}


# Kept only in this process. A new launcher/preflight always reads fresh bytes.
@functools.lru_cache(maxsize=None)
def _installed_hash(path, generation):
    with open(path, "rb") as stream:
        value = hashlib.file_digest(stream, "sha256").hexdigest()
        if _generation(os.fstat(stream.fileno())) != generation:
            raise ValueError(f"interpreter file changed while hashing: {path}")
    return value


def _generation(st):
    return st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns


def file_hash(path):
    path = Path(path)
    return _installed_hash(str(path), _generation(path.stat()))


_INTERPRETER = sys.executable
_STARTUP_PATH = tuple(sys.path)


@functools.lru_cache(maxsize=1)
def isolated_search_path():
    # Readers use the same search roots as the -I -S measurement, never their
    # caller's cwd, PYTHONPATH, pytest paths or site startup additions.
    if sys.flags.isolated and sys.flags.no_site:
        return getattr(sys, "_bfme_cycle_startup_path", _STARTUP_PATH)
    program = IO_BOOTSTRAP + ("\np=sys.argv[1]; ns={'__file__':p, '__name__':'path_preflight'}; "
                             "exec(compile(open(p,'rb').read(),p,'exec'),ns); "
                             "print(ns['json'].dumps({'paths':sys.path, "
                             "'evidence':ns['observed_runtime'](ns['Path'](p).parent.parent)}))")
    result = subprocess.run([_INTERPRETER, "-I", "-S", "-B", "-c", program, __file__],
                            env=clean_environment({}), check=True, capture_output=True, text=True)
    value = json.loads(result.stdout)
    isolated_search_path.evidence = value["evidence"]
    return tuple(value["paths"])



@functools.lru_cache(maxsize=1)
def loaded_runtime_library():
    """Resolve the provider actually hosting Python's C API, not just sysconfig."""
    import ctypes
    if os.name == "nt":
        buffer = ctypes.create_unicode_buffer(32768)
        if not ctypes.windll.kernel32.GetModuleFileNameW(
                ctypes.c_void_p(sys.dllhandle), buffer, len(buffer)):
            raise OSError("cannot resolve loaded Python DLL")
        return Path(buffer.value).resolve()

    class DlInfo(ctypes.Structure):
        _fields_ = [("filename", ctypes.c_char_p), ("base", ctypes.c_void_p),
                    ("symbol", ctypes.c_char_p), ("address", ctypes.c_void_p)]

    dladdr = ctypes.CDLL(None).dladdr
    dladdr.argtypes = [ctypes.c_void_p, ctypes.POINTER(DlInfo)]
    dladdr.restype = ctypes.c_int
    info = DlInfo()
    address = ctypes.cast(ctypes.pythonapi.Py_IsInitialized, ctypes.c_void_p)
    if not dladdr(address, ctypes.byref(info)) or not info.filename:
        raise OSError("cannot resolve loaded libpython")
    return Path(os.fsdecode(info.filename)).resolve()


def runtime_roots():
    stdlib, native, packages = runtime_paths()
    # The bare prefixes are not loadable roots (sys.base_prefix is /usr on Linux):
    # only their library trees are, plus a venv's pyvenv.cfg, which selects the base.
    roots = [*(Path(prefix) / "pyvenv.cfg" for prefix in {sys.prefix, sys.exec_prefix}),
             *isolated_search_path(), stdlib, native, packages, *dependency_roots(),
             *(path.parent for path in dependency_locations().values()),
             loaded_runtime_library(), Path(sys.executable).resolve(),
             Path(getattr(sys, "_base_executable", sys.executable)).resolve()]
    library = sysconfig.get_config_var("LDLIBRARY")
    if library:
        roots.append(Path(sysconfig.get_config_var("LIBDIR") or Path(sys.executable).parent) / library)
    # On Windows libpython is a DLL beside the executable/base installation.
    if os.name == "nt":
        for directory in {Path(sys.executable).resolve().parent, Path(sys.base_prefix)}:
            roots.extend(directory.glob("python*.dll"))
    return tuple(sorted({str(Path(p).absolute()) for p in roots}))


def runtime_inventory(roots, *, snapshot=None):
    """All reachable regular files, including data, caches and symlink targets.

    Paths and absent roots are bound too. Visit resolved directories once, so
    symlink cycles terminate without excluding any reachable regular file.
    No basename, suffix, package or bytecode-cache exclusions are safe here:
    CPython reads startup caches even with -B, and resource APIs read any file.
    """
    files, links, visited, directories = {}, {}, set(), set()
    excluded = Path(snapshot).resolve() if snapshot else None

    def visit(path):
        try:
            resolved = path.resolve()
        except (RuntimeError, OSError) as error:
            # A symlink loop has no reachable file; retain its link text.
            if isinstance(error, OSError) and error.errno != errno.ELOOP:
                raise
            links[str(path)] = os.readlink(path)
            return
        if excluded and (resolved == excluded or resolved.is_relative_to(excluded)):
            return
        if path.is_symlink():
            links[str(path)] = str(resolved)
        try:
            st = resolved.stat()
        except OSError as error:
            if error.errno == errno.ENOENT:
                return
            if error.errno == errno.ELOOP and path.is_symlink():
                links[str(path)] = os.readlink(path)
                return
            raise
        if stat.S_ISDIR(st.st_mode):
            key = (st.st_dev, st.st_ino)
            if key in visited:
                return
            visited.add(key)
            directories.add(str(resolved))
            with os.scandir(resolved) as entries:
                for entry in entries:
                    visit(Path(entry.path))
        elif stat.S_ISREG(st.st_mode):
            files[str(resolved)] = (file_hash(resolved), st.st_size)

    roots = sorted(set(map(str, roots)))
    for root in roots:
        visit(Path(root))
    payload = {"roots": roots, "links": links, "directories": sorted(directories),
               "files": {name: value[0] for name, value in sorted(files.items())}}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(), files


def runtime_identity(*, snapshot=None):
    started = time.monotonic()
    digest, files = runtime_inventory(runtime_roots(), snapshot=snapshot)
    # Cost is diagnostic only; time/stat metadata must never perturb identity.
    runtime_identity.cost = {"files": len(files), "bytes": sum(v[1] for v in files.values()),
                             "seconds": time.monotonic() - started}
    return {"version": sys.version, "executable_sha256": file_hash(Path(sys.executable).resolve()),
            "files_sha256": digest}


def mapped_files_windows(api=None):
    """Enumerate the actual process modules, including transitive DLL loads.

    The injectable API is used only by unit tests; production always calls the
    process APIs with pointer-sized handles (also on 64-bit Windows).
    """
    import ctypes
    from ctypes import wintypes
    if api is None:
        kernel = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.EnumProcessModules.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.HMODULE),
                                            wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
        psapi.GetModuleFileNameExW.argtypes = [wintypes.HANDLE, wintypes.HMODULE,
                                             wintypes.LPWSTR, wintypes.DWORD]
        api = (kernel.GetCurrentProcess, psapi.EnumProcessModules, psapi.GetModuleFileNameExW)
    current, enumerate_modules, filename = api
    process = current()
    capacity = 256
    while True:
        modules = (wintypes.HMODULE * capacity)()
        needed = wintypes.DWORD()
        if not enumerate_modules(process, modules, ctypes.sizeof(modules), ctypes.byref(needed)):
            raise OSError("cannot enumerate mapped runtime modules")
        if needed.value <= ctypes.sizeof(modules):
            break
        capacity = needed.value // ctypes.sizeof(wintypes.HMODULE) + 1
    paths = set()
    for handle in modules[:needed.value // ctypes.sizeof(wintypes.HMODULE)]:
        buffer = ctypes.create_unicode_buffer(32768)
        length = filename(process, handle, buffer, len(buffer))
        if not length or length >= len(buffer):
            raise OSError("cannot resolve mapped runtime module")
        paths.add(str(Path(buffer.value).resolve(strict=True)))
    return paths


def mapped_files(*, data=False):
    if os.name == "nt":
        return set() if data else mapped_files_windows()
    if not sys.platform.startswith("linux"):
        raise ValueError("mapped runtime evidence requires Linux or Windows")
    paths, executable = set(), set()
    with open("/proc/self/maps", encoding="utf-8") as stream:
        for line in stream:
            fields = line.rstrip("\n").split(None, 5)
            if len(fields) != 6 or not fields[5].startswith("/"):
                continue
            name = fields[5]
            # A deleted mapping cannot be rehashed from its original pathname.
            if name.endswith(" (deleted)"):
                raise ValueError("mapped runtime file was deleted: " + name)
            # proc escapes newlines in pathnames with octal sequences.
            import re
            name = re.sub(r"\\([0-7]{3})", lambda m: chr(int(m[1], 8)), name)
            path = Path(name).resolve(strict=True)
            st = path.stat()
            if stat.S_ISREG(st.st_mode):
                # Refuse a replaced inode behind a still-live old mapping.
                # Overlay/bind mounts can report different device IDs through
                # stat and maps on this host; the inode still identifies the file.
                if st.st_ino != int(fields[4]):
                    raise ValueError("mapped runtime file changed: " + name)
                paths.add(str(path))
                if "x" in fields[1]:
                    executable.add(str(path))
    # A library's read-only segments belong to the same native module as its
    # executable segment. A PE parsed as data has no executable mapping.
    return paths - executable if data else executable


def input_epoch(root, *, prepare=False, outputs=None):
    """Allow compile/link outputs to settle before consuming their final bytes.

    Ledger/retail reads remain observed throughout. Only explicitly mutable
    build outputs are excluded during preparation, including Python workers.
    """
    observer = getattr(sys, "_bfme_cycle_io", None)
    if observer is None:
        return
    ignored = {str((Path(root) / "build").resolve())} if prepare else set()
    if outputs is not None:
        ignored.add(str(Path(outputs).resolve()))
    observer["ignored_inputs"] = ignored
    os.environ["BFME_CYCLE_INPUT_PREPARE"] = "1" if prepare else "0"


class InputChanged(ValueError):
    pass


def consumed_inputs(root):
    observer = getattr(sys, "_bfme_cycle_io", None)
    if observer is None:
        raise ValueError("missing opened-file audit hook")
    if "<unresolved descriptor>" in observer["read_errors"]:
        raise InputChanged("incomplete consumed input: unresolved opened descriptor")
    tops = tuple((Path(root) / name).resolve() for name in ("build", "inputs", "targets"))
    for name in observer["read_errors"]:
        path = Path(name)
        if any(path == top or path.is_relative_to(top) for top in tops):
            raise InputChanged("moved_during_run: consumed input changed or unreadable: " + name)
    result = {}
    for name, entry in tuple(observer["reads"].items()):
        path = Path(name)
        if not any(path == top or path.is_relative_to(top) for top in tops):
            continue
        try:
            same = (_generation(path.stat()) == tuple(entry["generation"])
                    and file_hash(path) == entry["sha256"])
        except (OSError, ValueError):
            same = False
        if not same or name in observer["read_errors"]:
            raise InputChanged("moved_during_run: consumed input changed: " + name)
        result[name] = entry
    return result


def observed_runtime(root, audited=None):
    """End-of-process external reads and native mappings, excluding bound inputs.

    Snapshot build objects/receipts, retail inputs and ledgers already have
    dedicated identities. The seed/export/audit directories are launcher-owned
    outputs. Everything else outside the static inventory is rule evidence.
    Observation's own hashing/listing must not recursively expand the read set.
    """
    observer = getattr(sys, "_bfme_cycle_io", None)
    if observer is None:
        raise ValueError("missing opened-file audit hook")
    started = time.monotonic()
    tid = threading.get_ident()
    observer["paused"].add(tid)
    try:
        root = Path(root).resolve()
        inputs = {(root / name).resolve() for name in ("build", "inputs", "targets")}
        snapshots = {root}
        if audited:
            audit = Path(audited).resolve()
            # The launcher has a unique workspace; the seed exports into s/.
            snapshots.update((audit.parent / "seed", audit.parent / "s"))
        _, inventory = runtime_inventory(runtime_roots(), snapshot=root)
        directories = tuple(Path(p).resolve() for p in runtime_roots() if Path(p).is_dir())

        def classification(path):
            p = Path(path)
            if audited and (p == audit or p.is_relative_to(audit)):
                return "audit-output"
            if any(p == top or p.is_relative_to(top) for top in inputs):
                return "measurement-input"
            if any(p == top or p.is_relative_to(top) for top in snapshots):
                return "snapshot"
            if path in inventory or any(p == top or p.is_relative_to(top) for top in directories):
                return "runtime-root"
            return "runtime"

        # Check input generations before excluding them from rule identity.
        observed_runtime.inputs = consumed_inputs(root)
        opened, listed, classified = {}, {}, {}
        for path, generation in tuple(observer["events"].items()):
            kind = classification(path)
            classified[kind] = classified.get(kind, 0) + 1
            if kind != "runtime":
                continue
            try:
                st = Path(path).stat()
            except FileNotFoundError:
                if generation is not None:
                    raise ValueError("opened runtime file disappeared: " + path)
                continue
            if _generation(st) != generation or path in observer["errors"]:
                raise ValueError("opened runtime file changed during measurement: " + path)
            if stat.S_ISREG(st.st_mode):
                opened[path] = file_hash(path)
            if path in observer["directories"]:
                names = sorted(os.listdir(path))
                if names != list(observer["directories"][path]):
                    raise ValueError("runtime directory changed during measurement: " + path)
                listed[path] = names
        mapped = {p: file_hash(p) for p in sorted(mapped_files())}
        for path in sorted(mapped_files(data=True)):
            kind = classification(path)
            if kind == "measurement-input":
                # mmap normally follows an observed open. Refuse an unobserved
                # data mapping rather than guessing its original generation.
                if any(path == top or path.startswith(top + os.sep) for top in observer["ignored_inputs"]):
                    continue
                if path not in observed_runtime.inputs:
                    raise InputChanged("incomplete consumed input: unobserved data mapping: " + path)
            elif kind == "runtime":
                opened[path] = file_hash(path)
        evidence = {"opened_files": dict(sorted(opened.items())), "mapped_files": mapped,
                    "directories": dict(sorted(listed.items()))}
        observed_runtime.cost = {"opened_files": len(observer["events"]),
                                 "external_opened_files": len(opened), "mapped_libs": len(mapped),
                                 "classified": classified, "seconds": time.monotonic() - started}
        return evidence
    finally:
        observer["paused"].remove(tid)


def merge_runtime_evidence(records):
    evidence = {"opened_files": {}, "mapped_files": {}, "directories": {}}
    file_digests = {}
    for record in records:
        value = record.get("runtime_evidence")
        if not isinstance(value, dict) or set(value) != set(evidence):
            raise ValueError("missing observed runtime evidence")
        for kind, entries in value.items():
            if not isinstance(entries, dict):
                raise ValueError("invalid observed runtime entries")
            for path, digest in entries.items():
                if path in evidence[kind] and evidence[kind][path] != digest:
                    raise ValueError("runtime dependency changed across subprocesses: " + path)
                evidence[kind][path] = digest
                if kind != "directories":
                    if path in file_digests and file_digests[path] != digest:
                        raise ValueError("runtime dependency changed across subprocesses: " + path)
                    file_digests[path] = digest
    return {kind: dict(sorted(entries.items())) for kind, entries in evidence.items()}


def current_runtime_evidence(evidence):
    """Rehash the recorded dependency set; never inventory unrelated host files."""
    if not isinstance(evidence, dict) or set(evidence) != {"opened_files", "mapped_files", "directories"}:
        raise ValueError("invalid observed runtime evidence")
    result = {}
    for kind, entries in evidence.items():
        if not isinstance(entries, dict):
            raise ValueError("invalid observed runtime entries")
        result[kind] = {}
        for path, value in entries.items():
            p = Path(path)
            if not p.is_absolute() or str(p.resolve(strict=True)) != path:
                raise ValueError("non-canonical runtime dependency: " + path)
            if kind == "directories":
                result[kind][path] = sorted(os.listdir(path))
            else:
                if not p.is_file() or not isinstance(value, str) or len(value) != 64:
                    raise ValueError("invalid runtime dependency: " + path)
                result[kind][path] = file_hash(path)
    return result


def clean_runtime_identity(tools):
    """Launcher preflight: independent clean process, before measurement starts."""
    source = Path(tools).resolve() / "cycle_source.py"
    program = IO_BOOTSTRAP + ("\np=sys.argv[1]; ns={'__file__':p, '__name__':'runtime_preflight'}; "
               "exec(compile(open(p,'rb').read(),p,'exec'),ns); "
               "print(ns['json'].dumps({'identity':ns['runtime_identity'](), "
               "'evidence':ns['observed_runtime'](ns['Path'](p).parent.parent)},sort_keys=True))")
    result = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", program, str(source)],
                            env=clean_environment({}), check=True, capture_output=True, text=True)
    value = json.loads(result.stdout)
    clean_runtime_identity.evidence = value["evidence"]
    return value["identity"]


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
    for name in (AUDIT_ENV, "BFME_CYCLE_EXPECTED_SEMANTIC", "LINK_CYCLE_ROOT", "GIT_CEILING_DIRECTORIES",
                 "BFME_CYCLE_INPUT_PREPARE"):
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


def audit_runtime(directory, *, roots):
    # Validate every process, including otherwise empty worker/tracker records.
    records = [json.loads(path.read_bytes()) for path in Path(directory).glob("*.json")]
    if not records:
        raise ValueError("missing observed runtime evidence")
    allowed = {str(Path(p).resolve()) for p in roots}
    for record in records:
        if record.get("tools") not in allowed:
            raise ValueError("executed module origin outside snapshot tools")
        if record.get("complete") is not True:
            raise ValueError("incomplete executed-module evidence")
    evidence = merge_runtime_evidence(records)
    if current_runtime_evidence(evidence) != evidence:
        raise ValueError("observed runtime changed after measurement")
    return evidence


def audit_inputs(directory, *, roots, receipt=None, target=None, compile_inputs=None, canonical=False):
    """Validate consumed bytes, separately from runtime/rule evidence.

    Absolute paths and stat generations stay in the ephemeral audit. Receipt
    bindings use their existing canonical hashes, so parser lifetime and unique
    snapshot paths cannot perturb the reproducible measurement identity.
    """
    allowed = {str(Path(p).resolve()) for p in roots}
    union, hashes = {}, {}
    logs = list(Path(directory).glob("*.json"))
    if not logs:
        raise ValueError("missing consumed-input evidence")
    for log in logs:
        record = json.loads(log.read_bytes())
        if record.get("tools") not in allowed or record.get("complete") is not True:
            raise ValueError("incomplete consumed-input evidence: " + str(record.get("moved_during_run") or log))
        entries = record.get("consumed_inputs")
        if not isinstance(entries, dict):
            raise ValueError("incomplete consumed-input evidence")
        root = Path(record["tools"]).parent
        for name, entry in entries.items():
            path = Path(name)
            try:
                same = (_generation(path.stat()) == tuple(entry["generation"])
                        and file_hash(path) == entry["sha256"])
            except (OSError, ValueError):
                same = False
            if not same or (name in union and union[name] != entry):
                raise ValueError("moved_during_run: consumed input changed: " + name)
            union[name] = entry
            # Resolve input roots too: build/ may be a symlink to an object
            # store, without making its bytes runtime/rule dependencies.
            relative = next(((Path(top) / path.relative_to((root / top).resolve())).as_posix()
                             for top in ("build", "inputs", "targets")
                             if path.is_relative_to((root / top).resolve())), None)
            if relative is None:
                raise ValueError("invalid consumed-input origin: " + name)
            if relative in hashes and hashes[relative] != entry["sha256"]:
                raise ValueError("moved_during_run: consumed input changed across snapshots: " + relative)
            hashes[relative] = entry["sha256"]
            if receipt is not None:
                bound = receipt.get("consumed_inputs", {}).get(relative)
                if bound is not None and entry["sha256"] != bound:
                    raise ValueError("moved_during_run: consumed input differs from receipt: " + name)
                expected = receipt.get("inputs", {}).get(relative)
                if expected is not None:
                    normalized = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
                    if normalized != expected:
                        raise ValueError("moved_during_run: consumed input differs from receipt: " + name)
                raw_expected = None
                if target is not None and relative == Path(target).as_posix():
                    raw_expected = receipt.get("retail_sha256")
                if path == Path(compile_inputs or root / "build/link_cycle/compile_inputs.json").resolve():
                    raw_expected = receipt.get("compile_inputs_sha256")
                if path.parts[-3:-1] == ("Vc7", "bin"):
                    raw_expected = receipt.get("toolchain_sha256", {}).get(path.name, raw_expected)
                if raw_expected is not None and entry["sha256"] != raw_expected:
                    raise ValueError("moved_during_run: consumed input differs from receipt: " + name)
    return dict(sorted(hashes.items())) if canonical else union


def install(tools=None, *, bootstrap_raw=None, early=None):
    if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
        raise RuntimeError("source-only snapshot requires Python -I -S -B")
    sys.dont_write_bytecode = True
    os.open = sys._bfme_cycle_descriptor_open
    tools = Path(tools or Path(__file__).parent).resolve()
    root = tools.parent
    if os.environ.get("BFME_CYCLE_INPUT_PREPARE") == "1":
        input_epoch(root, prepare=True)
    audited = os.environ.get(AUDIT_ENV)
    declared = declared_files(tools) if audited else None
    if declared:
        reject_shadows(tools, declared)
    modules = {}
    runtime_modules = {}
    identity = runtime_identity(snapshot=root)
    preloaded = tuple(sys.modules.items())
    log = Path(audited) / (uuid.uuid4().hex + ".json") if audited else None

    writer_lock = threading.RLock()
    failed = False
    completed = False
    input_failure = None

    def write(complete=False):
        nonlocal failed, completed, input_failure
        if log:
            with writer_lock:
                evidence = None
                if complete:
                    try:
                        evidence = observed_runtime(root, audited)
                    except InputChanged as error:
                        # Preserve an incomplete audit for the launcher, even
                        # when the driver itself finished normally. Never stamp
                        # a measurement whose consumed generation moved.
                        input_failure = str(error)
                        failed = True
                        write(False)
                        return
                    except BaseException:
                        failed = True
                        write(False)
                        raise
                    completed = True
                temporary = log.with_suffix(".tmp")
                temporary.write_text(json.dumps({"complete": complete and not failed, "tools": str(tools),
                                                 "modules": modules, "runtime_modules": runtime_modules,
                                                 "runtime_identity": identity,
                                                 "moved_during_run": input_failure,
                                                 "runtime_evidence": evidence,
                                                 "consumed_inputs": (getattr(observed_runtime, "inputs", None)
                                                                     if complete else None),
                                                 "runtime_cost": getattr(observed_runtime, "cost", None)}, sort_keys=True))
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
    covered_roots = tuple(Path(p).resolve() for p in runtime_roots())
    for name, module in preloaded:
        if module is None:
            continue
        spec = getattr(module, "__spec__", None)
        origin = getattr(spec, "origin", None)
        loader = getattr(spec, "loader", None)
        path = getattr(module, "__file__", None)
        if getattr(module, "__cached__", None) != getattr(spec, "cached", None):
            refuse(f"preloaded module cached path mismatch: {name}")
        if origin in ("built-in", "frozen"):
            expected = (importlib.machinery.BuiltinImporter if origin == "built-in"
                        else importlib.machinery.FrozenImporter)
            state = getattr(spec, "loader_state", None)
            frozen_path = getattr(state, "filename", None)
            # importlib.__init__ assigns the bootstrap's source hint although
            # FrozenImporter intentionally leaves loader_state.filename None.
            if origin == "frozen" and path and frozen_path is None and getattr(state, "origname", None):
                frozen_path = str(stdlib / (state.origname.replace(".", "/") + ".py"))
            if (loader is not expected or getattr(module, "__loader__", None) is not loader
                    or (origin == "built-in" and path)
                    or (origin == "frozen" and path != frozen_path)):
                refuse(f"preloaded module loader/origin mismatch: {name}")
            runtime_modules[name] = {"origin": origin + ":" + name,
                                     "sha256": identity["executable_sha256"]}
            continue
        if (name == "__main__" and spec is None and path is None
                and getattr(module, "__loader__", None) is importlib.machinery.BuiltinImporter):
            runtime_modules[name] = {"origin": "interpreter:" + name,
                                     "sha256": identity["executable_sha256"]}
            continue
        if not origin or not path or Path(path).absolute() != Path(origin).absolute():
            refuse(f"preloaded module file/spec origin mismatch: {name}")
        if getattr(module, "__loader__", None) is not loader:
            refuse(f"preloaded module loader mismatch: {name}")
        if type(loader) is zipimport.zipimporter:
            # Startup ZIPs have already executed before our import guards.
            # Bind them in preflight, but refuse them as unsupported providers;
            # never reinterpret a virtual archive member as an on-disk source.
            refuse(f"unsupported preloaded ZIP module: {name}: {loader.archive}")
        if type(loader) not in (importlib.machinery.SourceFileLoader,
                                importlib.machinery.SourcelessFileLoader,
                                importlib.machinery.ExtensionFileLoader) or loader.path != origin:
            refuse(f"preloaded module loader/origin mismatch: {name}")
        for candidate in (origin, getattr(spec, "cached", None)):
            if candidate and not any(Path(candidate).resolve() == p or
                                     Path(candidate).resolve().is_relative_to(p)
                                     for p in covered_roots):
                refuse(f"preloaded module outside runtime roots: {name}: {candidate}")
        record(origin, name, Path(origin).read_bytes())

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
        mapped_files()
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

        import atexit
        # Registered before provider callbacks, so this runs after them. A late
        # read or mutation cannot escape the completed process record.
        atexit.register(lambda: write(completed))

    return record, write, declared


# Execute this .py directly before any snapshot import, including itself.
BOOTSTRAP = IO_BOOTSTRAP + """
sys._bfme_cycle_startup_path = tuple(sys.path)
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
