#!/usr/bin/env python3
"""
Esqueleto del Codificador Educativo de Instrucciones RISC-V.
CE4301 Arquitectura de Computadores I — Proyecto Individual — 2026-II

Este esqueleto ya implementa el contrato de línea de comandos y de salida
requerido por la especificación. Usted debe completar las dos funciones
marcadas con TODO; puede modificar el resto del archivo si lo necesita,
siempre que se preserve el contrato de invocación y la línea "HEX: 0x...".

No es obligatorio usar este esqueleto ni Python: puede implementar su
propia herramienta desde cero, en el lenguaje que prefiera, siempre que
respete el mismo contrato (ver especificación, sección "Modo de operación").
"""
import re
import sys

SOPORTADAS = ["add", "sub", "and", "or", "addi", "andi",
              "lw", "lb", "sw", "sb", "beq", "bne"]

# Opcodes — RISC-V ISA Vol. I
OPCODE_OP = 0b0110011      # R: ALU registro-registro
OPCODE_OP_IMM = 0b0010011  # I: ALU con inmediato
OPCODE_LOAD = 0b0000011    # I: carga desde memoria
OPCODE_STORE = 0b0100011   # S: almacenamiento en memoria
OPCODE_BRANCH = 0b1100011  # B: salto condicional

# mnemonic -> (funct3, funct7)
R_TYPE = {
    "add": (0b000, 0b0000000),
    "sub": (0b000, 0b0100000),
    "and": (0b111, 0b0000000),
    "or":  (0b110, 0b0000000),
}

# mnemonic -> funct3  (opcode OP-IMM)
I_TYPE_ARITH = {
    "addi": 0b000,
    "andi": 0b111,
}

# mnemonic -> funct3  (opcode LOAD)
I_TYPE_LOAD = {
    "lw": 0b010,
    "lb": 0b000,
}

# mnemonic -> funct3  (opcode STORE)
S_TYPE = {
    "sw": 0b010,
    "sb": 0b000,
}

# mnemonic -> funct3  (opcode BRANCH)
B_TYPE = {
    "beq": 0b000,
    "bne": 0b001,
}


def parse_register(token: str) -> int:
    """Convierte 'xN' (0–31) en el índice de registro."""
    token = token.strip().lower()
    match = re.fullmatch(r"x([0-9]|[12][0-9]|3[01])", token)
    if not match:
        raise ValueError(f"Registro inválido: '{token}' (se espera x0–x31)")
    return int(match.group(1))


def parse_imm12(token: str) -> int:
    """Parsea un inmediato con signo de 12 bits (-2048 … 2047)."""
    token = token.strip()
    try:
        # int() acepta decimal y 0x…; los vectores usan decimal (pos/neg)
        value = int(token, 0)
    except ValueError as exc:
        raise ValueError(
            f"Inmediato inválido: '{token}' (se espera entero con signo)"
        ) from exc
    if value < -2048 or value > 2047:
        raise ValueError(
            f"Inmediato fuera de rango de 12 bits: {value} (válido: -2048…2047)"
        )
    return value


def parse_branch_offset(token: str) -> int:
    """Parsea offset de salto en bytes (par, rango B-type: -4096…4094)."""
    token = token.strip()
    try:
        value = int(token, 0)
    except ValueError as exc:
        raise ValueError(
            f"Offset de salto inválido: '{token}' (se espera entero con signo en bytes)"
        ) from exc
    if value % 2 != 0:
        raise ValueError(
            f"Offset de salto debe ser par (bytes): {value}"
        )
    if value < -4096 or value > 4094:
        raise ValueError(
            f"Offset fuera de rango B-type: {value} (válido: -4096…4094, par)"
        )
    return value


def parse_r_operands(rest: str) -> tuple[int, int, int]:
    """Parsea 'rd, rs1, rs2' para formato R."""
    parts = [p.strip() for p in rest.split(",")]
    if len(parts) != 3:
        raise ValueError(
            f"Formato R espera 3 operandos (rd, rs1, rs2); se recibieron {len(parts)}"
        )
    rd = parse_register(parts[0])
    rs1 = parse_register(parts[1])
    rs2 = parse_register(parts[2])
    return rd, rs1, rs2


def parse_i_arith_operands(rest: str) -> tuple[int, int, int]:
    """Parsea 'rd, rs1, imm' para addi/andi."""
    parts = [p.strip() for p in rest.split(",")]
    if len(parts) != 3:
        raise ValueError(
            f"Formato I aritmético espera 3 operandos (rd, rs1, imm); "
            f"se recibieron {len(parts)}"
        )
    rd = parse_register(parts[0])
    rs1 = parse_register(parts[1])
    imm = parse_imm12(parts[2])
    return rd, rs1, imm


def parse_i_load_operands(rest: str) -> tuple[int, int, int]:
    """Parsea 'rd, imm(rs1)' para lw/lb (p. ej. 'x5, 8(x6)' o 'x5, -4(x2)')."""
    parts = [p.strip() for p in rest.split(",")]
    if len(parts) != 2:
        raise ValueError(
            f"Formato I load espera 2 operandos (rd, imm(rs1)); "
            f"se recibieron {len(parts)}"
        )
    rd = parse_register(parts[0])
    match = re.fullmatch(
        r"(-?(?:0x[0-9a-fA-F]+|\d+))\(\s*(x(?:[0-9]|[12][0-9]|3[01]))\s*\)",
        parts[1],
    )
    if not match:
        raise ValueError(
            f"Operando de load inválido: '{parts[1]}' "
            f"(se espera imm(rs1), p. ej. 8(x6) o -4(x2))"
        )
    imm = parse_imm12(match.group(1))
    rs1 = parse_register(match.group(2))
    return rd, rs1, imm


def parse_s_store_operands(rest: str) -> tuple[int, int, int]:
    """Parsea 'rs2, imm(rs1)' para sw/sb (p. ej. 'x8, -4(x2)')."""
    parts = [p.strip() for p in rest.split(",")]
    if len(parts) != 2:
        raise ValueError(
            f"Formato S store espera 2 operandos (rs2, imm(rs1)); "
            f"se recibieron {len(parts)}"
        )
    rs2 = parse_register(parts[0])
    match = re.fullmatch(
        r"(-?(?:0x[0-9a-fA-F]+|\d+))\(\s*(x(?:[0-9]|[12][0-9]|3[01]))\s*\)",
        parts[1],
    )
    if not match:
        raise ValueError(
            f"Operando de store inválido: '{parts[1]}' "
            f"(se espera imm(rs1), p. ej. -4(x2) o 72(x28))"
        )
    imm = parse_imm12(match.group(1))
    rs1 = parse_register(match.group(2))
    return rs2, rs1, imm


def parse_b_branch_operands(rest: str) -> tuple[int, int, int]:
    """Parsea 'rs1, rs2, offset' para beq/bne (offset en bytes)."""
    parts = [p.strip() for p in rest.split(",")]
    if len(parts) != 3:
        raise ValueError(
            f"Formato B espera 3 operandos (rs1, rs2, offset); "
            f"se recibieron {len(parts)}"
        )
    rs1 = parse_register(parts[0])
    rs2 = parse_register(parts[1])
    offset = parse_branch_offset(parts[2])
    return rs1, rs2, offset


def split_mnemonic(instruction: str) -> tuple[str, str]:
    """Separa mnemónico y el resto de la cadena de instrucción."""
    text = instruction.strip()
    if not text:
        raise ValueError("Instrucción vacía")
    parts = text.split(None, 1)
    mnemonic = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""
    return mnemonic, rest


def pack_r(funct7: int, rs2: int, rs1: int, funct3: int, rd: int, opcode: int) -> int:
    return (
        ((funct7 & 0x7F) << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | ((rd & 0x1F) << 7)
        | (opcode & 0x7F)
    )


def pack_i(imm: int, rs1: int, funct3: int, rd: int, opcode: int) -> int:
    """Formato I: imm[11:0] | rs1 | funct3 | rd | opcode."""
    return (
        ((imm & 0xFFF) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | ((rd & 0x1F) << 7)
        | (opcode & 0x7F)
    )


def pack_s(imm: int, rs2: int, rs1: int, funct3: int, opcode: int) -> int:
    """Formato S: imm[11:5] | rs2 | rs1 | funct3 | imm[4:0] | opcode."""
    imm12 = imm & 0xFFF
    imm_hi = (imm12 >> 5) & 0x7F
    imm_lo = imm12 & 0x1F
    return (
        (imm_hi << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | (imm_lo << 7)
        | (opcode & 0x7F)
    )


def pack_b(offset: int, rs2: int, rs1: int, funct3: int, opcode: int) -> int:
    """Formato B: imm[12|10:5] | rs2 | rs1 | funct3 | imm[4:1|11] | opcode."""
    imm = offset & 0x1FFF  # imm[12:0] con imm[0]=0 (offset par)
    imm_12 = (imm >> 12) & 0x1
    imm_11 = (imm >> 11) & 0x1
    imm_10_5 = (imm >> 5) & 0x3F
    imm_4_1 = (imm >> 1) & 0xF
    return (
        (imm_12 << 31)
        | (imm_10_5 << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | (imm_4_1 << 8)
        | (imm_11 << 7)
        | (opcode & 0x7F)
    )


def encode_instruction(instruction: str) -> int:
    """
    Recibe una instrucción como texto, p. ej. "add x5, x6, x7", y debe
    retornar su codificación de 32 bits como entero (0 <= valor < 2**32).

    Debe soportar únicamente las instrucciones en SOPORTADAS. Los valores
    de opcode/funct3/funct7 de cada una NO se proveen aquí: deben
    investigarse en el manual oficial de la ISA RISC-V (ver referencia en
    la especificación) y documentarse en el README.
    """
    mnemonic, rest = split_mnemonic(instruction)

    if mnemonic in R_TYPE:
        funct3, funct7 = R_TYPE[mnemonic]
        rd, rs1, rs2 = parse_r_operands(rest)
        return pack_r(funct7, rs2, rs1, funct3, rd, OPCODE_OP)

    if mnemonic in I_TYPE_ARITH:
        funct3 = I_TYPE_ARITH[mnemonic]
        rd, rs1, imm = parse_i_arith_operands(rest)
        return pack_i(imm, rs1, funct3, rd, OPCODE_OP_IMM)

    if mnemonic in I_TYPE_LOAD:
        funct3 = I_TYPE_LOAD[mnemonic]
        rd, rs1, imm = parse_i_load_operands(rest)
        return pack_i(imm, rs1, funct3, rd, OPCODE_LOAD)

    if mnemonic in S_TYPE:
        funct3 = S_TYPE[mnemonic]
        rs2, rs1, imm = parse_s_store_operands(rest)
        return pack_s(imm, rs2, rs1, funct3, OPCODE_STORE)

    if mnemonic in B_TYPE:
        funct3 = B_TYPE[mnemonic]
        rs1, rs2, offset = parse_b_branch_operands(rest)
        return pack_b(offset, rs2, rs1, funct3, OPCODE_BRANCH)

    raise ValueError(
        f"Instrucción no soportada: '{mnemonic}'. "
        f"Soportadas: {', '.join(SOPORTADAS)}"
    )


def _bits(value: int, width: int) -> str:
    return format(value & ((1 << width) - 1), f"0{width}b")


def _field_row(name: str, hi: int, lo: int, value: int, role: str) -> str:
    width = hi - lo + 1
    return (
        f"  {name:8s} bits [{hi:2d}:{lo:2d}]  "
        f"bin={_bits(value, width)}  dec={value:<5d}  | {role}"
    )


def _imm12_signed(raw12: int) -> int:
    """Interpreta imm[11:0] como entero con signo."""
    raw12 &= 0xFFF
    return raw12 - 0x1000 if raw12 & 0x800 else raw12


def _branch_offset_from_word(word: int) -> int:
    """Reconstruye el offset en bytes (imm[12:1] << 1) desde una palabra B."""
    imm_12 = (word >> 31) & 0x1
    imm_11 = (word >> 7) & 0x1
    imm_10_5 = (word >> 25) & 0x3F
    imm_4_1 = (word >> 8) & 0xF
    imm = (imm_12 << 12) | (imm_11 << 11) | (imm_10_5 << 5) | (imm_4_1 << 1)
    if imm & 0x1000:
        imm -= 0x2000
    return imm


def _explain_r(instruction: str, mnemonic: str, word: int) -> str:
    opcode = word & 0x7F
    rd = (word >> 7) & 0x1F
    funct3 = (word >> 12) & 0x7
    rs1 = (word >> 15) & 0x1F
    rs2 = (word >> 20) & 0x1F
    funct7 = (word >> 25) & 0x7F

    binary = format(word, "032b")
    visual = (
        f"{binary[0:7]}|{binary[7:12]}|{binary[12:17]}|"
        f"{binary[17:20]}|{binary[20:25]}|{binary[25:32]}"
    )
    ops = {
        "add": f"x{rd} ← x{rs1} + x{rs2}",
        "sub": f"x{rd} ← x{rs1} - x{rs2}",
        "and": f"x{rd} ← x{rs1} AND x{rs2}",
        "or":  f"x{rd} ← x{rs1} OR  x{rs2}",
    }
    return "\n".join([
        f"Instrucción: {instruction.strip()}",
        f"Formato:     R",
        f"Codificación: 0x{word:08x}",
        f"Binario 32:   {binary}",
        f"Campos:       {visual}",
        f"              funct7 | rs2 | rs1 | f3 |  rd | opcode",
        "",
        "Desglose de campos:",
        _field_row("funct7", 31, 25, funct7,
                   "distingue operaciones (p. ej. add vs sub)"),
        _field_row("rs2", 24, 20, rs2,
                   f"segundo registro fuente (x{rs2})"),
        _field_row("rs1", 19, 15, rs1,
                   f"primer registro fuente (x{rs1})"),
        _field_row("funct3", 14, 12, funct3,
                   f"selecciona la operación dentro del opcode OP ({mnemonic})"),
        _field_row("rd", 11, 7, rd,
                   f"registro destino (x{rd})"),
        _field_row("opcode", 6, 0, opcode,
                   "OP = 0110011: ALU registro-registro"),
        "",
        f"Semántica: {ops[mnemonic]}",
    ])


def _explain_s(instruction: str, mnemonic: str, word: int) -> str:
    opcode = word & 0x7F
    imm_lo = (word >> 7) & 0x1F
    funct3 = (word >> 12) & 0x7
    rs1 = (word >> 15) & 0x1F
    rs2 = (word >> 20) & 0x1F
    imm_hi = (word >> 25) & 0x7F
    imm_raw = (imm_hi << 5) | imm_lo
    imm = _imm12_signed(imm_raw)

    binary = format(word, "032b")
    visual = (
        f"{binary[0:7]}|{binary[7:12]}|{binary[12:17]}|"
        f"{binary[17:20]}|{binary[20:25]}|{binary[25:32]}"
    )
    width = "palabra (32 bits)" if mnemonic == "sw" else "byte (8 bits)"
    semantics = f"mem[x{rs1} + {imm}] ← x{rs2}  ({width})"

    return "\n".join([
        f"Instrucción: {instruction.strip()}",
        f"Formato:     S",
        f"Codificación: 0x{word:08x}",
        f"Binario 32:   {binary}",
        f"Campos:       {visual}",
        f"              imm[11:5] | rs2 | rs1 | f3 | imm[4:0] | opcode",
        "",
        "Desglose de campos:",
        _field_row("imm[11:5]", 31, 25, imm_hi,
                   f"parte alta del offset (inmediato completo = {imm})"),
        _field_row("rs2", 24, 20, rs2,
                   f"registro fuente a almacenar (x{rs2})"),
        _field_row("rs1", 19, 15, rs1,
                   f"registro base de dirección (x{rs1})"),
        _field_row("funct3", 14, 12, funct3,
                   f"selecciona la operación ({mnemonic})"),
        _field_row("imm[4:0]", 11, 7, imm_lo,
                   f"parte baja del offset (inmediato completo = {imm})"),
        _field_row("opcode", 6, 0, opcode,
                   "STORE = 0100011: almacenamiento en memoria"),
        "",
        f"Semántica: {semantics}",
    ])


def _explain_b(instruction: str, mnemonic: str, word: int) -> str:
    opcode = word & 0x7F
    imm_11 = (word >> 7) & 0x1
    imm_4_1 = (word >> 8) & 0xF
    funct3 = (word >> 12) & 0x7
    rs1 = (word >> 15) & 0x1F
    rs2 = (word >> 20) & 0x1F
    imm_10_5 = (word >> 25) & 0x3F
    imm_12 = (word >> 31) & 0x1
    offset = _branch_offset_from_word(word)

    binary = format(word, "032b")
    visual = (
        f"{binary[0:1]}|{binary[1:7]}|{binary[7:12]}|{binary[12:17]}|"
        f"{binary[17:20]}|{binary[20:24]}|{binary[24:25]}|{binary[25:32]}"
    )
    cond = "==" if mnemonic == "beq" else "!="
    semantics = (
        f"si x{rs1} {cond} x{rs2}, saltar PC + {offset} bytes "
        f"(destino relativo a la instrucción)"
    )

    return "\n".join([
        f"Instrucción: {instruction.strip()}",
        f"Formato:     B",
        f"Codificación: 0x{word:08x}",
        f"Binario 32:   {binary}",
        f"Campos:       {visual}",
        f"              imm12|imm10:5| rs2 | rs1 | f3 |imm4:1|i11| opcode",
        "",
        "Desglose de campos:",
        _field_row("imm[12]", 31, 31, imm_12,
                   f"bit alto del offset (offset bytes = {offset})"),
        _field_row("imm[10:5]", 30, 25, imm_10_5,
                   "parte media del offset de salto"),
        _field_row("rs2", 24, 20, rs2,
                   f"segundo registro comparado (x{rs2})"),
        _field_row("rs1", 19, 15, rs1,
                   f"primer registro comparado (x{rs1})"),
        _field_row("funct3", 14, 12, funct3,
                   f"{'igual' if mnemonic == 'beq' else 'distinto'} ({mnemonic})"),
        _field_row("imm[4:1]", 11, 8, imm_4_1,
                   "parte baja del offset de salto"),
        _field_row("imm[11]", 7, 7, imm_11,
                   "bit intermedio del offset"),
        _field_row("opcode", 6, 0, opcode,
                   "BRANCH = 1100011: salto condicional"),
        "",
        f"Semántica: {semantics}",
    ])


def _explain_i(instruction: str, mnemonic: str, word: int) -> str:
    opcode = word & 0x7F
    rd = (word >> 7) & 0x1F
    funct3 = (word >> 12) & 0x7
    rs1 = (word >> 15) & 0x1F
    imm_raw = (word >> 20) & 0xFFF
    imm = _imm12_signed(imm_raw)

    binary = format(word, "032b")
    visual = f"{binary[0:12]}|{binary[12:17]}|{binary[17:20]}|{binary[20:25]}|{binary[25:32]}"

    if mnemonic in I_TYPE_ARITH:
        opcode_role = "OP-IMM = 0010011: ALU con inmediato"
        if mnemonic == "addi":
            semantics = f"x{rd} ← x{rs1} + {imm}"
        else:
            semantics = f"x{rd} ← x{rs1} AND {imm}"
    else:
        opcode_role = "LOAD = 0000011: carga desde memoria"
        width = "palabra (32 bits)" if mnemonic == "lw" else "byte (8 bits, sign-extend)"
        semantics = f"x{rd} ← mem[x{rs1} + {imm}]  ({width})"

    return "\n".join([
        f"Instrucción: {instruction.strip()}",
        f"Formato:     I",
        f"Codificación: 0x{word:08x}",
        f"Binario 32:   {binary}",
        f"Campos:       {visual}",
        f"              imm[11:0] | rs1 | f3 |  rd | opcode",
        "",
        "Desglose de campos:",
        _field_row("imm", 31, 20, imm_raw,
                   f"inmediato de 12 bits con signo (valor = {imm})"),
        _field_row("rs1", 19, 15, rs1,
                   f"registro base / fuente (x{rs1})"),
        _field_row("funct3", 14, 12, funct3,
                   f"selecciona la operación ({mnemonic})"),
        _field_row("rd", 11, 7, rd,
                   f"registro destino (x{rd})"),
        _field_row("opcode", 6, 0, opcode, opcode_role),
        "",
        f"Semántica: {semantics}",
    ])


def explain_instruction(instruction: str, word: int) -> str:
    """
    Debe retornar un texto (para imprimirse en pantalla) que muestre, de
    forma visual, los 32 bits de 'word' divididos en los campos del
    formato correspondiente (R, I, S o B) — indicando el rango de bits y
    el valor de cada campo — junto con una breve explicación de cada uno.
    El formato visual (colores, tabla, arte ASCII, etc.) queda a su
    criterio, siempre que sea claro.
    """
    mnemonic, _ = split_mnemonic(instruction)
    word &= 0xFFFFFFFF

    if mnemonic in R_TYPE:
        return _explain_r(instruction, mnemonic, word)
    if mnemonic in I_TYPE_ARITH or mnemonic in I_TYPE_LOAD:
        return _explain_i(instruction, mnemonic, word)
    if mnemonic in S_TYPE:
        return _explain_s(instruction, mnemonic, word)
    if mnemonic in B_TYPE:
        return _explain_b(instruction, mnemonic, word)

    raise NotImplementedError(
        f"explain_instruction: formato de '{mnemonic}' aún no implementado"
    )


def main():
    if len(sys.argv) != 2:
        print(f'Uso: {sys.argv[0]} "<instruccion>"', file=sys.stderr)
        print(f'Ejemplo: {sys.argv[0]} "add x5, x6, x7"', file=sys.stderr)
        sys.exit(2)

    instruction = sys.argv[1]
    try:
        word = encode_instruction(instruction) & 0xFFFFFFFF
    except (ValueError, NotImplementedError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(explain_instruction(instruction, word))

    # No modificar el formato de la siguiente línea: la especificación la
    # requiere, literal, para permitir la validación automática.
    print(f"HEX: 0x{word:08x}")


if __name__ == "__main__":
    main()
