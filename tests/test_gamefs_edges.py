"""Descriptor confinement regressions with swapped roots and symbolic links."""

import io
from pathlib import Path

import decky_mods.deployment as deployment
import decky_mods.gamefs as gamefs
import pytest
from decky_mods.deployment import Deployment
from decky_mods.errors import ModsError
from decky_mods.gamefs import GameFiles, fingerprint
from decky_mods.objects import Objects


@pytest.fixture
def filesystem(tmp_path):
    library = tmp_path / "library"
    root = library / "game"
    root.mkdir(parents=True)
    (root / "data").mkdir()
    (root / "data/original.bin").write_bytes(b"vanilla")
    game = {"id": "secure-game", "path": str(root), "build_id": "1", "running": False}
    objects = Objects(tmp_path / "objects")
    before, _ = objects.put(io.BytesIO(b"vanilla"))
    after, _ = objects.put(io.BytesIO(b"mod"))
    return game, objects, before, after


@pytest.mark.parametrize("replacement", ["symlink-ancestor", "new-root"])
def test_apply_rejects_replaced_game_root_after_initial_fingerprint(
    filesystem, tmp_path, replacement
):
    game, objects, before, after = filesystem
    files = GameFiles(game, objects)
    root = Path(game["path"])
    if replacement == "symlink-ancestor":
        library = root.parent
        saved = tmp_path / "library-original"
        library.rename(saved)
        outside = tmp_path / "outside"
        (outside / "game/data").mkdir(parents=True)
        (outside / "game/data/original.bin").write_bytes(b"vanilla")
        library.symlink_to(outside, target_is_directory=True)
        unexpected_target = outside / "game/data/original.bin"
        original_target = saved / "game/data/original.bin"
    else:
        saved = root.with_name("game-original")
        root.rename(saved)
        (root / "data").mkdir(parents=True)
        (root / "data/original.bin").write_bytes(b"vanilla")
        unexpected_target = root / "data/original.bin"
        original_target = saved / "data/original.bin"
    with pytest.raises(ModsError, match="目录|身份|变化|链接"):
        files.apply("data/original.bin", before, after, 0o644, ".deckymods-abc123")
    assert unexpected_target.read_bytes() == b"vanilla"
    assert original_target.read_bytes() == b"vanilla"
    assert list(tmp_path.rglob(".deckymods-*")) == []


def test_engine_does_not_recapture_replaced_root_as_trusted(filesystem, tmp_path, monkeypatch):
    game, _, _, _ = filesystem
    root = Path(game["path"])
    engine = Deployment(tmp_path / "state")
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    (extracted / "mod.bin").write_bytes(b"mod")
    plan = engine.prepare(
        game,
        "one",
        extracted,
        {"files": [{"source": "mod.bin", "target": "data/original.bin"}]},
    )
    real_files = GameFiles
    saved = root.with_name("original-game")

    def replace_before_open(current_game, objects, **kwargs):
        root.rename(saved)
        (root / "data").mkdir(parents=True)
        (root / "data/original.bin").write_bytes(b"vanilla")
        return real_files(current_game, objects, **kwargs)

    monkeypatch.setattr(deployment, "GameFiles", replace_before_open)
    with pytest.raises(ModsError, match="目录|身份|变化"):
        engine.install(game, plan["id"], True)
    assert (root / "data/original.bin").read_bytes() == b"vanilla"
    assert (saved / "data/original.bin").read_bytes() == b"vanilla"
    assert engine.list_mods(game["id"]) == []


@pytest.mark.parametrize("replacement", ["ancestor", "target"])
def test_apply_rejects_symlink_introduced_after_fingerprint(filesystem, tmp_path, replacement):
    game, objects, before, after = filesystem
    files = GameFiles(game, objects)
    root = Path(game["path"])
    outside = tmp_path / "outside"
    outside.mkdir()
    external = outside / "original.bin"
    external.write_bytes(b"vanilla")
    if replacement == "ancestor":
        (root / "data").rename(root / "data-original")
        (root / "data").symlink_to(outside, target_is_directory=True)
    else:
        (root / "data/original.bin").unlink()
        (root / "data/original.bin").symlink_to(external)
    with pytest.raises((ModsError, OSError)):
        files.apply("data/original.bin", before, after, 0o644, ".deckymods-abc123")
    assert external.read_bytes() == b"vanilla"
    assert list(outside.glob(".deckymods-*")) == []


def test_already_open_parent_descriptor_does_not_follow_later_ancestor_swap(
    filesystem, tmp_path, monkeypatch
):
    game, objects, before, after = filesystem
    files = GameFiles(game, objects)
    root = Path(game["path"])
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "original.bin").write_bytes(b"vanilla")
    rename = gamefs.rename_at
    swapped = False

    def swap_ancestor_before_rename(parent, source, target, *, exchange):
        nonlocal swapped
        if not swapped:
            swapped = True
            (root / "data").rename(root / "old-data")
            (root / "data").symlink_to(outside, target_is_directory=True)
        return rename(parent, source, target, exchange=exchange)

    monkeypatch.setattr(gamefs, "rename_at", swap_ancestor_before_rename)
    files.apply("data/original.bin", before, after, 0o644, ".deckymods-abc123")
    assert swapped
    assert (outside / "original.bin").read_bytes() == b"vanilla"
    assert (root / "old-data/original.bin").read_bytes() == b"mod"
    assert fingerprint(game)["path"] == game["path"]
