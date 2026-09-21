# Dogfood: Chrome-to-Fox

Fecha de ejecución: 2026-09-21.

`isycofeedback` ejecutó comandos con cwd real de Chrome-to-Fox y leyó el
manifest externo
`examples/chrome-to-fox.isycofeedback.yml`. Los recibos se guardaron fuera del
consumidor mediante `--evidence-path`; Chrome-to-Fox no fue modificado.

## Doctor

```text
GIT  PASS
GH  AVAILABLE
PYTHON  AVAILABLE
MANIFEST  PASS
PROJECT  Chrome-to-Fox
COMMANDS  reproduce, run, test, verify
```

## Test real PASS

Contrato usado:

```yaml
test: PYTHONPATH=src py -m pytest -q
```

Resultado:

```text
TEST  PASS
Receipt: /tmp/isycofeedback-chrome2fox.lD7pWe/.isycofeedback/receipts/333079adb2f44175a978cb8589f73d69.json
```

El recibo registra cwd, comando, timestamps, duración, streams y exit code.

## Fallo real preservado

El análisis ejecutó código real de Chrome-to-Fox:

```text
RUN  FAIL
```

El proceso imprimió un informe con `errors: []`, pero Chrome-to-Fox devolvió
exit code `1`. El runner conservó stdout y clasificó el resultado como FAIL;
no convirtió la salida textual en PASS.

También se observó inicialmente:

```text
ModuleNotFoundError: No module named 'chrome2fox'
```

El contrato se corrigió para declarar `PYTHONPATH=src`. En otra prueba, el
ejecutable `chrome2fox` no estaba instalado y se cambió el ejemplo al módulo
`py -m chrome2fox.cli`, sin tocar el repositorio consumidor.

## NOT_DEMONSTRATED

- `reproduce` y `verify` no se ejecutaron porque producirían archivos de
  salida dentro de Chrome-to-Fox y esta demo está restringida a no modificar
  ese repositorio.
- La llamada HTTP real al proveedor OpenAI-compatible no se ejecutó: el
  sandbox no permite abrir sockets locales. La construcción de URL, payload y
  header fue verificada con tests.
- Firefox real aún no está conectado al CLI de isycofeedback.
