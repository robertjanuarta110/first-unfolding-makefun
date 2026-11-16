"""Deliver the original static artwork using only the Python standard library."""
import os
from pathlib import Path
import shutil


def output_directory():
    return Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main():
    source = Path(__file__).resolve().with_name("entry.png")
    if not 0 < source.stat().st_size <= 1_048_576:
        raise ValueError("Artwork must be nonempty and no larger than 1 MiB")
    with source.open("rb") as stream:
        if stream.read(8) != b"\x89PNG\r\n\x1a\n":
            raise ValueError("Artwork must have the expected PNG signature")
    destination = output_directory()
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination / "entry.png")


if __name__ == "__main__":
    main()
