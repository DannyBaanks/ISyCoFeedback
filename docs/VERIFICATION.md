# Verificación local de la fusión — 2026-10-21

Rama: `codex/feedback-unified-core`. Versión: `2.0.0a1`. Base de Feedback: `cd1593aa217fe103f073f53af772986a369f6e99`.

## Resultados

- Suite completa: **179 passed** en Linux/Python 3.12.
- Demo real local: reparación **PASS** tras dos verificaciones; propuesta fuera de alcance **DENIED**; tres fallos **REPAIR_EXHAUSTED**; auditoría **VALID**; modificación de recibo **INVALID**.
- Demo documental: confianza desconocida, rechazo explícito del reviewer sintético y evidencia **VALID**.
- Wheel construido y probado después de instalación offline en directorio temporal, fuera del árbol fuente.
- Ruff, reglas F: sin incidencias. `git diff --check`: sin errores.
- Búsqueda de integraciones retiradas en código, pruebas y documentación del producto: sin coincidencias.

Logs completos: `verification-suite.log`, `verification-demo.log`, `verification-documents.log`, `verification-wheel.log`, `verification-installed-wheel.log`, `verification-lint.log`. Resumen estructurado: `verification-results.json`.

Los comandos del producto se ejecutaron dentro de bubblewrap, con red deshabilitada y sin montar el home del usuario. Sólo el checkout del producto era escribible, además del /tmp aislado. Las librerías Python disponibles se montaron de sólo lectura; no hubo llamadas a proveedores ni instalaciones desde Internet.

## Revisión independiente

Un revisor inspeccionó el diff sin ejecutar ni editar el producto. Se reprodujeron y corrigieron: rollback ante excepciones, limpieza de procesos tras interrupción, replay con evidencia faltante, recuperación de ambos backends, claves primarias del backend de memoria y vinculación de políticas documentales a la evidencia.

La revisión posterior comprobó recuperación repetible de backups pendientes, filtrado por repositorio, rechazo de symlinks en directorios padres y rechazo de contenido con secretos configurados antes de persistir backups. No quedaron bloqueantes materiales en esos puntos inspeccionados.

## Límites

Las demos usan fixtures y propuestas fijas declaradas. No prueban reparación con IA real, GitLab Duo, despliegue, canales externos, PDF real ni Windows. El código de respaldo y los proveedores siguen sujetos a las licencias indicadas en PROVENANCE. Los hashes no autentican al generador ni una revisión humana.

El CI añadido no se ejecutó en GitHub: los cambios permanecen locales. Los proyectos originales se conservaron; OTP recibió la licencia MIT solicitada y Trustworthy ya tenía MIT. Los archivos fuente copiados procedían de working trees modificados, documentados en el manifiesto de migración.
