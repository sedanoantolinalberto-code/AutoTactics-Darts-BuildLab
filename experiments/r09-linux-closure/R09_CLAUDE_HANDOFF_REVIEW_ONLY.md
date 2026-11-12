# Handoff para revisión cruzada de Claude — Engine YT T21-R09

**Documento de coordinación.** No sustituye el bundle ni el ZIP final de
\`work/t21-r09-consolidation\`. Este repo de BuildLab no incluye el código
privado/local de T21. Mantener las ramas independientes hasta finalizar la
comparación.

## Evidencia comunicada por Claude (no revalidada en este repo)

- \`9ef8e95\` R09-1: FIFO/WAL, casos antes/después.
- \`b678234\` R09-2: limpieza en host cgroup v1.
- \`9e4f1f0\` R09-3: fixture truncado-antes-de-escritura y timeout intermitente.
- \`92c01c9\` R09-4: contabilidad de SKIP/XFAIL.

Claude tenía pendientes R09-5, R09-6, R09-7, matrices reales root/uid65534 y
entrega final con hashes/bundle. No atribuirle avances posteriores que no haya
declarado con pruebas.

## Evidencia independiente *nueva*, exclusivamente de referencia

PR borrador: https://github.com/sedanoantolinalberto-code/AutoTactics-Darts-BuildLab/pull/16

- R09-5: protocolo de pipe CLOEXEC para distinguir \`TEST_EXITED(127)\`,
  \`PDEATHSIG_SETUP_FAILED\`, \`EXEC_SETUP_FAILED\`, \`PARENT_IDENTITY_CHANGED\`.
- \`PR_SET_PDEATHSIG\` denegado **realmente por un filtro seccomp-BPF del
  kernel**, no solo por mock. Linux x86_64.
- R09-6: política de matrices y hashes de logs con lectura \`openat\` anclada
  por descriptores; rechaza FIFO, symlink, entrada malformada, omisiones y
  resultados XFAIL.
- R09-7: documentación de los prerrequisitos para cgroup v2 delegado, unión
  previa a la ejecución, custodio externo y verificación de \`populated=0\`.
- Nativo: nieto no hereda PDEATHSIG tras \`fork\`, y \`setuid(65534)\` puede
  borrar PDEATHSIG.
- CI Linux **127/127 PASS** como prueba del laboratorio, IDs y SHAs en
  \`R09_LINUX_REFERENCE_EVIDENCE.json\`. **Cero** suites oficiales T21
  ejecutadas desde este PR.

## Acciones concretas para cerrar T21-R09

1. Cotejar el diff completo de los cuatro commits anteriores y R09-5/6/7
   locales de Claude, recuperando su identidad Git y el ZIP/bundle final.
2. Evaluar la posibilidad de incorporar el patrón de canal de error
   pre-exec sin una ventana de falsos positivos antes de \`execve\`.
   En el supervisor real se deberá evitar \`fork\` inseguro desde un proceso
   multihilo; el laboratorio NO es una implementación productiva.
3. Ejecutar **las suites reales T21** (634 oficiales, 49 adicionales, 13
   R07, 14 R09) separando logs por suite y UID. Referencia documental:
   root 710 PASS, UID 65534 708 PASS + 2 SKIP, este último **BLOCKED**.
   No copiar estos números a un informe nuevo sin ejecuciones verificadas.
4. Registrar cualquier fallo/timeout/interrupción como FAIL/BLOCKED, nunca
   omitir una prueba del denominador.
5. Reproducir los 11 adversariales originales de Claude y registrar de
   manera transparente los resultados incompatibles con la política de
   terminación insegura de procesos.
6. Probar que no queden artefactos residuales de cgroups v1/v2; si la
   delegación v2 no existe, no declarar custodia completa.
7. Si R09-7 sigue siendo propuesta, mantener contención total en
   BLOCKED. Un prototipo alternativo nunca puede promover el gate por
   analogía.
8. Entregar commit exacto, \`git bundle\`, ZIP con CRC, hashes SHA-256,
   diffs, logs, inventario de SKIP, informe en español y tabla de
   limitaciones que distinga \`PASS\`, \`PASS_LIMITED\`, \`BLOCKED\`, \`NO-GO\`.

## Frontera de integración

No hacer merge automático ni modificar las gates:
\`R17/E5B4D=NO-GO\`, \`TB09/G3=BLOCKED\`, renderizado/publicación deshabilitados.

El laboratorio Windows B31–B33 (PR borrador #15) se contrasta por separado;
sus 9 pruebas Windows NO son el Gate V8 de 17 pruebas del supervisor real.
