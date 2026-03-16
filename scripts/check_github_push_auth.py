#!/usr/bin/env python

import argparse
import json
import subprocess
import sys
from pathlib import Path


def repo_root():
    return Path(__file__).resolve().parent.parent


def run_git(*args):
    result = subprocess.run(
        ["git", *args],
        cwd=str(repo_root()),
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode, (result.stdout or "").strip(), (result.stderr or "").strip()


def detect_remote_info():
    code, stdout, stderr = run_git("remote", "get-url", "origin")
    if code != 0:
        raise RuntimeError(stderr or "Could not read origin remote")

    url = stdout
    is_github_https = url.startswith("https://github.com/")
    is_github_ssh = url.startswith("git@github.com:")
    ssh_url = None
    if is_github_https:
        path = url.removeprefix("https://github.com/")
        ssh_url = "git@github.com:%s" % path
    elif is_github_ssh:
        ssh_url = url

    return {
        "origin_url": url,
        "is_github_https": is_github_https,
        "is_github_ssh": is_github_ssh,
        "suggested_ssh_url": ssh_url,
    }


def detect_workflow_changes():
    code, stdout, stderr = run_git("status", "--short", "--", ".github/workflows")
    if code != 0:
        raise RuntimeError(stderr or "Could not inspect workflow changes")

    entries = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        status = line[:2]
        path = line[3:].lstrip()
        entries.append({"status": status, "path": path})
    return entries


def detect_gh():
    try:
        result = subprocess.run(
            ["gh", "--version"],
            cwd=str(repo_root()),
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return False
    return result.returncode == 0


def render_text(report):
    remote = report["remote"]
    workflow_changes = report["workflow_changes"]

    print("GitHub Push Auth Report")
    print("  origin: %s" % remote["origin_url"])
    print("  remote_mode: %s" % report["remote_mode"])
    print("  gh_cli_available: %s" % ("yes" if report["gh_cli_available"] else "no"))
    print("Workflow changes")
    if workflow_changes:
        for entry in workflow_changes:
            print("  %s %s" % (entry["status"], entry["path"]))
    else:
        print("  none")

    print("Recommendation")
    if remote["is_github_https"]:
        print("  Current remote uses HTTPS.")
        print("  If you need to push .github/workflows/* changes, prefer one of these paths:")
        print("  1. Switch this repo to SSH authentication")
        if remote["suggested_ssh_url"]:
            print("     git remote set-url origin %s" % remote["suggested_ssh_url"])
        print("  2. Use a classic Personal Access Token with repo + workflow scope")
    elif remote["is_github_ssh"]:
        print("  Current remote already uses SSH.")
        print("  If workflow pushes still fail, test your SSH authentication with:")
        print("     ssh -T git@github.com")
    else:
        print("  Remote is not a standard github.com HTTPS/SSH URL. Inspect repository auth manually.")

    if workflow_changes:
        print("Why this matters")
        print("  GitHub treats pushes that create or modify .github/workflows/* as higher-privilege operations.")
        print("  A token without workflow-related permission can still push code, but the workflow file update is rejected.")

    print("Suggested next manual steps")
    print("  - Run this helper before pushing workflow changes")
    print("  - If using HTTPS, either switch to SSH or refresh the token before retrying")
    print("  - After auth is fixed, rerun: git push origin %s" % report["current_branch"])


def main():
    parser = argparse.ArgumentParser(
        description="Inspect the current GitHub remote mode and explain how to unblock workflow-file pushes."
    )
    parser.add_argument("--json", action="store_true", help="Print the report as JSON")
    args = parser.parse_args()

    code, branch, stderr = run_git("branch", "--show-current")
    if code != 0:
        raise SystemExit(stderr or "Could not determine current branch")

    report = {
        "current_branch": branch,
        "remote": detect_remote_info(),
        "workflow_changes": detect_workflow_changes(),
        "gh_cli_available": detect_gh(),
    }
    report["remote_mode"] = (
        "github_https"
        if report["remote"]["is_github_https"]
        else "github_ssh"
        if report["remote"]["is_github_ssh"]
        else "other"
    )

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        render_text(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
