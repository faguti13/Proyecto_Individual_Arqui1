# Documentación técnica

**Curso:** CE-4301 Arquitectura de Computadores I  
**Proyecto individual** — Codificador Educativo de Instrucciones RISC-V  
**Estudiante:** Fabián Gutiérrez Jiménez — 2023141317  
**II Semestre 2026**

> **Estado actual:** implementados los formatos **R** (`add`, `sub`, `and`, `or`) e **I** (`addi`, `andi`, `lw`, `lb`).  
> Los formatos S y B quedan para siguientes iteraciones; el ejemplo de salida S/B se añadirá cuando estén implementados.

La evidencia tabular de comparación contra el toolchain está en [`VALIDACION.md`](VALIDACION.md).  
La preparación mínima para `./run.sh` está en [`README.md`](README.md).

---

## 1. Instrucciones soportadas y campos de codificación

### Fase R (implementada)

| Mnemónico | Formato | opcode `[6:0]` | funct3 `[14:12]` | funct7 `[31:25]` |
|-----------|---------|----------------|------------------|------------------|
| `add` | R | `0110011` (OP) | `000` | `0000000` |
| `sub` | R | `0110011` (OP) | `000` | `0100000` |
| `and` | R | `0110011` (OP) | `111` | `0000000` |
| `or`  | R | `0110011` (OP) | `110` | `0000000` |

**Cómo se obtuvieron los campos:** del manual oficial *The RISC-V Instruction Set Manual, Volume I: User-Level ISA*, Document Version 20191213 (Waterman y Asanović), tabla de instrucciones del conjunto base RV32I, opcode `OP` (ALU registro-registro).

Disposición de bits del formato R:

```
31        25 24    20 19    15 14  12 11     7 6      0
+-----------+--------+--------+------+--------+--------+
|  funct7   |  rs2   |  rs1   |funct3|   rd   | opcode |
+-----------+--------+--------+------+--------+--------+
```

Ensamblado:

```text
word = (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
```

### Fase I (implementada)

| Mnemónico | Formato | opcode `[6:0]` | funct3 `[14:12]` | Notas |
|-----------|---------|----------------|------------------|-------|
| `addi` | I | `0010011` (OP-IMM) | `000` | `imm[11:0]` en bits `[31:20]` |
| `andi` | I | `0010011` (OP-IMM) | `111` | inmediato con signo (p. ej. negativos) |
| `lw` | I | `0000011` (LOAD) | `010` | sintaxis `rd, imm(rs1)` |
| `lb` | I | `0000011` (LOAD) | `000` | carga de byte con extensión de signo |

**Fuente:** mismo manual ISA Vol. I, opcodes `OP-IMM` y `LOAD`.

Disposición de bits del formato I:

```
31              20 19    15 14  12 11     7 6      0
+-----------------+--------+------+--------+--------+
|    imm[11:0]    |  rs1   |funct3|   rd   | opcode |
+-----------------+--------+------+--------+--------+
```

Ensamblado:

```text
word = ((imm & 0xFFF) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
```

### Pendientes (subconjunto del enunciado)

| Mnemónico | Formato previsto |
|-----------|------------------|
| `sw`, `sb` | S |
| `beq`, `bne` | B |

La herramienta debe generalizar a **cualquier** combinación válida de registros/inmediatos del subconjunto soportado, no solo a los casos documentados en la validación manual.

---

## 2. Arquitectura del código

Archivo principal: [`encoder_skeleton.py`](encoder_skeleton.py).  
Punto de entrada fijo: [`run.sh`](run.sh) → `python3 encoder_skeleton.py "<instruccion>"`.

```
argv "<instrucción>"
        │
        ▼
  split_mnemonic  →  mnemónico + operandos
        │
        ├── R_TYPE  → parse_r_operands → pack_r
        ├── I_ARITH → parse_i_arith_operands (rd, rs1, imm) → pack_i (OP-IMM)
        ├── I_LOAD  → parse_i_load_operands (rd, imm(rs1)) → pack_i (LOAD)
        └── pendiente / desconocida → error
        │
        ├─► explain_instruction  (desglose visual R o I)
        └─► print "HEX: 0x........"
```

Decisiones de diseño:

- Tablas `R_TYPE`, `I_TYPE_ARITH` e `I_TYPE_LOAD` centralizan opcode/funct3(/funct7).
- Inmediatos I: 12 bits con signo (−2048…2047); en la palabra se guardan como `imm & 0xFFF`.
- Loads: parseo de la forma ensamblador `imm(rs1)`.
- `main` captura errores; si la codificación tiene éxito, siempre imprime `HEX:` en el formato exigido.

---

## 3. Ejemplos de salida explicativa

Cuando existan S y B se documentará un ejemplo por esos formatos (requisito §3.5: una por R, I, S, B).

### Formato R

```text
$ ./run.sh "add x5, x6, x7"
Instrucción: add x5, x6, x7
Formato:     R
Codificación: 0x007302b3
Binario 32:   00000000011100110000001010110011
Campos:       0000000|00111|00110|000|00101|0110011
              funct7 | rs2 | rs1 | f3 |  rd | opcode

Desglose de campos:
  funct7   bits [31:25]  bin=0000000  dec=0      | distingue operaciones (p. ej. add vs sub)
  rs2      bits [24:20]  bin=00111  dec=7      | segundo registro fuente (x7)
  rs1      bits [19:15]  bin=00110  dec=6      | primer registro fuente (x6)
  funct3   bits [14:12]  bin=000  dec=0      | selecciona la operación dentro del opcode OP (add)
  rd       bits [11: 7]  bin=00101  dec=5      | registro destino (x5)
  opcode   bits [ 6: 0]  bin=0110011  dec=51     | OP = 0110011: ALU registro-registro

Semántica: x5 ← x6 + x7
HEX: 0x007302b3
```

### Formato I

```text
$ ./run.sh "addi x5, x25, 2035"
Instrucción: addi x5, x25, 2035
Formato:     I
Codificación: 0x7f3c8293
Binario 32:   01111111001111001000001010010011
Campos:       011111110011|11001|000|00101|0010011
              imm[11:0] | rs1 | f3 |  rd | opcode

Desglose de campos:
  imm      bits [31:20]  bin=011111110011  dec=2035   | inmediato de 12 bits con signo (valor = 2035)
  rs1      bits [19:15]  bin=11001  dec=25     | registro base / fuente (x25)
  funct3   bits [14:12]  bin=000  dec=0      | selecciona la operación (addi)
  rd       bits [11: 7]  bin=00101  dec=5      | registro destino (x5)
  opcode   bits [ 6: 0]  bin=0010011  dec=19     | OP-IMM = 0010011: ALU con inmediato

Semántica: x5 ← x25 + 2035
HEX: 0x7f3c8293
```

---

## 4. Evidencia de comparación contra la herramienta oficial

Ver [`VALIDACION.md`](VALIDACION.md) y el log generado por [`validate.sh`](validate.sh). Los **36 casos** del enunciado están en [`casos_prueba.txt`](casos_prueba.txt) (3 escenarios por instrucción: típico/positivo/negativo/límite según el formato).

```bash
./validate.sh                 # compara modelo vs objdump
./validate.sh --markdown      # escribe validacion_resultado.md
```

Estado actual de esa corrida: **24/36 OK** (R e I). Los 12 de S/B fallan hasta implementar esos formatos; los 36 ensamblan correctamente con el toolchain.

---

## 5. Instalación del toolchain utilizado

Se usó [riscv-gnu-toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain), clonado y compilado en **WSL (Ubuntu)**, con prefijo `/opt/riscv`.

**Recomendación de entorno:** Linux nativo o WSL. Compilar e instalar el toolchain en Windows “puro” (CMD/PowerShell sin capa Unix) no es el flujo habitual; el proyecto oficial está pensado para un entorno tipo Unix (Linux/macOS/WSL).

**Nota sobre Bash:** el toolchain en sí no “solo corre en Bash”. `riscv64-unknown-elf-as` y `objdump` son binarios del sistema que se invocan desde cualquier shell en Linux/WSL (Bash, Zsh, etc.). Lo que sí depende de Bash/POSIX es:

- el punto de entrada del proyecto, [`run.sh`](run.sh) (`#!/usr/bin/env bash`);
- el proceso típico de *compilación* del toolchain (`configure` / `make`).

Uso para validación RV32I:

```bash
export PATH=/opt/riscv/bin:$PATH
riscv64-unknown-elf-as -march=rv32i -mabi=ilp32 -o caso.o caso.s
riscv64-unknown-elf-objdump -d caso.o
```

---

## 6. Instalación / preparación de esta herramienta

Ver [`README.md`](README.md): Python 3, `chmod +x run.sh`, entorno Linux/WSL recomendado. Sin dependencias `pip`.

Invocación para verificación automática (§3.4):

```bash
./run.sh "<instruccion>"
```

---

## 7. Herramientas y declaración de uso de IA

En el desarrollo de este proyecto se utilizó **Cursor** como entorno de desarrollo asistido por IA (edición de código, documentación y apoyo en la implementación). El diseño, la validación contra el toolchain RISC-V y la responsabilidad del contenido entregado corresponden al estudiante.

---

## Referencias

1. Andrew Waterman y Krste Asanović. *The RISC-V Instruction Set Manual, Volume I: User-Level ISA*, Document Version 20191213. RISC-V Foundation, 2019.
2. Especificación del Proyecto Individual — CE-4301 Arquitectura de Computadores I.
3. [riscv-collab/riscv-gnu-toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain).
