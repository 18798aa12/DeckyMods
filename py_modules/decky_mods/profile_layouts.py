"""Conservative, independently implemented path rules from documented mod layouts."""

from pathlib import PurePosixPath

from .adapters import _is_metadata
from .errors import ModsError
from .profile_bethesda import DATA_ROOTS, data_layout


def anchored(
    paths: list[PurePosixPath], anchors: tuple[str, ...]
) -> list[tuple[PurePosixPath, PurePosixPath]]:
    result, prefixes = [], set()
    for path in paths:
        lower = tuple(part.casefold() for part in path.parts)
        index = next(
            (i for i in range(len(lower) - len(anchors)) if lower[i : i + len(anchors)] == anchors),
            None,
        )
        if index is None:
            if not _is_metadata(path) and path.name.casefold() not in {"license", "licence"}:
                raise ModsError("包内存在该安装方式不支持的目录或文件，请单独导入需要的版本")
            continue
        prefixes.add(lower[:index])
        result.append((path, PurePosixPath(*path.parts[index + len(anchors) :])))
    if len(prefixes) != 1 or not result:
        raise ModsError("安装目录不完整，或包内包含多个互斥版本；请按说明分别导入")
    return result


def path_layout(paths: list[PurePosixPath], handler: str, game: dict | None = None) -> list[dict]:
    if handler == "cyberpunk_archive":
        payload = [
            p
            for p in paths
            if p.suffix.casefold() == ".archive" or p.name.casefold().endswith(".archive.xl")
        ]
        if not payload:
            raise ModsError("未找到 .archive 资源包；REDmod、脚本和框架请使用对应说明")
        if any(
            tuple(x.casefold() for x in p.parts[:3]) == ("archive", "pc", "mod")
            or "archive" in [x.casefold() for x in p.parts]
            for p in payload
        ):
            items = anchored(paths, ("archive", "pc", "mod"))
        elif len({p.parent for p in payload}) == 1 and all(
            p in payload or _is_metadata(p) for p in paths
        ):
            items = [(p, PurePosixPath(p.name)) for p in payload]
        else:
            raise ModsError("资源包包含多个目录或其它格式，不能猜测安装版本")
        if any(
            p.suffix.casefold() != ".archive" and not p.name.casefold().endswith(".archive.xl")
            for p, _ in items
        ):
            raise ModsError("该方案仅部署 archive 资源及配套 archive.xl 文件")
        return [{"source": str(p), "target": f"archive/pc/mod/{tail}"} for p, tail in items]
    if handler == "bethesda_data":
        if any("data" in (x.casefold() for x in p.parts[:-1]) for p in paths):
            items = anchored(paths, ("data",))
        else:
            payload = [
                p
                for p in paths
                if p.parts[0].casefold() in DATA_ROOTS
                or len(p.parts) == 1
                and p.suffix.casefold() in {".esp", ".esm", ".esl", ".bsa", ".ba2"}
            ]
            if not payload or any(p not in payload and not _is_metadata(p) for p in paths):
                raise ModsError(
                    "仅支持明确的 Data 目录或标准数据文件；FOMOD/加载器请按专用说明处理"
                )
            items = [(p, p) for p in payload]
        return data_layout(items, game or {})
    if handler == "bepinex_plugins":
        items = anchored(paths, ("bepinex", "plugins"))
        if not any(p.suffix.casefold() == ".dll" for p, _ in items):
            raise ModsError("未找到 BepInEx 插件 DLL；加载器和 patcher 需要单独处理")
        return [{"source": str(p), "target": f"BepInEx/plugins/{tail}"} for p, tail in items]
    if handler == "witcher3_mods":
        items = anchored(paths, ("mods",))
        for _, tail in items:
            if len(tail.parts) < 3 or (
                not tail.parts[0].casefold().startswith("mod")
                or tail.parts[1].casefold() != "content"
            ):
                raise ModsError("MOD 子目录结构不完整；配置合并、DLC 或外部工具请按单独说明处理")
        return [{"source": str(p), "target": f"Mods/{tail}"} for p, tail in items]
    raise ModsError("此安装方式尚未实现文件部署，请按方案说明使用对应工具")
