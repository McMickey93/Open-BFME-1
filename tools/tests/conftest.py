"""Hermetic Python installations for the cycle provenance tests.

The production inventory binds entire prefixes and refuses unreadable files.
A system prefix such as /usr includes root-only files on some development
hosts. Tests use a disposable installation, never weaken that inventory.
"""
import os
import sys
from pathlib import Path

import pytest


CYCLE_TESTS = {
    *(f"test_bfme2_port_r{i}_regressions" for i in range(1, 7)),
    "test_cycle_artifacts", "test_publish_cycle", "test_cycle_diff", "test_data_back_rank",
    "test_closure_report", "test_link_cycle_identity", "test_link_cycle",
    "test_link_cycle_currency", "test_repair_queue", "test_repair_queue_link",
    "test_census_receipts", "test_link_census_currency",
}


@pytest.fixture(scope="session")
def cycle_python_installation(tmp_path_factory):
    from test_bfme2_port_r5_regressions import private_python
    return private_python(tmp_path_factory.mktemp("cycle-runtime"))


@pytest.fixture(autouse=True)
def hermetic_cycle_python(request, monkeypatch):
    if os.name == "nt" or Path(request.node.path).stem not in CYCLE_TESTS:
        yield
        return
    import cycle_source as cs
    py, stdlib = request.getfixturevalue("cycle_python_installation")
    for name in ("executable", "_base_executable"):
        monkeypatch.setattr(sys, name, str(py))
    for name in ("prefix", "base_prefix", "exec_prefix", "base_exec_prefix"):
        monkeypatch.setattr(sys, name, str(py.parent.parent))
    get_path = cs.sysconfig.get_path
    monkeypatch.setattr(cs.sysconfig, "get_path",
                        lambda name, *a, **kw: str(stdlib) if name == "stdlib" else get_path(name, *a, **kw))
    monkeypatch.setattr(cs, "_INTERPRETER", str(py))
    search_path = cs.isolated_search_path
    search_path.cache_clear()
    search_path()  # Discover before individual tests stub subprocess.run.
    yield
    search_path.cache_clear()
