#!/usr/bin/env python3
"""Add one reviewed-ready packages/*/pack.json record to catalogue.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "catalogue.json"


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: python3 tools/add_package.py packages/<autor>/<id>/<versión>/pack.json", file=sys.stderr)
        return 2
    source = Path(sys.argv[1])
    if not source.is_absolute():
        source = ROOT / source
    try:
        relative = source.absolute().relative_to(ROOT.resolve()).as_posix().split("/")
        if len(relative) != 5 or relative[0] != "packages" or relative[-1] != "pack.json":
            raise ValueError("estructura esperada: packages/autor/id/versión/pack.json")
        current = ROOT
        for part in relative:
            current = current / part
            if current.is_symlink():
                raise ValueError("no se admiten enlaces simbólicos en la carpeta del paquete")
        path = source.resolve(strict=True)
        if ROOT.resolve() not in path.parents:
            raise ValueError("la ruta del paquete debe permanecer en el repositorio")
        pack = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(pack, dict) or pack.get("schema") != 1:
            raise ValueError("pack.json debe declarar schema: 1")
        expected = {"author": relative[1], "id": relative[2], "version": relative[3]}
        if any(pack.get(key) != value for key, value in expected.items()):
            raise ValueError("autor, id y versión deben coincidir con la ruta")
        if not isinstance(pack.get("assets"), list) or not pack["assets"]:
            raise ValueError("pack.json debe incluir al menos un recurso")
        record = {key: pack[key] for key in ("id", "name", "description", "author", "version", "license", "tags", "assets") if key in pack}
        raw = CATALOGUE.read_bytes()
        catalogue = json.loads(raw)
        if catalogue.get("schema") != 1 or not isinstance(catalogue.get("packs"), list):
            raise ValueError("catalogue.json no usa el formato schema 1")
        key = (record["author"], record["id"], record["version"])
        if any((item.get("author"), item.get("id"), item.get("version")) == key for item in catalogue["packs"]):
            raise ValueError("esa versión ya está publicada en el catálogo; aumenta SemVer")
        catalogue["packs"].append(record)
        catalogue["packs"].sort(key=lambda item: (item.get("name", "").casefold(), item.get("author", ""), item.get("version", "")))
        temporary = CATALOGUE.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(CATALOGUE)
        print(f"Añadido {record['author']}/{record['id']}@{record['version']}; ejecuta tools/validate_catalogue.py")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        print(f"No se añadió el paquete: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
