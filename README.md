# ✨ ISyCoFeedback

<p align="center">
  <strong>Cuando un proyecto falla, debería dejarte un camino para seguir.</strong>
</p>

<p align="center">
  <a href="README_EN.md">🇬🇧 English version</a>
</p>

ISyCoFeedback es un compañero de terminal para cualquier repositorio.

Te ayuda a:

```text
ejecutarlo   →  ver qué pasó
probarlo     →  saber si realmente funciona
reintentarlo →  detenerse después de tres intentos honestos
guardar      →  conservar la evidencia útil
pedir ayuda  →  preparar un issue o una contribución
```

Sin mensajes mágicos de “¡arreglado!”. Sin ciclos infinitos. Sin perder el contexto.

Sólo un camino tranquilo y repetible desde **“se rompió”** hasta **“esto es lo que sabemos.”**

> **Estado:** `0.1.0 ALPHA` — ya demostrado contra el repositorio real de
> Chrome-to-Fox mediante un contrato local externo. El proyecto es joven,
> pero la promesa central ya funciona.

---

## La idea en una imagen

```text
+------------------------------------------+
|               Tu proyecto                |
|      Python · JS · GlyphFuck · lo que sea |
|             build o workflow              |
+---------------------+--------------------+
                      |
              contrato local pequeño
                      |
                      v
+------------------------------------------+
|              ISyCoFeedback                |
|                                          |
|          run · test · verify              |
|          retry · repair                   |
|          evidencia · compartir            |
+---------------------+--------------------+
                      |
                      v
+------------------------------------------+
|             Un siguiente paso             |
|          no sólo una marca roja           |
+------------------------------------------+
```

Tu proyecto conserva el control de sus comandos. ISyCoFeedback simplemente les
da una superficie consistente y fácil de entender.

## Una demo pequeña

```console
$ isycofeedback test
TEST  FAIL

$ isycofeedback retry
ATTEMPT 1/3  FAIL
ATTEMPT 2/3  FAIL
ATTEMPT 3/3  FAIL

Presupuesto de reparación agotado.
Evidencia guardada.
Siguientes pasos: issue • fork • pull request
```

Lo importante no es que la salida sea roja. Es que el fallo queda capturado,
reproducible y listo para que otra persona lo entienda.

## Por qué usarlo

### 🧭 Menos adivinanzas

Puedes ver el comando, la carpeta, los tiempos, la salida y el resultado exacto
de cada intento.

### 🧱 No hay ciclos infinitos

El presupuesto de reparación por defecto es de tres intentos. Después se
detiene y muestra las siguientes acciones útiles.

### 🧾 No hay éxitos de “confía en mí”

Un proyecto sólo recibe `PASS` cuando su comando real de verificación pasa.

### 🛟 Mejores relevos

Cuando algo falla, la evidencia guardada puede convertirse en el punto de
partida de un issue, un fork o un pull request.

### 🌍 Funciona con tu proyecto

Python, JavaScript, Rust, scripts de shell, herramientas de build o algo
maravillosamente extraño: el proyecto define sus propios comandos.

## Pruébalo en dos minutos

Desde el repositorio al que quieras darle esta superficie:

```console
$ isycofeedback init
$ isycofeedback doctor
$ isycofeedback capabilities
$ isycofeedback test
```

El primer comando crea un archivo pequeño `.isycofeedback.yml`. No intenta
adivinar el significado de tu proyecto ni inventar un workflow en silencio.

Example:

```yaml
version: 1

project:
  name: My Project

commands:
  test: "your test command"
  verify: "your verification command"
  reproduce: "your reproduction command"

retry:
  max_attempts: 3
```

Esa es toda la idea: tu repositorio declara los botones; ISyCoFeedback los
vuelve consistentes.

## Prueba real: Chrome-to-Fox

ISyCoFeedback ya ejecutó la suite real de Chrome-to-Fox con:

```text
GIT  PASS
MANIFEST  PASS
PROJECT  Chrome-to-Fox
TEST  PASS
```

La evidencia se guardó fuera del repositorio consumidor, así que no se modificó
durante la demostración.

También detectó una diferencia real: el analizador de Chrome-to-Fox imprimió
una lista de errores vacía, pero devolvió un código de salida de fallo.
ISyCoFeedback conservó el resultado como `FAIL` en vez de fingir que el texto
significaba éxito.

See the full, honest transcript in
[docs/DEMO-CHROME-TO-FOX.md](docs/DEMO-CHROME-TO-FOX.md).

## ¿Qué pasa con tus datos privados?

- La configuración contiene comandos, no credenciales.
- Los recibos son locales y Git los ignora por defecto.
- Las API keys nunca se escriben en manifests ni recibos.
- La reparación opcional con IA recibe un resumen acotado del fallo, no todo tu
  repositorio por defecto.
- Las acciones de GitHub se preparan como dry-runs antes de cualquier cambio remoto.

## ¿Qué está listo hoy?

| Experiencia | Estado |
|---|---|
| `init`, `doctor`, `capabilities` | ✅ Funciona |
| run, test, verify, reproduce | ✅ Funciona |
| Recibos y evidencia | ✅ Funciona |
| Límite de tres intentos | ✅ Funciona |
| Reparación fake mediante patches | ✅ Funciona |
| Constructor OpenAI-compatible | ✅ Funciona |
| GitHub issue / PR dry-run | ✅ Funciona |
| Demostración con Firefox | 🚧 Siguiente milestone |
| Petición real al proveedor | ⚠️ Falta una prueba de integración externa |

## La promesa

ISyCoFeedback no intenta convertirse en tu sistema de build, tu project
manager ni el cerebro de tu repositorio.

Es la capa pequeña que hace que un fallo sea entendible y que contribuir sea
posible.

## Desarrollo

```console
$ PYTHONPATH=src py -m pytest -q
27 passed
```

El roadmap vive en [docs/ROADMAP.md](docs/ROADMAP.md).

## License

MIT. Consulta [LICENSE](LICENSE).
