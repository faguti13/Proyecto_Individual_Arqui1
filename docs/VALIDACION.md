# Evidencia de validación contra el toolchain oficial

**Curso:** CE-4301 Arquitectura de Computadores I  
**Estudiante:** Fabián Gutiérrez Jiménez — 2023141317  
**II Semestre 2026**

Entregable §3.5 (punto 2): comparación del codificador contra el toolchain RISC-V 32-bit.

> **Estado:** **36/36 casos OK** — subconjunto completo (12 instrucciones × 3 escenarios del kit).  
> Referencia: [`vectores_ejemplo.txt`](vectores_ejemplo.txt).

## Toolchain y procedimiento

- Prefijo típico: `/opt/riscv` (o binarios `riscv64-unknown-elf-*` en `PATH`)
- Ensamblador / desensamblador: `riscv64-unknown-elf-as`, `riscv64-unknown-elf-objdump`
- Flags: `-march=rv32i -mabi=ilp32`

Por cada caso:

1. Obtener la codificación del modelo: `./run.sh "<instruccion>"` → línea `HEX: 0x...`
2. Ensamblar la misma instrucción en un `.s` mínimo con el toolchain
3. Extraer el encoding de referencia con `objdump -d`
4. Comparar ambos valores hexadecimales

Ejemplo (instrucción tipo R):

```bash
export PATH=/opt/riscv/bin:$PATH
printf '.text\n\tadd x5, x6, x7\n' > caso.s
riscv64-unknown-elf-as -march=rv32i -mabi=ilp32 -o caso.o caso.s
riscv64-unknown-elf-objdump -d caso.o
./run.sh "add x5, x6, x7"
```

Los valores en la verificación automática del profesor pueden diferir; la herramienta generaliza al subconjunto soportado.

**Nota B-type:** al validar saltos con `as`, el destino del branch debe existir en la sección `.text` (p. ej. etiqueta + `.space`); el codificador recibe el offset numérico directamente, como indica el enunciado.

---

## Resumen por formato

| Formato | Instrucciones | Casos | Resultado |
|---------|---------------|-------|-----------|
| R | add, sub, and, or | 12 | 12/12 |
| I | addi, andi, lw, lb | 12 | 12/12 |
| S | sw, sb | 6 | 6/6 |
| B | beq, bne | 6 | 6/6 |
| **Total** | **12** | **36** | **36/36** |

---

## Formato R — 12 casos (kit)

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

---

## Formato I — 12 casos (kit)

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

---

## Formato S — 6 casos (kit)

| Instrucción | HEX modelo | HEX objdump | ¿Coincide? |
|-------------|------------|-------------|------------|
| sw x31, -411(x23) | 0xe7fba2a3 | 0xe7fba2a3 | sí |
| sw x16, 1774(x31) | 0x6f0fa723 | 0x6f0fa723 | sí |
| sw x31, -1773(x27) | 0x91fda9a3 | 0x91fda9a3 | sí |
| sb x18, 1701(x20) | 0x6b2a02a3 | 0x6b2a02a3 | sí |
| sb x6, 72(x28) | 0x046e0423 | 0x046e0423 | sí |
| sb x28, 1439(x11) | 0x59c58fa3 | 0x59c58fa3 | sí |

---

## Formato B — 6 casos (kit)

| Instrucción | HEX modelo | HEX objdump | ¿Coincide? |
|-------------|------------|-------------|------------|
| beq x30, x4, -80 | 0xfa4f08e3 | 0xfa4f08e3 | sí |
| beq x31, x23, 16 | 0x017f8863 | 0x017f8863 | sí |
| beq x26, x9, 60 | 0x029d0e63 | 0x029d0e63 | sí |
| bne x5, x0, 60 | 0x02029e63 | 0x02029e63 | sí |
| bne x12, x15, 16 | 0x00f61863 | 0x00f61863 | sí |
| bne x17, x22, 20 | 0x01689a63 | 0x01689a63 | sí |

**Resultado global:** 36/36 coinciden (vectores de [`vectores_ejemplo.txt`](vectores_ejemplo.txt) y casos adicionales documentados manualmente).
