# Evidencia de validación contra el toolchain oficial

**Curso:** CE-4301 Arquitectura de Computadores I  
**Estudiante:** Fabián Gutiérrez Jiménez — 2023141317  
**II Semestre 2026**

Entregable §3.5 (punto 2): comparación del codificador contra el toolchain RISC-V 32-bit.

> **Estado:** documentados y ejercitados **36 casos** en [`casos_prueba.txt`](casos_prueba.txt) (12 × 3).  
> Codificador: **24/36** coinciden con el toolchain (R e I). S y B pendientes de implementación.  
> Script: [`validate.sh`](validate.sh) — `./validate.sh` o `./validate.sh --markdown`.

## Toolchain y procedimiento

- Prefijo típico: `/opt/riscv` (o binarios `riscv64-unknown-elf-*` en `PATH`)
- Ensamblador / desensamblador: `riscv64-unknown-elf-as`, `riscv64-unknown-elf-objdump`
- Flags: `-march=rv32i -mabi=ilp32`
- Automatizado:

```bash
./validate.sh casos_prueba.txt --markdown
```

Por cada caso el script:
1. Ejecuta `./run.sh "<instruccion>"` y lee `HEX: 0x...`
2. Ensambla la misma instrucción con el toolchain
3. Extrae el encoding con `objdump -d`
4. Compara modelo vs objdump

Los valores en la verificación automática del profesor pueden diferir; la herramienta debe generalizar al subconjunto soportado.

---

## Formato R — 12 casos (3 por instrucción)

| Instrucción | HEX modelo | HEX objdump | ¿Coincide? |
|-------------|------------|-------------|------------|
| add x7, x20, x6 | 0x006a03b3 | 0x006a03b3 | sí |
| add x14, x26, x31 | 0x01fd0733 | 0x01fd0733 | sí |
| add x28, x15, x0 | 0x00078e33 | 0x00078e33 | sí |
| sub x5, x7, x18 | 0x412382b3 | 0x412382b3 | sí |
| sub x6, x28, x0 | 0x400e0333 | 0x400e0333 | sí |
| sub x31, x20, x13 | 0x40da0fb3 | 0x40da0fb3 | sí |
| and x25, x16, x22 | 0x01687cb3 | 0x01687cb3 | sí |
| and x22, x24, x4 | 0x004c7b33 | 0x004c7b33 | sí |
| and x21, x5, x18 | 0x0122fab3 | 0x0122fab3 | sí |
| or x18, x29, x9 | 0x009ee933 | 0x009ee933 | sí |
| or x19, x1, x23 | 0x0170e9b3 | 0x0170e9b3 | sí |
| or x23, x29, x27 | 0x01beebb3 | 0x01beebb3 | sí |

**Resultado R:** 12/12. Escenarios: distintos registros y uso de `x0`.

---

## Formato I — 12 casos (3 por instrucción)

| Instrucción | HEX modelo | HEX objdump | ¿Coincide? |
|-------------|------------|-------------|------------|
| addi x5, x25, 2035 | 0x7f3c8293 | 0x7f3c8293 | sí |
| addi x7, x27, 1974 | 0x7b6d8393 | 0x7b6d8393 | sí |
| addi x25, x16, 1392 | 0x57080c93 | 0x57080c93 | sí |
| andi x30, x1, -209 | 0xf2f0ff13 | 0xf2f0ff13 | sí |
| andi x8, x3, -1208 | 0xb481f413 | 0xb481f413 | sí |
| andi x27, x30, -882 | 0xc8ef7d93 | 0xc8ef7d93 | sí |
| lw x30, -1049(x14) | 0xbe772f03 | 0xbe772f03 | sí |
| lw x29, 8(x30) | 0x008f2e83 | 0x008f2e83 | sí |
| lw x25, 1875(x19) | 0x7539ac83 | 0x7539ac83 | sí |
| lb x25, -389(x27) | 0xe7bd8c83 | 0xe7bd8c83 | sí |
| lb x18, -1973(x17) | 0x84b88903 | 0x84b88903 | sí |
| lb x2, 1705(x9) | 0x6a948103 | 0x6a948103 | sí |

**Resultado I:** 12/12 en esta tabla (casos del kit / corridas previas).  
Con [`casos_prueba.txt`](casos_prueba.txt) vía `./validate.sh`: **24/36 OK** (todos los R e I de ese archivo). Ver también [`validacion_resultado.md`](validacion_resultado.md).

### Pendiente (fallan en validate.sh hasta implementar)

| Formato | Instrucciones | Casos en casos_prueba.txt |
|---------|---------------|---------------------------|
| S | sw, sb | 6 (positivo / negativo / límite) |
| B | beq, bne | 6 (positivo / negativo / límite) |
| **Total objetivo** | 12 instrucciones | **36** |
