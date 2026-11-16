"""Run local verification; test artifacts stay under the ignored out/ folder."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time
import zlib
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_png(path):
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    offset, names, idat = 8, [], bytearray()
    width = height = 0
    while offset < len(data):
        length = struct.unpack_from(">I", data, offset)[0]
        kind = data[offset + 4:offset + 8]
        body = data[offset + 8:offset + 8 + length]
        crc = struct.unpack_from(">I", data, offset + 8 + length)[0]
        assert zlib.crc32(kind + body) & 0xffffffff == crc
        names.append(kind.decode("ascii"))
        if kind == b"IHDR":
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", body)
            assert (depth, color, compression, filtering, interlace) == (8, 2, 0, 0, 0)
        if kind == b"IDAT":
            idat.extend(body)
        offset += length + 12
        if kind == b"IEND":
            assert length == 0 and offset == len(data)
            break
    assert names[0] == "IHDR" and names[-1] == "IEND"
    raw = zlib.decompress(idat)
    assert len(raw) == height * (1 + width * 3)
    assert all(raw[row * (1 + width * 3)] <= 4 for row in range(height))
    assert 0 < width <= 1024 and 0 < height <= 1024
    assert len(data) <= 1048576
    return {"format": "PNG", "dimensions": [width, height], "bytes": len(data),
            "chunks": names, "crc_checks": "all passed", "decompressed_scanline_bytes": len(raw)}


def main():
    tree = ast.parse((ROOT / "main.py").read_text(), feature_version=(3, 13))
    imports = [node.module if isinstance(node, ast.ImportFrom) else alias.name
               for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
               for alias in node.names]
    assert set(imports) == {"os", "pathlib", "shutil"}
    report = {"python": sys.version.split()[0], "python_313_grammar": "PASS",
              "runtime_imports": imports, "image": verify_png(ROOT / "entry.png")}
    source_hash = digest(ROOT / "entry.png")
    runs = []
    for name in ["run-a", "different/nested/run-b"]:
        dest = OUT / name
        env = dict(os.environ, MAKEFUN_OUTPUT_DIR=str(dest), PYTHONDONTWRITEBYTECODE="1")
        start = time.perf_counter()
        result = subprocess.run([sys.executable, "-I", "-S", str(ROOT / "main.py")],
                                cwd=OUT, env=env, check=True, capture_output=True, text=True)
        assert result.stdout == result.stderr == ""
        actual = digest(dest / "entry.png")
        assert actual == source_hash
        runs.append({"directory": str(dest.relative_to(ROOT)), "sha256": actual,
                     "seconds": round(time.perf_counter() - start, 4)})
    report["runtime_runs"] = runs
    spec = importlib.util.spec_from_file_location("entry_runtime", ROOT / "main.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    default_dest = OUT / "default-path-redirected"
    default_dest.mkdir(exist_ok=True)
    mkdir_calls, copy_calls = [], []
    real_copy = module.shutil.copyfile

    def redirect_mkdir(path, *args, **kwargs):
        assert path == Path("/output")
        mkdir_calls.append(str(path))
        assert kwargs == {"parents": True, "exist_ok": True}

    def redirect_copy(source, target):
        assert target == Path("/output/entry.png")
        assert source == ROOT / "entry.png"
        copy_calls.append(str(target))
        return real_copy(source, default_dest / "entry.png")

    with patch.dict(os.environ, {}, clear=True):
        assert module.output_directory() == Path("/output")
        with patch.object(Path, "mkdir", redirect_mkdir), patch.object(module.shutil, "copyfile", redirect_copy):
            module.main()
    assert mkdir_calls == ["/output"] and copy_calls == ["/output/entry.png"]
    assert digest(default_dest / "entry.png") == source_hash
    report["default_path"] = {"selected": "/output", "requested_copy": copy_calls[0],
                              "actual_write": str(default_dest.relative_to(ROOT)),
                              "sha256": source_hash, "method": "filesystem writes redirected with unittest.mock"}
    report["asset_sha256"] = source_hash
    report["result"] = "PASS"
    (OUT / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
