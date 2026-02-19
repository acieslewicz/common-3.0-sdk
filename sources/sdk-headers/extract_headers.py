#!/usr/bin/env python

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, TypedDict

import pygit2
import yaml


class SourceMapping(TypedDict):
    source: str
    dest: str


class RepoConfig(TypedDict):
    repo_url: str
    sources: Dict[str, List[SourceMapping]]


class HeaderExtractor:
    def __init__(self, config_path: str | Path, output_dir: str | Path):
        self.output_dir: Path = Path(output_dir)
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.repos_dir = Path("repos")
        self.repos_dir.mkdir(exist_ok=True)

        with open(config_path, "r", encoding="utf-8") as f:
            self.sources: Dict[str, RepoConfig] = yaml.safe_load(f)

    def get_repository(self, name: str, repo_info: RepoConfig) -> pygit2.Repository:
        repo_path = self.repos_dir / name
        if repo := pygit2.discover_repository(repo_path):
            logging.info("Using existing repository at %s", repo_path)
            return pygit2.Repository(repo)

        logging.info("Cloning %s from %s", name, repo_info["repo_url"])
        return pygit2.clone_repository(repo_info["repo_url"], repo_path)

    def checkout_tag(self, repo: pygit2.Repository, tag_name: str) -> None:
        reference = repo.lookup_reference_dwim(tag_name)
        logging.info("Checking out %s for %s", reference.name, repo.path)
        repo.checkout(reference)

    def extract_headers(self) -> None:
        for name, config in self.sources.items():
            repo = self.get_repository(name, config)
            for tag, sources in config["sources"].items():
                logging.info("Processing %s %s", name, tag)
                self.checkout_tag(repo, tag)
                for file_info in sources:
                    source_path = self.repos_dir / name / file_info["source"]
                    dest_path = self.output_dir / file_info["dest"]

                    if not source_path.exists():
                        logging.warning("Source not found: %s", source_path)
                        return

                    if source_path.is_file():
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_path, dest_path)
                        logging.info("Copied file: %s to %s", source_path, dest_path)
                    else:
                        dest_path.mkdir(parents=True, exist_ok=True)
                        for file in source_path.glob("*.h"):
                            final_dest_path = dest_path / file.name
                            shutil.copy2(file, final_dest_path)
                            logging.info("Copied file: %s to %s", file, final_dest_path)


def apply_patches(
    target_dir: Path | str, patches_dir: Path | str, strip_level: int = 1
) -> None:
    patches_dir = Path(patches_dir)
    target_dir = Path(target_dir)

    if not patches_dir.exists():
        logging.info("No patches directory found")
        return

    patches = sorted(patches_dir.glob("*.patch"))
    if not patches:
        logging.info("No .patch files found in patches directory")
        return

    logging.info("Applying %d patche(s)...", len(patches))

    for patch in patches:
        result = subprocess.run(
            [
                "patch",
                f"-p{strip_level}",
                "-d",
                str(target_dir),
                "-i",
                str(patch.absolute()),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            logging.info("Successfully applied patch: %s", patch.name)
        else:
            logging.error("Failed to apply patch %s: %s", patch.name, result.stderr)
            # Try to reverse failed patch
            subprocess.run(
                [
                    "patch",
                    "-R",
                    f"-p{strip_level}",
                    "-d",
                    str(target_dir),
                    "-i",
                    str(patch.absolute()),
                ],
                capture_output=True,
                check=False,
            )


def main():
    parser = argparse.ArgumentParser(
        description="Extract iOS 3.0 SDK headers from source repositories"
    )
    parser.add_argument(
        "--config",
        default="header_sources.yaml",
        help="Path to YAML header configuration file",
    )
    parser.add_argument(
        "--output", default="extracted_headers", help="Output directory for extracted headers"
    )
    parser.add_argument(
        "--patches", default="patches", help="Directory containing patches to apply"
    )
    args = parser.parse_args()

    extractor = HeaderExtractor(args.config, args.output)
    extractor.extract_headers()

    apply_patches(args.output, args.patches)


if __name__ == "__main__":
    main()
