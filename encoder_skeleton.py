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

# Opcode OP (register-register) — RISC-V ISA Vol. I, formato R
OPCODE_OP = 0b0110011

# mnemonic -> (funct3, funct7)
R_TYPE = {
    "add": (0b000, 0b0000000),
    "sub": (0b000, 0b0100000),
    "and": (0b111, 0b0000000),
    "or":  (0b110, 0b0000000),
}

PENDIENTES = {"addi", "andi", "lw", "lb", "sw", "sb", "beq", "bne"}


def parse_register(token: str) -> int:
    """Convierte 'xN' (0–31) en el índice de registro."""
    token = token.strip().lower()
    match = re.fullmatch(r"x([0-9]|[12][0-9]|3[01])", token)
    if not match:
        raise ValueError(f"Registro inválido: '{token}' (se espera x0–x31)")
    return int(match.group(1))


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

    if mnemonic in PENDIENTES:
        raise NotImplementedError(
            f"'{mnemonic}' pertenece al subconjunto soportado pero aún no "
            f"está implementada (fase actual: solo formato R)."
        )

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
        f"bin={_bits(value, width)}  dec={value:<3d}  | {role}"
    )


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

    if mnemonic not in R_TYPE:
        raise NotImplementedError(
            f"explain_instruction: formato de '{mnemonic}' aún no implementado"
        )

    opcode = word & 0x7F
    rd = (word >> 7) & 0x1F
    funct3 = (word >> 12) & 0x7
    rs1 = (word >> 15) & 0x1F
    rs2 = (word >> 20) & 0x1F
    funct7 = (word >> 25) & 0x7F

    binary = format(word, "032b")
    # Visual: funct7 | rs2 | rs1 | funct3 | rd | opcode
    visual = (
        f"{binary[0:7]}|{binary[7:12]}|{binary[12:17]}|"
        f"{binary[17:20]}|{binary[20:25]}|{binary[25:32]}"
    )

    lines = [
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
        f"Semántica: x{rd} = x{rs1} {mnemonic} x{rs2}"
        if mnemonic in ("add", "sub", "and", "or")
        else "",
    ]
    # Clarificar semántica por mnemónico
    ops = {
        "add": f"x{rd} ← x{rs1} + x{rs2}",
        "sub": f"x{rd} ← x{rs1} - x{rs2}",
        "and": f"x{rd} ← x{rs1} AND x{rs2}",
        "or":  f"x{rd} ← x{rs1} OR  x{rs2}",
    }
    lines[-1] = f"Semántica: {ops[mnemonic]}"
    return "\n".join(lines)


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
