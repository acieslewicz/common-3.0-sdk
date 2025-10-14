#!/usr/bin/env python3

import argparse

from collections import defaultdict

from pathlib import Path

from typing import Dict, List


def generate_stub(input_files: List[Path | str], output_dir: Path | str) -> None:
    input_files, output_dir = [Path(file) for file in input_files], Path(output_dir)

    source_files: Dict[Path, List[str]] = defaultdict(list)
    for input_file in input_files:
        with open(input_file, "r", encoding="utf-8") as f:
            source_path: None | Path = None
            in_body: bool = False
            for line in f:
                if line.startswith("//"):
                    if not source_path or in_body:
                        source_path = Path(line.strip("/").strip())
                        in_body = False
                    # Ignore non canonical paths
                elif not source_path:
                    print(
                        f"WARN: Missing source path for line ({line.strip()}) found in ({input_file})."
                    )
                else:
                    in_body = True
                    if line in source_files[source_path] and "@end" not in line:
                        print(
                            f"WARN: Duplicate line ({line.strip()}) found for {source_path} in {input_file}."
                        )
                    source_files[source_path].append(line)

    for source_path, source in source_files.items():
        if "touchHLE" in str(source_path):
            # Skip touchHLE internal classes
            continue

        with open(output_dir / f"{source_path.name}.m", "w", encoding="utf-8") as f:
            f.writelines(source)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse touchHLE style symbol dumps into their corresponding source files."
    )
    parser.add_argument(
        "symbol_lists",
        help="A set of files used to generate the final sources.",
        type=Path,
        nargs="+",
    )
    parser.add_argument(
        "--output_dir", help="The output dir.", default=Path("."), type=Path
    )
    args = parser.parse_args()
    generate_stub(args.symbol_lists, args.output_dir)


if __name__ == "__main__":
    main()
