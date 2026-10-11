#!/usr/bin/env python3
"""Validate the static AK Screen community asset catalogue with the Python standard library."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "catalogue.json"
MAX_CATALOGUE = 2 * 1024 * 1024
MAX_MANIFEST = 1024 * 1024
MAX_FILE = 50 * 1024 * 1024
MAX_PACK = 250 * 1024 * 1024
LICENSES = {"CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0", "MIT", "Apache-2.0", "BSD-3-Clause", "ISC", "OFL-1.1"}
KINDS = {
    "mediaVideo": {"mp4", "webm", "mov", "mkv"},
    "mediaAudio": {"wav", "mp3", "flac", "ogg"},
    "mediaImage": {"png", "jpg", "jpeg", "webp", "gif"},
    "textTemplate": {"fcgt"},
    "effectPreset": {"json"},
    "transitionPreset": {"json"},
    "filterPreset": {"json"},
    "animationPreset": {"json"},
    "lut": {"cube"},
}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX = re.compile(r"^[0-9a-fA-F]{64}$")


def fail(message: str) -> None:
    raise ValueError(message)


def is_slug(value: object) -> bool:
    return isinstance(value, str) and len(value) <= 80 and SLUG.fullmatch(value) is not None


def repo_file(relative: object, prefix: str) -> tuple[Path, str]:
    if not isinstance(relative, str) or len(relative) > 512 or "\\" in relative:
        fail(f"ruta no válida: {relative!r}")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        fail(f"ruta insegura: {relative}")
    parts = relative.split("/")
    if len(parts) != 5 or parts[:4] != prefix.split("/"):
        fail(f"recurso fuera de su carpeta de paquete: {relative}")
    lexical_path = ROOT.joinpath(*parts)
    current = ROOT
    for part in parts:
        current = current / part
        if current.is_symlink():
            fail(f"el recurso atraviesa un enlace simbólico: {relative}")
    path = lexical_path.resolve(strict=True)
    if ROOT.resolve() not in path.parents or not path.is_file():
        fail(f"el recurso no es un archivo normal del repositorio: {relative}")
    return path, parts[-1].rsplit(".", 1)[-1].lower() if "." in parts[-1] else ""


def validate_pack(pack: object, seen_pack_versions: set[str], seen_assets: set[str]) -> None:
    if not isinstance(pack, dict):
        fail("cada paquete debe ser un objeto JSON")
    if set(pack) - {"id", "name", "description", "author", "version", "license", "tags", "assets"}:
        fail("el catálogo contiene campos de paquete desconocidos")
    author, pack_id, version = pack.get("author"), pack.get("id"), pack.get("version")
    if not is_slug(author) or not is_slug(pack_id):
        fail(f"autor o id no válido en el paquete: {pack.get('name', '?')}")
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?", version):
        fail(f"versión SemVer inválida en {author}/{pack_id}")
    if not isinstance(pack.get("name"), str) or not pack["name"].strip() or len(pack["name"]) > 160:
        fail(f"nombre inválido en {author}/{pack_id}")
    if not isinstance(pack.get("description", ""), str) or len(pack.get("description", "")) > 4000:
        fail(f"descripción demasiado larga en {author}/{pack_id}")
    tags = pack.get("tags", [])
    if not isinstance(tags, list) or len(tags) > 40 or any(not isinstance(tag, str) or len(tag) > 48 for tag in tags):
        fail(f"etiquetas no válidas en {author}/{pack_id}")
    if pack.get("license") not in LICENSES:
        fail(f"licencia de redistribución no permitida en {author}/{pack_id}")
    key = f"{author}/{pack_id}/{version}"
    if key in seen_pack_versions:
        fail(f"paquete/version duplicado: {key}")
    seen_pack_versions.add(key)
    assets = pack.get("assets")
    if not isinstance(assets, list) or not 1 <= len(assets) <= 100:
        fail(f"{key} debe contener entre 1 y 100 recursos")
    expected_prefix = f"packages/{author}/{pack_id}/{version}"
    version_dir = ROOT.joinpath(*expected_prefix.split("/"))
    current = ROOT
    for part in expected_prefix.split("/"):
        current = current / part
        if current.is_symlink():
            fail(f"la ruta del paquete atraviesa un enlace simbólico: {expected_prefix}")
    manifest_file = version_dir / "pack.json"
    if manifest_file.is_symlink() or not manifest_file.is_file() or manifest_file.stat().st_size > MAX_MANIFEST:
        fail(f"falta {expected_prefix}/pack.json")
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    for field in ("id", "name", "author", "version", "license"):
        if manifest.get(field) != pack.get(field):
            fail(f"{expected_prefix}/pack.json no coincide en {field}")
    manifest_assets = manifest.get("assets")
    if not isinstance(manifest_assets, list) or len(manifest_assets) != len(assets):
        fail(f"el manifiesto local no coincide con el catálogo en {key}")
    pack_total = 0
    for item in assets:
        if not isinstance(item, dict):
            fail(f"recurso inválido en {key}")
        if set(item) - {"id", "name", "type", "description", "path", "sha256", "size", "min_app_version", "attribution"}:
            fail(f"el recurso contiene campos desconocidos en {key}")
        asset_id = item.get("id")
        if not is_slug(asset_id) or len(asset_id) > 80:
            fail(f"id de recurso inválido en {key}")
        asset_key = f"{key}/{asset_id}"
        if asset_key in seen_assets:
            fail(f"id de recurso duplicado: {asset_key}")
        seen_assets.add(asset_key)
        kind = item.get("type")
        if kind not in KINDS:
            fail(f"tipo no admitido en {asset_key}: {kind!r}")
        expected_path_prefix = f"{expected_prefix}/"
        relative = item.get("path")
        if not isinstance(relative, str) or not relative.startswith(expected_path_prefix):
            fail(f"ruta fuera del paquete en {asset_key}")
        path, extension = repo_file(relative, expected_prefix)
        if extension not in KINDS[kind]:
            fail(f"extensión incompatible con {kind} en {asset_key}")
        size = path.stat().st_size
        if not 0 < size <= MAX_FILE or item.get("size") != size:
            fail(f"tamaño inválido en {asset_key}: {size}")
        pack_total += size
        if pack_total > MAX_PACK:
            fail(f"{key} supera 250 MB")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if not isinstance(item.get("sha256"), str) or not HEX.fullmatch(item["sha256"]) or digest != item["sha256"].lower():
            fail(f"SHA-256 incorrecto en {asset_key}")
        attribution = item.get("attribution")
        if not isinstance(attribution, dict) or set(attribution) != {"source", "license"} or not isinstance(attribution.get("source"), str) or not attribution["source"].strip() or len(attribution["source"]) > 1000:
            fail(f"falta procedencia en {asset_key}")
        if attribution.get("license") not in LICENSES:
            fail(f"falta una licencia redistribuible en {asset_key}")
        if not isinstance(item.get("name"), str) or not item["name"].strip() or len(item["name"]) > 160:
            fail(f"nombre no válido en {asset_key}")
        if not isinstance(item.get("description", ""), str) or len(item.get("description", "")) > 2000:
            fail(f"descripción no válida en {asset_key}")
        minimum = item.get("min_app_version", "")
        if not isinstance(minimum, str) or (minimum and not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?", minimum)):
            fail(f"min_app_version no válida en {asset_key}")
    for actual, expected in zip(manifest_assets, assets, strict=True):
        for field in ("id", "name", "type", "path", "size", "sha256", "attribution"):
            if actual.get(field) != expected.get(field):
                fail(f"pack.json no coincide con catalogue.json para {key}/{expected.get('id')}")
    allowed_files = {"pack.json"} | {Path(item["path"]).name for item in assets}
    for child in version_dir.iterdir():
        if child.name not in allowed_files or child.is_symlink() or not child.is_file():
            fail(f"archivo adicional o ruta insegura en {expected_prefix}: {child.name}")


def main() -> int:
    try:
        raw = CATALOGUE.read_bytes()
        if len(raw) > MAX_CATALOGUE:
            fail("catalogue.json supera 2 MB")
        catalogue = json.loads(raw)
        if not isinstance(catalogue, dict) or set(catalogue) != {"schema", "packs"} or catalogue.get("schema") != 1 or not isinstance(catalogue.get("packs"), list):
            fail("formato de catálogo no compatible; se requiere schema 1 y packs[]")
        if len(catalogue["packs"]) > 2000:
            fail("el catálogo supera 2000 paquetes")
        seen_pack_versions: set[str] = set()
        seen_assets: set[str] = set()
        for pack in catalogue["packs"]:
            validate_pack(pack, seen_pack_versions, seen_assets)
        print(f"Catálogo válido: {len(catalogue['packs'])} paquetes y {len(seen_assets)} recursos.")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, KeyError, TypeError) as error:
        print(f"Validación fallida: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
