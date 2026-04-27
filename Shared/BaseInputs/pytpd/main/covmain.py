#!/usr/intel/pkgs/python3/3.12.3/bin/python3

"""Coverage.py's main entry point."""

import os
import sys

def _abspath_from_cwd(path_str, repo_root):
    # Resolve a path relative to the given cwd, and normalize it.
    if os.path.isabs(path_str):
        return os.path.realpath(path_str)
    return os.path.realpath(os.path.join(repo_root, path_str))


def _collect_py_parents(args, repo_root):
    """
    From the arguments forwarded to coverage, collect parent directories of any
    existing *.py file paths. Deduplicate while preserving a stable order.
    """
    parents: list[str] = []
    seen: set[str] = set()

    # We scan all args for *.py paths. This also works with '--' where script args
    # may follow, because we only pick existing *.py files.
    for a in args:
        # Skip obvious options (starting with '-') to avoid treating flags like "-m" as paths.
        if a.startswith("-"):
            continue

        p = _abspath_from_cwd(a, repo_root)

        # If it's an existing .py file, collect its parent directory.
        if os.path.isfile(p) and p.endswith(".py"):
            parent_dir = os.path.dirname(p)
            if parent_dir not in seen:
                seen.add(parent_dir)
                parents.append(parent_dir)

    return parents


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    cov_root = os.path.join(os.path.dirname(repo_root), "pytpd-unittest", "coveragepy")

    if not os.path.exists(cov_root):
        print(f"coveragepy root not found: {cov_root}", file=sys.stderr)
        return 2

    # Ensure our coveragepy is imported first.
    if cov_root not in sys.path:
        sys.path.insert(0, cov_root)

    # coverage CLI entrypoint.
    from coverage.cmdline import main as coverage_main

    # Forward all arguments after covmain.py to coverage verbatim.
    cov_args = sys.argv[1:]

    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    # Ensure parent directories of referenced .py files are on sys.path
    #    so same-directory imports like `from setenv import ...` work.
    # Insert these before repo_root to give them higher priority.
    py_parents = _collect_py_parents(cov_args, repo_root)
    for parent_dir in reversed(py_parents):
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

    # Run coverage with the forwarded arguments.
    return coverage_main(cov_args)


if __name__ == "__main__":
    raise SystemExit(main())
