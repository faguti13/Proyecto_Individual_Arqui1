# Documentación técnica

**Curso:** CE-4301 Arquitectura de Computadores I  
**Proyecto individual** — Codificador Educativo de Instrucciones RISC-V  
**Estudiante:** Fabián Gutiérrez Jiménez — 2023141317  
**II Semestre 2026**

> **Estado actual:** implementados los **12 instrucciones** del subconjunto RV32I (formatos **R**, **I**, **S** y **B**).

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

### Fase S (implementada)

| Mnemónico | Formato | opcode `[6:0]` | funct3 `[14:12]` | Notas |
|-----------|---------|----------------|------------------|-------|
| `sw` | S | `0100011` (STORE) | `010` | sintaxis `rs2, imm(rs1)` |
| `sb` | S | `0100011` (STORE) | `000` | almacena byte en memoria |

**Fuente:** mismo manual ISA Vol. I, opcode `STORE`.

Disposición de bits del formato S (el inmediato de 12 bits se **parte**):

```
31        25 24    20 19    15 14  12 11     7 6      0
+-----------+--------+--------+------+--------+--------+
| imm[11:5] |  rs2   |  rs1   |funct3| imm[4:0]| opcode |
+-----------+--------+--------+------+--------+--------+
```

Ensamblado:

```text
imm12 = imm & 0xFFF
word = ((imm12 >> 5) << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | ((imm12 & 0x1F) << 7) | opcode
```

### Fase B (implementada)

| Mnemónico | Formato | opcode `[6:0]` | funct3 `[14:12]` | Notas |
|-----------|---------|----------------|------------------|-------|
| `beq` | B | `1100011` (BRANCH) | `000` | sintaxis `rs1, rs2, offset` (bytes, par) |
| `bne` | B | `1100011` (BRANCH) | `001` | offset relativo a PC de la instrucción |

**Fuente:** mismo manual ISA Vol. I, opcode `BRANCH`.

Disposición de bits del formato B (inmediato partido):

```
31 30     25 24    20 19    15 14  12 11     8 7 6      0
+--+---------+--------+--------+------+------+-+--------+
|12| 10:5   |  rs2   |  rs1   |funct3| 4:1  |11| opcode |
+--+---------+--------+--------+------+------+-+--------+
```

Ensamblado (`offset` en bytes, par):

```text
imm = offset & 0x1FFF
word = ((imm >> 12) & 1) << 31 | ((imm >> 5) & 0x3F) << 25 | (rs2 << 20)
     | (rs1 << 15) | (funct3 << 12) | ((imm >> 1) & 0xF) << 8 | ((imm >> 11) & 1) << 7 | opcode
```

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
        ├── S_TYPE  → parse_s_store_operands (rs2, imm(rs1)) → pack_s
        ├── B_TYPE  → parse_b_branch_operands (rs1, rs2, offset) → pack_b
        └── desconocida → error
        │
        ├─► explain_instruction  (desglose visual R, I, S o B)
        └─► print "HEX: 0x........"
```

Decisiones de diseño:

- Tablas `R_TYPE`, `I_TYPE_*`, `S_TYPE` y `B_TYPE` centralizan opcode/funct3(/funct7).
- Inmediatos: 12 bits con signo; en S y B el offset se reparte en campos no contiguos.
- Branches: offset en **bytes** (par), rango −4096…4094.
- Loads/stores: sintaxis ensamblador `imm(rs1)`; en S el primer operando es `rs2` (dato a guardar).
- `main` captura errores; si la codificación tiene éxito, siempre imprime `HEX:` en el formato exigido.

---

## 3. Ejemplos de salida explicativa (una por formato R, I, S, B)

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

### Formato S

```text
$ ./run.sh "sw x8, -4(x2)"
Instrucción: sw x8, -4(x2)
Formato:     S
Codificación: 0xfe812e23
Binario 32:   11111110100000010010111000100011
Campos:       1111111|01000|00010|010|11100|0100011
              imm[11:5] | rs2 | rs1 | f3 | imm[4:0] | opcode

Desglose de campos:
  imm[11:5] bits [31:25]  bin=1111111  dec=127    | parte alta del offset (inmediato completo = -4)
  rs2      bits [24:20]  bin=01000  dec=8      | registro fuente a almacenar (x8)
  rs1      bits [19:15]  bin=00010  dec=2      | registro base de dirección (x2)
  funct3   bits [14:12]  bin=010  dec=2      | selecciona la operación (sw)
  imm[4:0] bits [11: 7]  bin=11100  dec=28     | parte baja del offset (inmediato completo = -4)
  opcode   bits [ 6: 0]  bin=0100011  dec=35     | STORE = 0100011: almacenamiento en memoria

Semántica: mem[x2 + -4] ← x8  (palabra (32 bits))
HEX: 0xfe812e23
```

### Formato B

```text
$ ./run.sh "beq x31, x23, 16"
Instrucción: beq x31, x23, 16
Formato:     B
Codificación: 0x017f8863
Binario 32:   00000001011111111000100001100011
Campos:       0|000000|10111|11111|000|1000|0|1100011
              imm12|imm10:5| rs2 | rs1 | f3 |imm4:1|i11| opcode

Desglose de campos:
  imm[12]  bits [31:31]  bin=0  dec=0      | bit alto del offset (offset bytes = 16)
  imm[10:5] bits [30:25]  bin=000000  dec=0      | parte media del offset de salto
  rs2      bits [24:20]  bin=10111  dec=23     | segundo registro comparado (x23)
  rs1      bits [19:15]  bin=11111  dec=31     | primer registro comparado (x31)
  funct3   bits [14:12]  bin=000  dec=0      | igual (beq)
  imm[4:1] bits [11: 8]  bin=1000  dec=8      | parte baja del offset de salto
  imm[11]  bits [ 7: 7]  bin=0  dec=0      | bit intermedio del offset
  opcode   bits [ 6: 0]  bin=1100011  dec=99     | BRANCH = 1100011: salto condicional

Semántica: si x31 == x23, saltar PC + 16 bytes (destino relativo a la instrucción)
HEX: 0x017f8863
```

---

## 4. Evidencia de comparación contra la herramienta oficial

Ver [`VALIDACION.md`](VALIDACION.md) y el log generado por [`validate.sh`](validate.sh). Los **36 casos** del enunciado están en [`casos_prueba.txt`](casos_prueba.txt) (3 escenarios por instrucción: típico/positivo/negativo/límite según el formato).

```bash
./validate.sh                 # compara modelo vs objdump
./validate.sh --markdown      # escribe validacion_resultado.md
```

Estado actual de esa corrida: **36/36 OK** (subconjunto completo). Los saltos B en `validate.sh` usan layout con etiquetas para que el ensamblador resuelva el destino dentro de la sección.

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
