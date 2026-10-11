# AK Screen Assets

Biblioteca comunitaria de recursos aprobados para AK Screen: medios pequeños, plantillas de títulos,
presets de efectos, transiciones, filtros, LUT y animaciones. Los paquetes pueden agrupar recursos de
un mismo tema —por ejemplo, una colección de fútbol— o publicar uno solo.

**Los usuarios pueden explorar y descargar sin iniciar sesión.** AK Screen consulta el catálogo
estático [`catalogue.json`](catalogue.json) y verifica el tamaño y el SHA-256 de cada recurso antes de
guardarlo. Los aportes entran mediante pull request y solo se muestran tras su revisión y fusión.

## Para publicar

Lee [CONTRIBUTING.md](CONTRIBUTING.md), prepara `packages/<tu-usuario>/<id-del-paquete>/<versión>/`
y abre un pull request. El editor puede preparar esa carpeta desde **Herramientas → Biblioteca
comunitaria → Preparar aporte**. Nunca añadas credenciales, programas ejecutables, scripts o código de
plugins.

## Formatos aceptados

| Tipo | Archivos |
|---|---|
| Vídeo | MP4, WebM, MOV, MKV |
| Audio | WAV, MP3, FLAC, OGG |
| Imagen | PNG, JPEG, WebP, GIF |
| Plantilla de título | `.fcgt` propio de AK Screen |
| Preset de efecto, transición, filtro o animación | JSON de presets compatibles |
| LUT | `.cube` |

Un preset modifica parámetros de capacidades que ya existen en la aplicación. Este repositorio no
distribuye extensiones ni código ejecutable; esos componentes usan su catálogo separado y su modelo
de revisión/permisos.

## Licencias y tamaño

Cada recurso declara atribución, procedencia y licencia en `pack.json`. Se admiten CC0-1.0,
CC-BY-4.0, CC-BY-SA-4.0, MIT, Apache-2.0, BSD-3-Clause, ISC y OFL-1.1. El autor debe tener derecho a
redistribuir el archivo y sus recursos incluidos.

El límite es 50 MB por archivo y 250 MB por paquete. Los vídeos de mayor tamaño deben adjuntarse a una
GitHub Release tras su aprobación; no uses Git LFS para colecciones descargadas por mucha gente porque
su cuota de transferencia pertenece al propietario del repositorio. Si el tráfico crece, el catálogo
puede seguir en este repositorio y los binarios grandes migrar a un CDN u objeto público.

## Seguridad y privacidad

El contenido se sirve desde GitHub Raw bajo HTTPS; la aplicación limita tamaños, rutas y extensiones,
verifica hashes y solo pasa a sus importadores formatos de datos conocidos. GitHub Actions valida cada
pull request. El editor no ejecuta el contenido de este repositorio ni envía proyectos, clips o datos
personales. La licencia y autoría de cada recurso se conservan en su manifiesto.

La biblioteca y el catálogo son públicos. No se requiere token para descargar o actualizar. Nunca
subas un PAT, contraseña, clave privada ni API key a este repositorio.
