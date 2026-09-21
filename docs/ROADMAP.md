# ISyCoFeedback — Roadmap de demostración real

## Objetivo

Demostrar que `isycofeedback` puede conectarse a un repositorio ajeno mediante
un contrato pequeño y coordinar ejecución, pruebas, verificación, evidencia,
reparación acotada y contribución. El primer consumidor real será
`Chrome-to-Fox`, sin acoplar su dominio al núcleo.

## Estado inicial verificado

- El proyecto se ubicará en `/home/danny/Development/ISyCo Git/isycofeedback`.
- `Chrome-to-Fox` ya expone CLI, corpus de extensiones, conversión,
  validación, packaging y un harness experimental de Firefox.
- La suite de `Chrome-to-Fox` requiere instalación editable para ser ejecutada;
  un `pytest -q` sin instalar el paquete produjo `ModuleNotFoundError`.
- Hay cambios no rastreados preexistentes en `Chrome-to-Fox`; no forman parte
  de este proyecto y deben conservarse.

## Milestones

### M0 — Baseline reproducible

Capturar comandos, dependencias, herramientas disponibles y fallos de
`Chrome-to-Fox` sin modificarlo.

Salida:

- `isycofeedback doctor` distingue Git, Python, pytest, Firefox, `gh`,
  manifest y comandos configurados.
- Cada fallo tiene clasificación (`CONFIGURATION_FAILURE`,
  `DEPENDENCY_FAILURE`, `ENVIRONMENT_FAILURE`, etc.).
- Ningún entorno incompleto aparece como `PASS`.

### M1 — Contrato mínimo del consumidor

Definir `.isycofeedback.yml` en el repositorio consumidor, con comandos
declarativos para `run`, `test`, `verify` y `reproduce`, más el presupuesto de
retry. El núcleo no interpreta Python, Firefox ni Chrome-to-Fox.

Salida:

- El manifest se valida.
- `isycofeedback capabilities` refleja sólo lo declarado.
- No hay secretos en la configuración del proyecto.

### M2 — Flujo verde extremo a extremo

Usar `corpus/simple-popup/` para demostrar:

```text
init → doctor → capabilities → run → test → verify → PASS → receipt
```

El recibo debe conservar comando, cwd, timestamps, duración, exit code,
stdout/stderr, HEAD, archivos cambiados, verdict y `run_id`.

### M3 — Flujo rojo determinista

Ejecutar un fixture fallido y demostrar el límite duro de tres intentos:

```text
FAIL → ATTEMPT 1/3 → ATTEMPT 2/3 → ATTEMPT 3/3 → STOP
```

Cada intento tendrá evidencia independiente. Un cuarto intento será un fallo
del sistema.

### M4 — Reparación controlada sin créditos

Probar un reparador falso que entrega un patch válido. El harness aplica el
patch, vuelve a ejecutar la verificación y sólo declara `PASS` si el comando
real pasa.

Salida:

- Camino `FAIL → PATCH → VERIFY → PASS`.
- Patches y recibos separados por intento.
- El texto de un reparador nunca cuenta como evidencia de éxito.

### M5 — Proveedor OpenAI-compatible

Probar un endpoint HTTP falso con `base_url`, `model` y credencial externa.
Validar envelope acotado, timeouts, errores, modo deshabilitado y redacción.

La API key no puede aparecer en manifest, logs, stdout, recibos, prompts ni
diffs.

### M6 — Firefox real

Ejecutar conversión y pruebas en perfil Firefox desechable sobre el corpus:

```text
simple-popup
background-worker
content-script
has-offscreen
html-to-design
```

Un entorno sin Firefox produce `ENVIRONMENT_FAILURE` o
`NOT_DEMONSTRATED`, nunca un falso `PASS`.

### M7 — GitHub seguro

Implementar primero:

```bash
isycofeedback issue --dry-run
isycofeedback fork --dry-run
isycofeedback pr --dry-run
```

Los payloads deben incluir reproducción, commit, fallos, intentos, run ID y
estado de verificación, sin tokens ni mutaciones remotas.

### M8 — Dogfood completo con Chrome-to-Fox

Ejecutar una sesión documentada con camino verde y camino rojo:

```text
init → doctor → capabilities → run → test → verify → retry → issue --dry-run
```

La entrega se considera demostrada cuando existen:

- un caso real `PASS`;
- un caso real `FAIL`;
- exactamente tres intentos;
- recibos y evidencia verificables;
- reparación fake exitosa;
- prueba del proveedor compatible con endpoint falso;
- issue y PR en dry-run;
- prueba Firefox cuando el entorno lo permita;
- cero secretos en artefactos.

## Orden de ejecución

1. M0: baseline y doctor.
2. M1: manifest y capabilities.
3. M2: runner, receipts y flujo verde.
4. M3: retry y flujo rojo.
5. M4: fake repair provider.
6. M5: proveedor OpenAI-compatible.
7. M6: Firefox real.
8. M7: GitHub dry-run.
9. M8: demo final y documentación.

## Regla de evidencia

Cada milestone debe dejar comandos exactos, salida cruda, exit status, hashes
de artefactos cuando aplique y una sección explícita de
`NOT_DEMONSTRATED`. No se reemplaza evidencia histórica: cada ejecución usa
un `run_id` nuevo.
