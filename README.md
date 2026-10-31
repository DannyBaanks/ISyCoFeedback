# ISyCoFeedback

**Ejecuta, verifica, repara y conserva lo que realmente ocurrió.**

ISyCoFeedback reúne comandos de proyecto, reparación acotada, revisión de datos
y evidencia verificable en un paquete Python. La versión **2.0.0a1** fusiona los
núcleos propios de ejecución, documentos y persistencia. [English](README_EN.md).

## GitBack: vista previa web móvil

El prototipo PWA está en [`web/`](web/README.md). Requiere Node.js **20.19+**
(o **22.12+**) y npm:

```bash
cd web
npm ci
npm run dev
```

Es una interfaz de demostración con datos sintéticos. GitLab y Duo no están
conectados; no ejecuta pruebas reales ni envía cambios remotos. [Ver captura
móvil](docs/previews/gitback-mobile.png).

## Una demo local

Requiere Python **3.11+** y Git para las funciones que lo usan.

```bash
python -m pip install -e '.[dev]'
isycofeedback demo
isycofeedback document-demo
```

La primera demo ejecuta un comando real contra un fixture sintético, aplica una
propuesta fija y vuelve a verificar. También rechaza una edición fuera de alcance,
agota tres intentos fallidos y detecta un recibo alterado. Las propuestas son
explícitas: esta demo no llama a una IA ni a un servicio externo.

```text
REPAIR PASS (2 verifications; fixed proposal, no AI)
SCOPE DENIED
BUDGET REPAIR_EXHAUSTED (3 verifications)
LEDGER VALID
TAMPER INVALID
```

`document-demo` normaliza texto sin inventar confianza, requiere revisión y
registra el rechazo explícito del reviewer de demostración con evidencia válida.
Para conservar la primera demo, usa `isycofeedback demo --output /ruta/nueva`.

## Conectar un proyecto

```bash
isycofeedback init --path /ruta/proyecto
```

Edita `.isycofeedback.yml` con comandos que tú hayas revisado:

```yaml
version: 1
project:
  name: My project
commands:
  test: python -m unittest discover -s tests
  verify: python -m unittest discover -s tests
retry:
  max_attempts: 3
secrets:
  - MY_API_KEY
```

`secrets` contiene nombres de variables, nunca sus valores. Los valores configurados
se redactan antes de guardar stdout, stderr y comandos en recibos y base de intentos.
No es un detector universal de secretos: revisa el contenido antes de compartirlo.

```bash
isycofeedback doctor --path /ruta/proyecto
isycofeedback test --path /ruta/proyecto --run-id test-001
isycofeedback retry --path /ruta/proyecto --run-id repair-001
isycofeedback history --path /ruta/proyecto
isycofeedback audit --path /ruta/proyecto
```

El presupuesto es de **una a tres verificaciones por run ID**, incluida la inicial.
Reusar el mismo ID conserva su resultado y presupuesto; cambiar comando, proyecto,
alcance o presupuesto con ese ID se rechaza. Sin `--run-id`, cada invocación crea
un trabajo nuevo. Esto no impone por sí solo un presupuesto global por MR.

## Reparación por propuesta explícita

Un archivo JSON contiene los cambios propuestos:

```json
[
  {"path": "src/example.py", "old_content": "broken\n", "new_content": "fixed\n"}
]
```

```bash
isycofeedback repair --path /ruta/proyecto --run-id fix-001 \
  --patch-file /ruta/proposal.json --allow src/example.py
```

La verificación original se ejecuta antes y después del patch. Sólo se permiten
archivos existentes enumerados por `--allow`, con contenido previo exacto. Se
rechazan escapes, symlinks, duplicados, archivos de tests y controles de Git/CI.
Si la reparación no supera la verificación, se restaura el contenido anterior.
La librería `Workflow.run(..., provider=...)` admite un adaptador de propuestas;
el callback Python es código de confianza del host, no un sandbox para plugins.

## Persistencia y evidencia

```text
.isycofeedback/
  workflows.db       # reserva de intentos antes de ejecutar
  receipts/*.json    # resultado redactado y sellado
  ledger.jsonl       # cadena de hashes de los recibos
```

Los trabajos interrumpidos no se reejecutan automáticamente. Después de detener
los workers y revisar qué proceso quedó activo, `isycofeedback recover --path ...`
marca trabajos incompletos como `UNKNOWN`. No significa que se canceló un proceso
externo ni que la acción nunca sucedió.

Antes de aplicar un patch se guarda una copia para recuperación en SQLite, con
permisos de archivo restringidos. Se rechazan propuestas y originales que contengan
algún secreto configurado. No se detectan secretos que no hayas declarado.
La recuperación sólo restaura contenido que aún coincida con la propuesta; conserva
los cambios posteriores de otra persona y deja el backup pendiente. Puedes resolver
el conflicto y repetir `recover`; `history` muestra los backups pendientes.

`audit` verifica el ledger y cada recibo asociado. Conserva el HEAD impreso en un
almacén independiente y compruébalo con `audit --expected-head HASH` para detectar
truncamiento o reescritura respecto a ese valor. Los hashes prueban consistencia
respecto al ancla; no autentican personas ni equipos. Un propietario que pueda
cambiar todos los archivos y el ancla también puede reescribir la historia.

Una escritura usa un lock exclusivo. Si el proceso murió dejando `.ledger-lock`,
la siguiente escritura se detiene: inspecciona los recibos y el ledger antes de
retirar manualmente ese lock. Un recibo huérfano no se certifica como historial válido.

## Núcleos reutilizables

- `isycofeedback.documents`: DocumentPipeline, reglas por campo, revisión ligada a
  la extracción, evidencia y ledger. Extractores intercambiables por protocolo;
  PDF offline opcional con `pip install -e '.[pdf]'`.
  Las reglas personalizadas que no sean dataclasses deben declarar
  `evidence_config()` para incluir sus parámetros en la identidad de la evidencia.
- `isycofeedback.operations`: eventos, políticas de confirmación, contratos de
  acciones, persistencia SQLite/memoria y recuperación. Un proveedor que aceptó una
  acción no demuestra que el destinatario la confirmó.
- `isycofeedback.workflow`: comandos y propuestas limitadas, intentos durables,
  rollback y recibos enlazados al ledger.

Consulta [procedencia y licencia](docs/PROVENANCE.md) y el
[diseño](docs/superpowers/specs/2026-10-21-unified-core-design.md).

## Alcance comprobado

La suite local corre en Linux con Python 3.12, sin red y sin acceso al home.
Incluye reparación, DENY, presupuesto persistente, recuperación, alteración de
recibos y limpieza de procesos hijos por timeout en POSIX. La rama Windows del
runner no se verificó en esta sesión.

Los comandos del manifiesto usan shell y tienen los permisos del proceso: ejecuta
código no confiable en un contenedor o sandbox externo. El allowlist de patches
no impide que un comando autorizado edite otros archivos. La integración viva con
GitLab Duo y el despliegue público siguen pendientes; este merge no los demuestra.
`issue` y `pr` conservan su modo `--dry-run`, sin publicación remota.

```bash
python -m pytest -q
```

## Archivos añadidos al repositorio (2026-10-31)

El commit `36f4ac4` versiona 69 archivos que estaban sin control de versiones:

- `src/isycofeedback/documents/` y `src/isycofeedback/operations/` (incluye
  `persistence/` con sqlite, memoria y repositorio), más `audit.py`, `demo.py`,
  `workflow.py`, `workflow_store.py` y `__main__.py`.
- `tests/` — 12 módulos de pruebas (documentos, operaciones, CLI unificado, fronteras).
- `docs/` — `PROVENANCE.md`, `VERIFICATION.md`, `GITBACK_ROADMAP.md`, `GITLAB_CI.md`,
  `MIGRATION_MANIFEST.json` y los registros `verification-*.log`.
- `web/` — aplicación GitBack con Vite (`index.html`, `src/main.tsx`, `public/`, config).
- CI: `.github/workflows/ci.yml` y `.gitlab-ci.yml`.


## Licencia

MIT. Véanse [LICENSE](LICENSE) y [PROVENANCE](docs/PROVENANCE.md).
