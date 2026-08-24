# Evidencia de validación contra el toolchain oficial

**Curso:** CE-4301 Arquitectura de Computadores I  
**Estudiante:** Fabián Gutiérrez Jiménez — 2023141317  
**II Semestre 2026**

Entregable §3.5 (punto 2): comparación del codificador contra el toolchain RISC-V 32-bit.

> **Estado:** documentados los **12 casos** del formato R (4 instrucciones × 3 escenarios).  
> Al completar I, S y B se ampliará a los **36 casos** exigidos (12 × 3).

## Toolchain y procedimiento

- Prefijo: `/opt/riscv`
- Ensamblador / desensamblador: `riscv64-unknown-elf-as`, `riscv64-unknown-elf-objdump`
- Flags: `-march=rv32i -mabi=ilp32`
- Por cada caso:
  1. `./run.sh "<instruccion>"` → línea `HEX: 0x...`
  2. Ensamblar la misma instrucción y obtener el encoding con `objdump -d`
  3. Comparar con el valor esperado en [`vectores_ejemplo.txt`](vectores_ejemplo.txt)

Los valores concretos de registros e inmediatos en la verificación automática del profesor pueden diferir; la herramienta debe generalizar a cualquier instrucción válida del subconjunto soportado.

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

**Resultado parcial:** 12/12 coinciden con el kit y con el toolchain oficial.  
Escenarios cubiertos en R: distintos registros y uso de `x0` (en R no hay inmediatos negativos).

### Pendiente

| Formato | Instrucciones | Casos |
|---------|---------------|-------|
| I | addi, andi, lw, lb | 12 |
| S | sw, sb | 6 |
| B | beq, bne | 6 |
| **Total objetivo** | 12 instrucciones | **36** |
