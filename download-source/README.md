# Installer build inputs

These binary parts contain the unchanged existing ezuno 5.10.19 installation ZIP.
Each part is at most 48 MiB so that it can be stored as a normal Git file.
`manifest.json` records each part's size and SHA-256, plus the original ZIP's
size and SHA-256. No Git LFS or GitHub Release is needed.

The browser does not download or assemble these parts. Run:

```sh
python tools/build_site.py
```

The build verifies every part and the full SHA-256, then writes one ordinary
`_site/releases/ezuno-5.10.19-Installation-Package.zip` file. GitHub Pages serves
that file directly. The parts and this input directory are excluded from the
published artifact by the build allowlist.

For development from the repository root, restore the same file locally:

```sh
python tools/package_download.py assemble
```

The local assembled `releases/` file is ignored by Git. To recreate the inputs
from the original reviewed backup ZIP, use `tools/package_download.py split
--source PATH_TO_ORIGINAL_ZIP`; that command checks the expected full hash and
the ZIP's CRC before writing parts.
