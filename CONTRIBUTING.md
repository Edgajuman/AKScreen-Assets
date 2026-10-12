# Contribuir a la biblioteca

Los pull requests son la única vía para publicar. El catálogo de `main` es lo que ven los usuarios; un
aporte pendiente nunca se distribuye. Puedes preparar y enviar el fork/PR desde **AK Screen →
Herramientas → Biblioteca comunitaria**, o hacer el proceso manualmente desde GitHub.

## Estructura

```text
catalogue.json
packages/<usuario-github>/<id-paquete>/<versión>/
  pack.json
  asset-001.mp4
  asset-002.fcgt
```

Usa IDs minúsculos con letras ASCII, números y guiones. Las versiones son SemVer, como `1.0.0`. Cada
archivo se declara en `pack.json` y en la entrada del paquete de `catalogue.json`; la ruta, tamaño y
SHA-256 deben coincidir exactamente. El validador de Actions detecta los errores antes de la revisión.

## Qué se puede aportar

- Medios propios o con licencia abierta que permita su redistribución.
- Plantillas `.fcgt` de AK Screen, con fuentes incrustadas únicamente si su licencia lo permite.
- Presets JSON que usen efectos existentes en AK Screen.
- Archivos LUT `.cube`.
- Una carpeta/paquete con varios recursos relacionados o un único elemento independiente.

No se aceptan ejecutables, DLL, WASM, scripts, macros, fuentes de datos externas ejecutables, instaladores,
archivos comprimidos, archivos con contraseña, licencias NC/ND ni contenido obtenido sin autorización.
No publiques información personal de terceros, malware, material con copyright ajeno o recursos que
prometan funciones que el editor no puede aplicar.

## Licencia y atribución

Elige una licencia de redistribución explícita: CC0-1.0, CC-BY-4.0, CC-BY-SA-4.0, MIT, Apache-2.0,
BSD-3-Clause, ISC u OFL-1.1. Para cada elemento indica `source` como `original work` o una URL pública
del origen y vuelve a declarar su licencia. Añade créditos/condiciones de atribución al texto de la
descripción cuando la licencia los requiera. Al abrir el PR confirmas que creaste el recurso o que
tienes derechos suficientes para distribuirlo bajo la licencia indicada.

## Actualizar o retirar

Las versiones publicadas son inmutables. Para actualizar un paquete, publica una versión SemVer nueva
con carpeta y hashes nuevos; no reemplaces el contenido de una versión anterior. Para retirar o corregir
un recurso, abre otro PR y explica la causa. El mantenedor puede quitarlo del catálogo y conservar un
registro de la decisión.

## Lista antes de enviar

1. Comprueba `pack.json`, licencias, atribución, nombres y compatibilidad con AK Screen.
2. Para enviar desde AK Screen, crea el fork desde la página del repositorio e instala la [GitHub App](https://github.com/apps/ak-screen-asset-publisher)
   con acceso solo a ese fork. AK Screen autenticará tu cuenta con un código temporal, preparará la rama
   y abrirá un PR; no pide permiso para crear repositorios ni modifica `main`.
3. Para el envío manual, copia la carpeta preparada a `packages/<tu-usuario>/<id-del-paquete>/<versión>/`
   en tu fork.
4. Desde la raíz del repositorio ejecuta `python tools/add_package.py packages/<tu-usuario>/<id-del-paquete>/<versión>/pack.json`.
5. Ejecuta `python tools/validate_catalogue.py`; esta misma validación corre automáticamente en cada PR.
6. Abre un PR con una descripción breve, capturas/vistas previas creadas por ti y los cambios de versión.
7. Espera la revisión y las comprobaciones automáticas. No publiques anuncios de aceptación antes de que
   el PR se fusione.

Para crear presets, empieza con **Effects → Export Preset…** o exporta una plantilla `.fcgt`; evita
editar los formatos internos a mano salvo que conozcas su esquema.


## Recursos nuevos en 2.4.0

Usa `essentialGraphics` para plantillas .fcgt, `essentialSound` para ajustes JSON de audio y `chartTemplate` para .akchart. Un preset de transición contiene `format: akscreen.transition-preset`, `effect` (ID real del motor), `seconds` y `params`. Los demás presets conservan el formato de exportación del editor.

Cada recurso puede declarar `preview: {path, size, sha256}`: PNG, JPEG, WebP o SVG dentro de la misma carpeta, hasta 2 MiB. La imagen debe ser tuya o redistribuible. Describe si es ilustrativa. No incluyas claves, scripts o ejecutables. Mira las tres colecciones de dehuman para ejemplos completos.
