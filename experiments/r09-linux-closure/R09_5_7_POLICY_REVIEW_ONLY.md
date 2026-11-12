# Engine YT — R09-5/6/7, laboratorio de cierre Linux (REVIEW ONLY)

**No contiene ni reemplaza T21-R09. No permite integrar código, renderizar ni publicar.**

Esta rama se prepara mientras Claude consolida su rama local
\`work/t21-r09-consolidation\`. Los commits de Claude declarados por el usuario
(\`9ef8e95\`, \`b678234\`, \`9e4f1f0\`, \`92c01c9\`) **no están incluidos ni revalidados aquí**.

## R09-5: clasificación de los resultados

Peligro: una aplicación puede salir legítimamente con estado 127, igual que un
lanzador que use 127 para expresar error de preparación. Un único código de
salida no sirve para distinguir los dos hechos.

En este laboratorio Linux de un solo hilo:

- Se crea un pipe con \`O_CLOEXEC\` exclusivamente para los errores
  pre-\`exec\`.
- El proceso hijo establece \`PR_SET_PDEATHSIG(SIGKILL)\`.
- Comprueba de nuevo la identidad de su padre después de \`prctl\`.
- Solo después intenta \`execv\`.
- Un error de \`prctl\` emite \`PDEATHSIG:<errno>\`, uno de identidad
  \`PARENT_CHANGED:<errno>\` y otro de \`execv\`, \`EXECV:<errno>\`.
- La salida de un comando que ejecutó \`execv\` se atribuye al comando,
  incluido \`127\`.
- Los errores de protocolo y los plazos agotados producen un resultado separado
  y se cierran sin acreditar el test.
- Se mata/recolecta únicamente al **hijo directamente creado por el laboratorio**.

**Importante:** la inyección de \`EPERM\` y \`ENOSYS\` es una prueba del
protocolo. No equivale a una denegación real por seccomp del kernel. Se ha añadido después una prueba de seccomp real sobre un proceso desechable. Para
calificar el supervisor T21 se requiere repetirla sobre su código, no este prototipo; también y revisar las
carreras de fallo antes de \`execv\`; el pipe por sí solo no es prueba formal.

Este código usa \`os.fork\` en una aplicación monohilo; no se propone incorporarlo
sin cambios a un supervisor Python con múltiples hilos.

## R09-6: política estricta de matrices

El verificador \`matrix_policy.py\` comprueba **metadatos declarados**, no
ejecuta las suites del paquete original. Exige cuatro recibos:
\`official=634\`, \`additional=49\`, \`r07=13\`, \`r09=14\`.
Solo admite cantidades enteras, cuatro identidades distintas, sumas consistentes,
códigos de salida 0 y hashes SHA-256 de archivos de log legibles dentro de la
raíz suministrada. Nunca convierte \`SKIP\` ni \`XFAIL\` en \`PASS\`.

Los recuentos atribuidos por el usuario a R09 implican:

| Modalidad | PASS | SKIP | Interpretación |
|---|---:|---:|---|
| root | 710 | 0 | Completitud local, **no** calificación |
| uid 65534 | 708 | 2 | **BLOCKED**, no 710 PASS |

Los tests que generan recibos falsos están etiquetados
\`SYNTHETIC_POLICY_TEST\`. Que pasen **no** prueba 710 casos reales ni
authentica automáticamente los logs. El modo \`OBSERVED_NATIVE\` requiere una
cadena externa de custodia, y aun así no implica autoridad de producción.

## R09-7: propuesta de contención integral, sin implementación

Condiciones necesarias para intentar calificar una vía Linux:

1. **cgroup v2 delegado y exclusivo** por ejecución; si existe solo cgroup v1,
   si la delegación está ausente o no se puede demostrar, **BLOCKED**.
2. Crear el proceso inicial **dentro de su cgroup antes de ejecutar código
   no fiable**, por ejemplo con una implementación nativa calificada de
   \`CLONE_INTO_CGROUP\` donde sea compatible, o lanzamiento suspendido con
   barreras verificables de alta fidelidad.
3. **Custodio independiente** del supervisor con custodia autenticada del
   cgroup, autoridad acotada sobre ese cgroup y registro persistente de la
   identidad de la ejecución. La muerte del supervisor activa limpieza y
   recuperación por el custodio.
4. Terminación mediante \`cgroup.kill\` exclusivamente sobre el cgroup
   verificado del trabajo, sin enumerar PIDs globales ni usar coincidencias
   de nombres. Comprobar \`cgroup.events\` y \`populated=0\`; registrar y
   bloquear si hay procesos persistentes.
5. Identificar el cgroup por estructura delegada, identificadores no
   reutilizables sin validación y comprobaciones de propiedad/ancestría.
   Evitar carreras de reutilización de PID; usar descriptores seguros y
   verificaciones del espacio de nombres correspondiente.
6. Fallos del custodio, pérdida de delegación, límites temporales, errores de
   eliminación, fallback a cgroup v1, cambios de credenciales, \`setsid\`,
   \`fork\` y fugas de FD deben producir estado **NO-GO/BLOCKED**, nunca PASS.
7. Una solución dependiente de un solo custodio no garantiza persistencia ante
   muerte simultánea del custodio y supervisor; exigir un nivel superior
   independiente de recuperación antes de declarar custodia integral.
8. Tests nativos para fallos en cada límite: antes de creación, tras unión al
   cgroup, tras fork/setsid/cambio de UID, muerte del supervisor, muerte del
   custodio, pérdida del stdout, limpieza parcial, cgroup v1/v2, SIGKILL,
   reuso de identidad, concurrencia y reinicios.

**Fuera de alcance de este paquete:** implementación de cgroup v2, ejecución
nativa del supervisor T21-R09, demostración de seccomp real, cualificación
Windows, Root matrix real, prueba de durabilidad física o promoción de gates.

## Reproducir la unidad Linux

\`\`\`sh
cd experiments/r09-linux-closure
python3 -m unittest -v test_exit127_guard test_matrix_policy
\`\`\`

El CI revisa el módulo de referencia. Las pruebas unitarias que simulan
matrices NO deben sumarse a los recuentos de R09.

## Bloqueos heredados

- \`R17/E5B4D = NO-GO\`
- \`TB09/G3 = BLOCKED\`
- \`rendering_go=false\`, \`publishing_go=false\`
- \`T21-R09\` y commits de Claude pendientes de paquete final y revisión externa.
- El Gate V8 original Windows permanece sin ejecutar en este laboratorio.

**Prohibido:** usar estos resultados como sustituto de la auditoría de Claude
o de las pruebas 634 + 49 + 13 + 14 de T21.


## Evidencia CI nativa del laboratorio de referencia — 12 noviembre 2026

GitHub Actions \`ubuntu-24.04\`, Linux x86_64, Python 3, rama
\`review/engineyt-r09-linux-closure-r5-r7-20261112\`.

- Primera campaña: run \`43143903822\`, **33/34 PASS + 1 ERROR**; el
  agregador lanzaba \`TypeError\` ante un nombre de suite no hashable.
- Corrección aislada: run \`43143981805\`, **34/34 PASS** con UID 1001
  y **34/34 PASS** con UID 0.
- Denegación kernel seccomp y modalidad UID 65534 incorporadas: run
  \`43144282009\`, **35/35 PASS** en cada UID 1001, 0 y 65534.
  El test \`test_real_kernel_seccomp_denies_prctl\` aplica un filtro
  seccomp-BPF *solo al hijo de laboratorio* y observa que el kernel
  devuelve \`EPERM\` para \`PR_SET_PDEATHSIG\`.
- Endurecimiento de lectura de logs ante FIFO, symlinks, límites de tamaño
  y rutas anidadas: run \`43144576938\`, **41/41 PASS** en cada modalidad,
  **123/123 PASS**, 0 errores y 0 pruebas omitidas, log recuperado.
- El test del filtro seccomp se limita a x86_64 y no valida una política
  de aislamiento general; no es un sandbox ni la campaña de Claude.

En los 123 casos de la última ejecución, **26 por modalidad son pruebas
de política del agregador con datos sintéticos**, y **15 por modalidad son
pruebas del lanzador de referencia**. No deben contabilizarse como 123
ejecuciones de T21-R09.

La lectura de logs mediante descriptores evita volver a abrir por nombre
tras la validación del tipo de archivo. La prueba de FIFO sin escritor
comprueba explícitamente que la lectura no se bloquee.

**Bloqueos no resueltos:** custodia de descendientes tras cambios de
credenciales, cgroup v2 delegado y custodia externa bajo fallos simultáneos.
R17/E5B4D NO-GO, TB09/G3 BLOCKED. Sin promoción a producción.


## R09-7 — Evidencia nativa de límites estructurales de PDEATHSIG

Se añadió \`test_kernel_semantics.py\` en copia aislada, sin tocar el
supervisor real. La ejecución \`43145127555\` de GitHub Actions pasó:

- UID 1001: 41 pruebas R09-5/6 + 1 prueba real de \`fork\`, todas PASS.
- UID 0: 41 pruebas R09-5/6 + 2 comprobaciones de kernel
  (\`fork\` y pérdida tras \`setuid(65534)\`), todas PASS.
- UID 65534: 41 pruebas R09-5/6 + 1 prueba real de \`fork\`,
  todas PASS.

**Total de esta campaña: 127/127 PASS**, 0 FAIL, 0 SKIP.

Lo observado es el *contraejemplo de seguridad*: la señal de muerte del padre
no se hereda por el nieto, y el cambio de UID puede desactivar PDEATHSIG.
Por tanto, estas pruebas **no convierten** la custodia de descendientes en PASS.
Refuerzan el requisito de un cgroup v2 delegado y un custodio externo, aún
no validados sobre T21-R09.

La rutina de pruebas solo envía señales a hijos propios todavía no recolectados;
tras \`waitpid\` no intenta señalizar PIDs potencialmente reutilizados.
