"""Build a reproducible Decky ZIP and its complete corresponding source bundle."""

import gzip
import io
import json
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from scripts.build_common import EPOCH, ROOT, digest, fetch, files, lock, write
from scripts.sanitize import check


def vendor_archive(wheel: Path, stage: Path) -> None:
    count = 0
    license_found = False
    with zipfile.ZipFile(wheel) as archive:
        for member in archive.infolist():
            relative = PurePosixPath(member.filename)
            if (
                len(relative.parts) == 2
                and relative.parts[0] == "libarchive"
                and relative.suffix == ".py"
            ):
                write(stage / "py_modules" / relative.as_posix(), archive.read(member))
                count += 1
            elif member.filename == "libarchive_c-5.3.dist-info/licenses/LICENSE.md":
                write(stage / "licenses/libarchive-c-LICENSE", archive.read(member))
                license_found = True
    if count < 4 or not license_found:
        raise ValueError("Unreviewed libarchive-c wheel layout")


def frontend_modules() -> dict[str, Path]:
    dependencies = json.loads((ROOT / "package.json").read_text())["dependencies"]
    result = {}
    for name, package in {
        "decky-api": "@decky/api",
        "react-icons": "react-icons",
        "tslib": "tslib",
    }.items():
        directory = (ROOT / "node_modules" / package).resolve(strict=True)
        installed = json.loads((directory / "package.json").read_text())
        if installed["version"] != dependencies[package]:
            raise ValueError("Frontend dependency differs from lock")
        result[name] = directory
    return result


def stage_plugin(stage: Path, wheel: Path) -> None:
    required = (
        "dist/index.js",
        "main.py",
        "plugin.json",
        "package.json",
        "LICENSE",
        "THIRD_PARTY_NOTICES.md",
        "README.md",
        "data/games.json",
        "data/install_guides.json",
        "data/dependencies.json",
        "assets/update-allowed-signers",
    )
    for relative in required:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing/unsafe input: {relative}")
        write(stage / relative, path.read_bytes())
    for directory in ("py_modules", "docs"):
        for path in files(ROOT / directory):
            if path.suffix in {".py", ".md"}:
                write(stage / path.relative_to(ROOT), path.read_bytes())
    for name, directory in frontend_modules().items():
        license_name = "LICENSE.txt" if name == "tslib" else "LICENSE"
        write(stage / "licenses" / f"{name}-LICENSE", (directory / license_name).read_bytes())
    # A source map can embed host paths and is unnecessary for plugin execution.
    vendor_archive(wheel, stage)


def build_zip(stage: Path, target: Path) -> None:
    temporary = target.with_suffix(".zip.tmp")
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in files(stage):
                info = zipfile.ZipInfo("DeckyMods/" + path.relative_to(stage).as_posix(), EPOCH)
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)


def source_files() -> list[tuple[Path, str]]:
    result = []
    for directory in ("src", "py_modules", "scripts", "data", "docs", "tests", "assets", ".github"):
        result.extend(
            (p, "DeckyMods/" + p.relative_to(ROOT).as_posix()) for p in files(ROOT / directory)
        )
    for name in (
        "main.py",
        "plugin.json",
        "package.json",
        "pnpm-lock.yaml",
        "pyproject.toml",
        "requirements-dev.txt",
        "requirements.txt",
        "rollup.config.mjs",
        "tsconfig.json",
        "vitest.config.ts",
        ".gitignore",
        "LICENSE",
        "README.md",
        "THIRD_PARTY_NOTICES.md",
    ):
        result.append((ROOT / name, "DeckyMods/" + name))
    for name, directory in frontend_modules().items():
        for path in files(directory):
            relative = path.relative_to(directory)
            if (
                name == "react-icons"
                and len(relative.parts) > 1
                and relative.parts[0] not in {"fa", "lib"}
            ):
                continue
            result.append((path, f"DeckyMods/third_party/frontend/{name}/{relative.as_posix()}"))
    return result


def build_source(target: Path, upstream: list[Path]) -> None:
    temporary = target.with_suffix(".tmp")
    try:
        with temporary.open("wb") as output:
            with gzip.GzipFile(filename="", fileobj=output, mode="wb", mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w") as archive:
                    entries = source_files() + [
                        (p, "DeckyMods/third_party/" + p.name) for p in upstream
                    ]
                    for path, name in sorted(entries, key=lambda item: item[1]):
                        if path.is_symlink():
                            raise ValueError("Source input is a link")
                        payload = path.read_bytes()
                        info = tarfile.TarInfo(name)
                        info.size, info.mode, info.mtime = len(payload), 0o644, 0
                        archive.addfile(info, io.BytesIO(payload))
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    version = json.loads((ROOT / "package.json").read_text())["version"]
    if not isinstance(version, str) or not all(char in "0123456789.-" for char in version):
        raise ValueError("Invalid release version")
    spec = lock()["libarchive-c"]
    wheel, upstream_source = fetch(spec), fetch(spec, source=True)
    release = ROOT / "release"
    release.mkdir(exist_ok=True)
    plugin = release / f"DeckyMods-v{version}.zip"
    source = release / f"DeckyMods-v{version}-source.tar.gz"
    with tempfile.TemporaryDirectory(prefix="deckymods-release-") as temporary:
        stage = Path(temporary)
        stage_plugin(stage, wheel)
        build_zip(stage, plugin)
    build_source(source, [wheel, upstream_source])
    for path in (plugin, source):
        check(path)
    write(
        release / "SHA256SUMS",
        "".join(f"{digest(p)}  {p.name}\n" for p in (plugin, source)).encode(),
    )
    print(f"Created {plugin.name} and matching source; privacy checks passed")


if __name__ == "__main__":
    main()
