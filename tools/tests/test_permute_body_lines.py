#!/usr/bin/env python3
"""tools/permute.py body_lines/focus_of: brace-counting body detection."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import permute  # noqa: E402


def picked(source, symbol=None, focus=None):
    lines = source.split("\n")
    focus = focus or permute.focus_of(symbol)
    return [lines[i].strip() for i in permute.body_lines(lines, focus)]


def test_column_zero_definition():
    src = "int Foo::bar(int x)\n{\n    int y = x + 1;\n    return y;\n}\n"
    assert picked(src, "?bar@Foo@@QAEHH@Z") == ["int y = x + 1;", "return y;"]


def test_indented_definition():
    src = "namespace n {\n  int Foo::bar(int x)\n  {\n    return x * 2;\n  }\n}\n"
    assert picked(src, "?bar@Foo@@QAEHH@Z") == ["return x * 2;"]


def test_one_line_definition():
    src = "int Foo::bar(int x) { return x - 1; }\nint other() { return 0; }\n"
    assert picked(src, "?bar@Foo@@QAEHH@Z") == ["int Foo::bar(int x) { return x - 1; }"]


def test_brace_statement_line_is_a_statement():
    src = "void Foo::bar()\n{\n    { Item i; i.go(); }\n}\n"
    assert picked(src, "?bar@Foo@@QAEXXZ") == ["{ Item i; i.go(); }"]


def test_constructor_initializer_list():
    src = ("Foo::Foo(int a, int b)\n    : m_a(a),\n      m_b(b + 1)\n{\n    m_c = 0;\n}\n"
           "void Foo::run()\n{\n    m_c = 5;\n}\n")
    assert permute.focus_of("??0Foo@@QAE@HH@Z") is not None
    assert picked(src, "??0Foo@@QAE@HH@Z") == [": m_a(a),", "m_b(b + 1)", "m_c = 0;"]


def test_destructor_focus_picks_destructor_only():
    src = "Foo::Foo()\n{\n    m_a = 1;\n}\nFoo::~Foo()\n{\n    m_a = 2;\n}\n"
    assert picked(src, "??0Foo@@QAE@XZ") == ["m_a = 1;"]
    assert picked(src, "??1Foo@@UAE@XZ") == ["m_a = 2;"]


def test_multi_function_file_picks_target_not_first_or_last():
    src = ("static int helper(int v)\n{\n    return v;\n}\n"
           "int Foo::target(int v)\n{\n    int t = helper(v);\n    return t;\n}\n"
           "int Foo::later(int v)\n{\n    return v + 9;\n}\n")
    assert picked(src, "?target@Foo@@QAEHH@Z") == ["int t = helper(v);", "return t;"]


def test_call_statement_and_declaration_are_not_definitions():
    src = ("int Foo::bar(int);\nint g = compute(3);\n"
           "int Foo::bar(int x)\n{\n    return Foo::baz(x);\n}\n")
    assert picked(src, "?bar@Foo@@QAEHH@Z") == ["return Foo::baz(x);"]


def test_macro_continuation_is_not_a_definition():
    src = ("#define REC(x) \\\n  track(x); \\\n  note(x)\n"
           "void GameEngine::run()\n{\n    step();\n}\n")
    assert picked(src, "?run@GameEngine@@QAEXXZ") == ["step();"]


def test_split_signature_and_nested_braces():
    src = ("void Foo::bar(int a,\n              int b) const\n{\n    if (a) {\n        b++;\n    }\n"
           "    while (b) { b--; }\n}\n")
    assert picked(src, "?bar@Foo@@QBEXHH@Z") == ["if (a) {", "b++;", "while (b) { b--; }"]


def test_without_focus_every_body():
    src = "int a() { return 1; }\nint b()\n{\n    return 2;\n}\n"
    lines = src.split("\n")
    assert [lines[i].strip() for i in permute.body_lines(lines)] == ["int a() { return 1; }", "return 2;"]


def test_missing_target_falls_back_to_every_body():
    src = "int a()\n{\n    return 1;\n}\n"
    assert picked(src, "?nope@Foo@@QAEHXZ") == ["return 1;"]


def test_return_type_of_indented_and_one_line_definitions():
    src = ("namespace n {\n  int Foo::bar(int x)\n  {\n    return x * 2;\n  }\n}\n"
           "float baz() { return 1.5f * 2.0f; }\n"
           "void Foo::none()\n{\n    return;\n}\n")
    lines = src.split("\n")
    assert permute._return_type(lines, 3) == "int"
    assert permute._return_type(lines, 6) == "float"
    assert permute._return_type(lines, 9) is None
