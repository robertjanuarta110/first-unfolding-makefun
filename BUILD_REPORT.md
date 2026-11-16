# Build report — The First Unfolding

Recommended public title: **The First Unfolding**

## Artwork and authorship

An immense origami phoenix unfolds from a small paper box containing a universe. A continuous zigzag paper tail joins the creature to its source. Warm ivory and gold planes rise against a restrained deep blue field; the near wing has cooler underside folds. A tiny human raises an arm beside the box, establishing the impossible scale. A ringed planet and constellations on the box's exterior reinforce the miniature-universe idea. No text appears in the image.

All geometry, gradients, palette, lighting and texture were authored in this recorded build session, without starter source, reference entries, downloaded imagery, fonts or existing artwork. The renderer uses Pillow only at build time, with a fixed random seed and 2x supersampling. The final artwork is a real RGB PNG, not a JPEG renamed as PNG.

The first render was 578,966 bytes. A genuine source revision added a localized light pool behind the human, enlarged its silhouette and added the ringed planet. The revised image differs within bounding box (415, 724, 756, 909). In the same thumbnail region (185, 228, 203, 253), mean RGB increased from [27.03, 37.72, 45.65] to [57.56, 61.45, 58.58]. This measures local brightness, not a judgment of aesthetic quality.

## Files

- `entry.png`: final artwork, 1024 x 1024 RGB PNG, 588,717 bytes.
- `main.py`: authored stdlib runtime; validates asset size/signature and copies exact bytes to the output directory.
- `render.py`: complete original build-time renderer; requires Pillow (built with Pillow 13.0.0).
- `verify.py`: local stdlib verifier, with output artifacts under ignored `out/`.
- `LICENSE`: MIT, including `SPDX-License-Identifier: MIT`.
- `.gitignore`: excludes `out/`, Python caches and temporary files.
- `README.md`: parent-provided public metadata appeared during the build and was preserved.
- `BUILD_REPORT.md`: this report.

Runtime only needs `main.py` and `entry.png`; it imports only `os`, `pathlib` and `shutil`. It uses no network, keys, secrets, subprocesses or third-party libraries.

## Exact commands

Competition runtime, with Python 3.13:

    python3 main.py

Default target: `/output/entry.png`.

Local runtime, keeping writes in this repository:

    MAKEFUN_OUTPUT_DIR=out/manual python3 main.py

Rebuild artwork (Pillow is a build-time dependency only):

    python3 render.py

Run the local checks:

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

## Actual verification results

Final runtime test run: PASS on the installed Python 3.14.9.

- Two separate subprocess executions of the revised main.py, from a working directory other than the repository root, with `-I -S` (isolated, no site-packages), wrote to `out/run-a` and `out/different/nested/run-b`.
- Execution times: 0.0235 seconds and 0.0268 seconds, including subprocess startup; these are local measurements, not sandbox performance guarantees.
- Both outputs exactly match the source asset's SHA-256:

    d0e2d8071efd35070c3c2d0da2ef4fc84530ad469a09b976ce5c05089fda983a

- With MAKEFUN_OUTPUT_DIR absent, the runtime selected `/output`, requested directory creation and copying to `/output/entry.png`; unittest.mock redirected both filesystem mutations to `out/default-path-redirected`. The resulting copied bytes match the same hash. Nothing was written to actual `/output`.
- Python 3.13 grammar parsing passed. AST import inspection found only os, pathlib and shutil.
- PNG signature, every chunk CRC, final IEND with no trailing bytes, zlib decompression, expected scanline length (3,146,752 bytes) and every scanline filter code passed.
- Dimensions 1024 x 1024 and size 588,717 bytes satisfy the 1024px and 1,048,576-byte caps.
- ImageMagick independently identified the final asset as 8-bit sRGB PNG, 1024 x 1024.
- Thumbnail generated and measured at exactly 300 x 300: `out/thumbnail.png`.
- Rebuilding the revised artwork again produced exactly the same SHA-256.
- `git check-ignore` confirmed the thumbnail and verification JSON are ignored.
- Machine-readable latest runtime results: `out/verification.json`.

## Limits and review handoff

Python 3.13 is not installed locally. Execution was verified on 3.14.9 with 3.13 syntax parsing and long-established stdlib APIs; the actual 3.13 competition sandbox remains an external check.

Visual inspection was attempted with the available vision tool for both full image and thumbnail. Both requests returned HTTP 403 (`client_not_allowed`). No successful visual inspection is claimed. Composition follows authored coordinates, and local evaluation used Pillow/ImageMagick metadata, actual image differences and thumbnail pixel measurements. A human should open `entry.png` and `out/thumbnail.png` before publication.

The full official RULES.txt was read, including runtime constraints, judge priorities and strict transcript requirements. This build has multiple substantive assistant text turns and actual renderer revisions, plus a revised runtime entrypoint. The server alone can determine transcript acceptance and judge score; no local grade is available.

No commit, authentication, signing, remote repository creation, push or submission was performed in this build session. No credentials were inspected. The recorder was left running and its logs were not edited. Parent review, official pre-submit checks, commit with verified identity, recorder sealing, submission and later win/loss reporting remain the parent's responsibility. No claim of submission or winning is made.
