# Documentación técnica

**Curso:** CE-4301 Arquitectura de Computadores I  
**Proyecto individual** — Codificador Educativo de Instrucciones RISC-V  
**Estudiante:** Fabián Gutiérrez Jiménez — 2023141317  
**II Semestre 2026**

> **Estado actual:** implementado el formato **R** (`add`, `sub`, `and`, `or`).  
> Los formatos I, S y B quedan para siguientes iteraciones; los ejemplos de salida I/S/B se añadirán cuando estén implementados.

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

### Pendientes (subconjunto del enunciado)

| Mnemónico | Formato previsto |
|-----------|------------------|
| `addi`, `andi`, `lw`, `lb` | I |
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
        ▼
  ¿está en R_TYPE? ──no──► error (pendiente I/S/B o no soportada)
        │ sí
        ▼
  parse_r_operands (rd, rs1, rs2 como x0–x31)
        │
        ▼
  pack_r  →  entero 32 bits
        │
        ├─► explain_instruction  (desglose visual de campos)
        └─► print "HEX: 0x........"
```

Decisiones de diseño:

- Tabla `R_TYPE` centraliza opcode/funct3/funct7 para extender después a I/S/B.
- Parseo de registros únicamente como `x0`–`x31`.
- `main` captura errores de parseo/implementación; si la codificación tiene éxito, siempre imprime la línea `HEX:` en el formato exigido.

---

## 3. Ejemplo de salida explicativa (formato R)

Cuando existan I, S y B se documentará un ejemplo por formato (requisito §3.5). Por ahora:

```text
$ ./run.sh "add x5, x6, x7"
Instrucción: add x5, x6, x7
Formato:     R
Codificación: 0x007302b3
Binario 32:   00000000011100110000001010110011
Campos:       0000000|00111|00110|000|00101|0110011
              funct7 | rs2 | rs1 | f3 |  rd | opcode

Desglose de campos:
  funct7   bits [31:25]  bin=0000000  dec=0    | distingue operaciones (p. ej. add vs sub)
  rs2      bits [24:20]  bin=00111  dec=7    | segundo registro fuente (x7)
  rs1      bits [19:15]  bin=00110  dec=6    | primer registro fuente (x6)
  funct3   bits [14:12]  bin=000  dec=0    | selecciona la operación dentro del opcode OP (add)
  rd       bits [11: 7]  bin=00101  dec=5    | registro destino (x5)
  opcode   bits [ 6: 0]  bin=0110011  dec=51   | OP = 0110011: ALU registro-registro

Semántica: x5 ← x6 + x7
HEX: 0x007302b3
```

---

## 4. Evidencia de comparación contra la herramienta oficial

Ver [`VALIDACION.md`](VALIDACION.md): 12 casos tipo R (3 por instrucción) confrontados con `vectores_ejemplo.txt` y con `riscv64-unknown-elf-objdump -d` (`-march=rv32i -mabi=ilp32`). Resultado: **12/12 coinciden**.

---

## 5. Instalación del toolchain utilizado

Se usó [riscv-gnu-toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain), clonado y compilado en WSL, con prefijo `/opt/riscv`.

Uso para validación RV32I:

```bash
export PATH=/opt/riscv/bin:$PATH
riscv64-unknown-elf-as -march=rv32i -mabi=ilp32 -o caso.o caso.s
riscv64-unknown-elf-objdump -d caso.o
```

---

## 6. Instalación / preparación de esta herramienta

Ver [`README.md`](README.md): solo Python 3 y `chmod +x run.sh`. Sin dependencias `pip`.

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
