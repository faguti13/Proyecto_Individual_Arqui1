#!/usr/bin/env bash
# Valida el codificador contra el toolchain RISC-V oficial (§3.3 / §3.4).
# Uso:
#   ./validate.sh                  # usa casos_prueba.txt
#   ./validate.sh vectores_ejemplo.txt
#   ./validate.sh casos_prueba.txt --markdown   # además escribe validacion_resultado.md
#
# Requiere: Python 3, ./run.sh, y el toolchain en PATH o en /opt/riscv/bin
#   export PATH=/opt/riscv/bin:$PATH
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CASES_FILE="${1:-casos_prueba.txt}"
WRITE_MD=0
if [[ "${2:-}" == "--markdown" ]] || [[ "${1:-}" == "--markdown" ]]; then
    WRITE_MD=1
    if [[ "${1:-}" == "--markdown" ]]; then
        CASES_FILE="casos_prueba.txt"
    fi
fi

if [[ ! -f "$CASES_FILE" ]]; then
    echo "No se encontró el archivo de casos: $CASES_FILE" >&2
    exit 1
fi

AS="${RISCV_AS:-}"
OD="${RISCV_OBJDUMP:-}"
if [[ -z "$AS" ]]; then
    if command -v riscv64-unknown-elf-as >/dev/null 2>&1; then
        AS="$(command -v riscv64-unknown-elf-as)"
    elif [[ -x /opt/riscv/bin/riscv64-unknown-elf-as ]]; then
        AS=/opt/riscv/bin/riscv64-unknown-elf-as
    else
        echo "No se encontró riscv64-unknown-elf-as. Instale el toolchain o exporte PATH=/opt/riscv/bin:\$PATH" >&2
        exit 1
    fi
fi
if [[ -z "$OD" ]]; then
    if command -v riscv64-unknown-elf-objdump >/dev/null 2>&1; then
        OD="$(command -v riscv64-unknown-elf-objdump)"
    elif [[ -x /opt/riscv/bin/riscv64-unknown-elf-objdump ]]; then
        OD=/opt/riscv/bin/riscv64-unknown-elf-objdump
    else
        echo "No se encontró riscv64-unknown-elf-objdump." >&2
        exit 1
    fi
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

ok=0
fail=0
skip=0
total=0
md_rows=()

echo "Toolchain AS:      $AS"
echo "Toolchain OBJDUMP: $OD"
echo "Archivo de casos:  $CASES_FILE"
echo "---------------------------------------------------------------"
printf "%-4s %-28s %-12s %-12s %s\n" "#" "INSTRUCCIÓN" "MODELO" "OBJDUMP" "RESULTADO"
echo "---------------------------------------------------------------"

while IFS= read -r line || [[ -n "$line" ]]; do
    # Comentarios / vacías
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// }" ]] && continue

    # instruccion ; escenario   Ó   instruccion ; 0xHEX
    instr="${line%%;*}"
    instr="$(echo "$instr" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [[ -z "$instr" ]] && continue

    total=$((total + 1))

    # Modelo
    model_out=""
    model_hex=""
    if model_out="$(./run.sh "$instr" 2>"$TMP/err.$total")"; then
        model_hex="$(echo "$model_out" | grep -E '^HEX: 0x[0-9a-fA-F]{8}$' | tail -n1 | awk '{print tolower($2)}')"
    else
        err="$(tr '\n' ' ' < "$TMP/err.$total" | sed 's/[[:space:]]*$//')"
        printf "%-4s %-28s %-12s %-12s %s\n" "$total" "$instr" "(error)" "-" "FAIL ($err)"
        fail=$((fail + 1))
        md_rows+=("| $instr | (error) | - | no |")
        continue
    fi

    if [[ -z "$model_hex" ]]; then
        printf "%-4s %-28s %-12s %-12s %s\n" "$total" "$instr" "(sin HEX)" "-" "FAIL"
        fail=$((fail + 1))
        md_rows+=("| $instr | (sin HEX) | - | no |")
        continue
    fi

    # Toolchain
    printf '.text\n\t%s\n' "$instr" > "$TMP/caso.s"
    if ! "$AS" -march=rv32i -mabi=ilp32 -o "$TMP/caso.o" "$TMP/caso.s" 2>"$TMP/as.err"; then
        printf "%-4s %-28s %-12s %-12s %s\n" "$total" "$instr" "$model_hex" "(as fail)" "FAIL"
        fail=$((fail + 1))
        md_rows+=("| $instr | $model_hex | (as fail) | no |")
        continue
    fi
    dump_raw="$("$OD" -d "$TMP/caso.o" | awk '/^[ ]*[0-9a-f]+:/{print $2; exit}')"
    dump_hex="0x$(echo "$dump_raw" | tr 'A-F' 'a-f')"

    if [[ "$model_hex" == "$dump_hex" ]]; then
        printf "%-4s %-28s %-12s %-12s %s\n" "$total" "$instr" "$model_hex" "$dump_hex" "OK"
        ok=$((ok + 1))
        md_rows+=("| $instr | $model_hex | $dump_hex | sí |")
    else
        printf "%-4s %-28s %-12s %-12s %s\n" "$total" "$instr" "$model_hex" "$dump_hex" "FAIL"
        fail=$((fail + 1))
        md_rows+=("| $instr | $model_hex | $dump_hex | no |")
    fi
done < "$CASES_FILE"

echo "---------------------------------------------------------------"
echo "Total: $total | OK: $ok | FAIL: $fail"

if [[ "$WRITE_MD" -eq 1 ]]; then
    OUT="validacion_resultado.md"
    {
        echo "# Resultado de validación automática"
        echo
        echo "Generado por \`./validate.sh $CASES_FILE --markdown\`."
        echo
        echo "| Instrucción | HEX modelo | HEX objdump | ¿Coincide? |"
        echo "|-------------|------------|-------------|------------|"
        for row in "${md_rows[@]}"; do
            echo "$row"
        done
        echo
        echo "**Resumen:** $ok/$total coinciden."
    } > "$OUT"
    echo "Tabla Markdown escrita en: $OUT"
fi

[[ "$fail" -eq 0 ]]
