#!/usr/bin/env python3
"""Run the ATLAS Open Data H->gammagamma analysis with TaskVine.

Run download_data.py first, or pass local ROOT files with --input-file.
"""

import argparse
import json
import time
from pathlib import Path

import ndcctools.taskvine as vine

from hyy_analysis import (
    BIN_EDGES,
    merge_results,
    process_file,
)


def process_file_task(url):
    try:
        return {
            "status": "success",
            "result": process_file(url),
        }
    except BaseException as exc:
        return {
            "status": "failed",
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }


def run_taskvine(args):
    if args.input_file:
        files = [str(path.resolve()) for path in args.input_file]
    else:
        files = [str(path.resolve()) for path in sorted(args.data_dir.glob("*.root"))]
    missing = [path for path in files if not Path(path).is_file()]
    if missing:
        raise FileNotFoundError(f"missing input files: {missing}")
    if not files:
        raise FileNotFoundError(f"no ROOT files in {args.data_dir}; run download_data.py")

    args.output.parent.mkdir(parents=True, exist_ok=True)

    manager = vine.Manager(args.port)
    print(f"manager listening on port {manager.port}", flush=True)
    analysis_file = manager.declare_file(
        str(Path(__file__).with_name("hyy_analysis.py")), cache=True
    )

    submitted = []
    start_time = time.time()
    for file_index, url in enumerate(files):
        task = vine.PythonTask(process_file_task, url)
        task.add_input(analysis_file, "hyy_analysis.py")
        task.set_cores(1)
        task.set_tag(f"hyy-file-{file_index:02d}")
        manager.submit(task)
        submitted.append((task, file_index, url))

    results = {}
    while not manager.empty():
        task = manager.wait(60)
        if task is not None:
            results[task.tag] = task.output

    failed = [
        {
            "tag": task.tag,
            "file_index": file_index,
            "url": url,
            "result": results.get(task.tag),
        }
        for task, file_index, url in submitted
        if not isinstance(results.get(task.tag), dict)
        or results[task.tag].get("status") != "success"
    ]
    elapsed = time.time() - start_time
    if failed:
        diagnostic = {
            "tasks": len(submitted),
            "failed_tasks": failed,
            "elapsed_seconds": elapsed,
        }
        args.output.write_text(json.dumps(diagnostic, indent=2, default=str))
        raise RuntimeError(
            f"{len(failed)} of {len(submitted)} tasks failed; see {args.output}"
        )

    partials = [results[task.tag]["result"] for task, *_ in submitted]
    merged = merge_results(partials)
    output = {
        key: value.tolist() if hasattr(value, "tolist") else value
        for key, value in merged.items()
    }
    output.update(
        {
            "files": files,
            "elapsed_seconds": elapsed,
            "bin_edges": BIN_EDGES.tolist(),
            "tasks": len(submitted),
            "manager_port": manager.port,
        }
    )
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(
        json.dumps(
            {
                "status": "completed",
                "tasks": len(submitted),
                "entries": merged["entries"],
                "selected": merged["selected"],
                "elapsed_seconds": elapsed,
                "output": str(args.output.resolve()),
            }
        )
    )


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("hyy-results.json"))
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--port", type=int, default=9123)
    parser.add_argument(
        "--input-file",
        type=Path,
        action="append",
        default=[],
        help="local ROOT input; repeat for multiple files (default: data/*.root)",
    )
    return parser


def main():
    args = build_parser().parse_args()
    run_taskvine(args)


if __name__ == "__main__":
    main()
