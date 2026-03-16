#!/usr/bin/env python

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ELF_MAGIC = b"\x7fELF"
MACHO_MAGICS = {
    b"\xfe\xed\xfa\xce",
    b"\xce\xfa\xed\xfe",
    b"\xfe\xed\xfa\xcf",
    b"\xcf\xfa\xed\xfe",
    b"\xca\xfe\xba\xbe",
    b"\xbe\xba\xfe\xca",
}


def repo_root():
    return Path(__file__).resolve().parent.parent


def read_magic(path):
    try:
        with open(path, "rb") as handle:
            return handle.read(4)
    except OSError:
        return b""


def unix_binary_compatible(path):
    magic = read_magic(path)
    if magic.startswith(b"#!"):
        return True
    if sys.platform == "darwin":
        return magic in MACHO_MAGICS
    if sys.platform.startswith("linux"):
        return magic == ELF_MAGIC
    return True


def is_compatible_executable(path):
    if not path or not os.path.isfile(path):
        return False
    if sys.platform == "win32":
        return os.path.splitext(path)[1].lower() in {".exe", ".bat", ".cmd"}
    return os.access(path, os.X_OK) and unix_binary_compatible(path)


def locate_executable(name):
    path_match = shutil.which(name)
    if is_compatible_executable(path_match):
        return path_match

    repo_bin = repo_root() / "bin"
    cwd_bin = Path.cwd() / "bin"
    candidates = []
    if sys.platform == "win32" and Path(name).suffix == "":
        candidates = [name + ".exe", name + ".bat", name + ".cmd"]
    else:
        candidates = [name]

    for bin_dir in (repo_bin, cwd_bin):
        for candidate_name in candidates:
            candidate = bin_dir / candidate_name
            if is_compatible_executable(str(candidate)):
                return str(candidate)
    return None


def get_module_version(module_name):
    code = """
import importlib, json, sys
name = sys.argv[1]
try:
    module = importlib.import_module(name)
    version = getattr(module, "__version__", None)
    if version is None and name == "libsbml":
        version = getattr(module, "getLibSBMLDottedVersion", lambda: None)()
    print(json.dumps({"ok": True, "version": version}))
except Exception as exc:
    print(json.dumps({"ok": False, "error": str(exc)}))
"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code, module_name],
            text=True,
            capture_output=True,
            check=False,
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

    stdout = (result.stdout or "").strip()
    if stdout:
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            pass

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        return {"ok": False, "error": stderr or "subprocess import failed with exit code %s" % result.returncode}

    return {"ok": False, "error": "subprocess import returned no output"}


def get_executable_info(executable_name):
    located = locate_executable(executable_name)
    return {
        "ok": bool(located),
        "path": located,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Inspect the runtime stack used by GMSM and optionally fail on missing components."
    )
    parser.add_argument("--json", action="store_true", help="Print the report as JSON")
    parser.add_argument(
        "--require-executable",
        action="append",
        default=[],
        help="Executable name that must resolve successfully (repeatable)",
    )
    parser.add_argument(
        "--require-module",
        action="append",
        default=[],
        help="Python module that must import successfully (repeatable)",
    )
    args = parser.parse_args()

    modules = ["cobra", "optlang", "Bio", "libsbml", "swiglpk"]
    report = {
        "platform": {
            "system": platform.system(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
        },
        "modules": {name: get_module_version(name) for name in modules},
        "executables": {
            "diamond": get_executable_info("diamond"),
            "skani": get_executable_info("skani"),
        },
    }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Platform")
        print("  system: %s" % report["platform"]["system"])
        print("  machine: %s" % report["platform"]["machine"])
        print("  python: %s" % report["platform"]["python"])
        print("Modules")
        for name, info in report["modules"].items():
            if info["ok"]:
                print("  %s: %s" % (name, info["version"]))
            else:
                print("  %s: ERROR %s" % (name, info["error"]))
        print("Executables")
        for name, info in report["executables"].items():
            if info["ok"]:
                print("  %s: %s" % (name, info["path"]))
            else:
                print("  %s: not found" % name)

    failures = []
    for executable_name in args.require_executable:
        if not report["executables"].get(executable_name, {}).get("ok"):
            failures.append("Missing executable: %s" % executable_name)
    for module_name in args.require_module:
        if not report["modules"].get(module_name, {}).get("ok"):
            failures.append("Missing module: %s" % module_name)

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
