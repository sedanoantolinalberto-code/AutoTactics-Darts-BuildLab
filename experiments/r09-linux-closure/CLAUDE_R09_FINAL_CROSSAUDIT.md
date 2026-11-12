# Engine YT — Claude T21-R09 final vs. Linux reference PR #16

**Fecha:** 2026-11-12. **Estado: revisión cruzada / NO MERGE.**

Fuentes: informe entregado por Claude \`INFORME_T21_R09.md\`
y ZIP \`EngineYT_T21_R09_Claude_Final_ReviewOnly.zip\` **no
verificado criptográficamente en esta sesión**, debido a error de
ejecución de Python y del contenedor. Lo siguiente no constituye
validación del bundle Git de Claude ni de su código.

## Resultado declarado por Claude (no reejecutado aquí)

- Rama \`work/t21-r09-consolidation\`; HEAD
  \`a19c7492324ed842ac81d68f15ff1c84d237cbd3\`;
  base \`34f75094f9eaf6707fa1a99887cdae7ec043ca62\`.
- R09-1 FIFO/WAL PASS; R09-2 cgroup v1 PASS_LIMITED; R09-3
  escritura atómica del fixture PASS limitado por muestra estadística;
  R09-4 contabilidad PASS_LIMITED; R09-5 127/PDEATHSIG
  PASS_LIMITED; R09-6 verificación estricta de logs PASS_LIMITED;
  R09-7 solo propuesta, BLOCKED.
- Matriz root declarada: oficial 634 PASS + adicionales 49 PASS +
  R07 13 PASS + R08 6 PASS/5 FAIL + R09 de Claude 41 PASS =
  **743 PASS / 5 FAIL / 748 total**.
- Matriz UID 65534 declarada: oficial 632 PASS/2 SKIP +
  adicionales 49 PASS + R07 13 PASS + R08 5 PASS/5 FAIL/1 SKIP +
  R09 de Claude 40 PASS/1 SKIP =
  **739 PASS / 5 FAIL / 4 SKIP / 748 total**.
- Los 14 casos R09 de Codex no estaban disponibles para Claude y no
  son intercambiables con sus 41 nuevos tests.
- R08: 2 fallos de EXP-3 no integrado; 1 discrepancia de SKIP
  superada por la nueva política; 2 discrepancias de esquema
  (\`failure_class\`/\`setup_failure\` y prefijo \`setup:\`).
  Las dos discrepancias de esquema requieren revisar consumidores
  de logs y no deben ocultarse como «PASS».
- \`fork()+setsid()\`, pérdida de PDEATHSIG tras \`setuid\`,
  cgroup v2, custodio externo, H2/H3 y causa de SIGKILL histórico
  siguen abiertos.

## Hallazgo F1 de Claude en PR #16: CONFIRMADO / MITIGADO EN LABORATORIO

La implementación anterior del validador verificaba hash SHA-256 y sumas
**declaradas**, pero no extraía PASS/SKIP/XFAIL del contenido del log.
Por eso un recibo que decía «todo PASS» podía superar la política
con logs que dijeran «skipped». El hecho de que ambos tuvieran SHA
correcto no acreditaba veracidad de los recuentos.

Corrección reference-only:
- Esquema nuevo \`engineyt-r09-suite-receipts/0.2\`, sin fallback a v0.1.
- Cada log debe ser JSON Lines, una fila
  \`{"schema":"engineyt-r09-case-result/0.1","case_id":"...","status":"PASS|FAIL|ERROR|SKIP|XFAIL"}\`
  por prueba, sin IDs duplicados ni campos adicionales.
- Lectura y hash desde el **mismo descriptor anclado**; un log
  ausente, parcial, FIFO, symlink o modificado se rechaza.
- Recuentos derivados directamente de cada caso; un total
  autodeclarado distinto provoca \`DECLARED_COUNTS_DISAGREE_WITH_LOG\`.
- Campos JSON duplicados rechazados (por ejemplo, \`"status":"SKIP"\`
  seguido de \`"status":"PASS"\`).
- Un recibo marcado \`OBSERVED_NATIVE\` **no** puede producir PASS:
  sin autenticación externa del ejecutor se devuelve
  \`BLOCKED_UNATTESTED_NATIVE_PROVENANCE\`, incluso si
  el log y el recibo son internamente coherentes.

**Limitación:** ni esta versión ni un hash autocertificado demuestran
que un ejecutor real haya realizado el trabajo. Se necesita custodia
externa para aceptar prueba nativa.

## Hallazgo F2 de Claude: CORREGIDO EN LABORATORIO

\`TIMEOUT_OR_PROTOCOL_FAILURE\` mezclaba causas. El candidato distingue
\`TEST_TIMEOUT\` (hijo sigue activo al vencimiento),
\`SETUP_PIPE_EOF_MISSING\` (hijo reaped pero falta EOF) y
\`MALFORMED_SETUP_REPORT\` (datos de error excesivos).
Una prueba nativa del hijo lento y dos comprobaciones del clasificador
constituyen la evidencia, no el test del supervisor real.

## F3 y F4: SIGUEN ABIERTOS

- F3: un nieto con \`setsid\` puede sobrevivir a la muerte del líder.
  El laboratorio termina únicamente su hijo directo y no acredita
  contención integral. \`BLOCKED\`.
- F4: \`os.fork()\` en un programa potencialmente multihilo.
  Requiere un launcher aislado y verificado, no integración directa
  del prototipo. \`BLOCKED\`.

## Aclaración: «127/127 sin SKIP» vs. «1 SKIP en UID 65534»

La ejecución GitHub Actions \`43145127555\` seleccionó expresamente
**una sola prueba de kernel** para UID 65534:
\`test_grandchild_does_not_inherit_pdeathsig\`. No ejecutó la
prueba \`test_uid_drop_clears_pdeathsig\`, marcada
\`@skipUnless(os.geteuid()==0)\`. Por eso su log legítimamente
contiene 0 SKIP. Claude ejecutó la **clase completa** de pruebas como
UID 65534 y vio 1 SKIP. No hay contradicción matemática; ambas
campañas tienen alcances distintos. No usar la primera para afirmar
que las 43 pruebas ejecutadas por Claude fueron «43 PASS».

## Evidencia CI de las correcciones PR #16

- \`43149639661\`: 53 pruebas de referencia por UID + cuatro
  pruebas de kernel seleccionadas = **163 PASS**, 0 FAIL,
  0 SKIP.
- \`43149857202\`: 56 pruebas de referencia por UID + cuatro
  pruebas de kernel seleccionadas = **172 PASS**, 0 FAIL,
  0 SKIP. Incluye test adversarial F1 y clasificación F2.
- \`43150302615\`: 57 pruebas de referencia por UID + cuatro
  de kernel seleccionadas = **175/175 PASS**, 0 FAIL, 0 SKIP;
  job \`130957625846\`, código \`3717beb907f88aa62cb5e4cfb991ec63d26b3ad4\`.
  Se comprobó el log completo: rechazo de claves JSON duplicadas,
  bloqueo de los recibos \`OBSERVED_NATIVE\` no autenticados y
  las regresiones F1/F2.

Estas son **pruebas del laboratorio** (gran parte de matrices
sintéticas), no las 748 pruebas de T21.

## Estado y siguientes criterios de aceptación

1. Verificación externa real del ZIP de Claude (CRC, SHA-256,
   \`git bundle verify\`, \`git fsck\`, árbol Git exacto).
2. Conservar los 5 FAIL R08 en recuentos. Revisar compatibilidad
   de las dos diferencias de esquema con lectores originales.
3. Comparar el código nativo de R09-5 y el verificador R09-6 de Claude
   con estos prototipos; NO hacer merge automático entre ramas.
4. Ejecutar Gate V8 original solo cuando se recupere B23–B25.
5. Mantener \`R17/E5B4D = NO-GO\`, \`TB09/G3 = BLOCKED\`,
   contención integral BLOCKED, render/publicación deshabilitados.

**No release · No merge · No producción.**
