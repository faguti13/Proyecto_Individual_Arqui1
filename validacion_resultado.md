# Resultado de validación automática

Generado por `./validate.sh casos_prueba.txt --markdown`.

| Instrucción | HEX modelo | HEX objdump | ¿Coincide? |
|-------------|------------|-------------|------------|
| add x5, x6, x7 | 0x007302b3 | 0x007302b3 | sí |
| add x14, x26, x31 | 0x01fd0733 | 0x01fd0733 | sí |
| add x28, x15, x0 | 0x00078e33 | 0x00078e33 | sí |
| sub x5, x7, x18 | 0x412382b3 | 0x412382b3 | sí |
| sub x31, x20, x13 | 0x40da0fb3 | 0x40da0fb3 | sí |
| sub x6, x28, x0 | 0x400e0333 | 0x400e0333 | sí |
| and x10, x11, x12 | 0x00c5f533 | 0x00c5f533 | sí |
| and x25, x16, x22 | 0x01687cb3 | 0x01687cb3 | sí |
| and x0, x5, x18 | 0x0122f033 | 0x0122f033 | sí |
| or x18, x29, x9 | 0x009ee933 | 0x009ee933 | sí |
| or x19, x1, x23 | 0x0170e9b3 | 0x0170e9b3 | sí |
| or x23, x0, x27 | 0x01b06bb3 | 0x01b06bb3 | sí |
| addi x5, x25, 100 | 0x064c8293 | 0x064c8293 | sí |
| addi x7, x27, -12 | 0xff4d8393 | 0xff4d8393 | sí |
| addi x10, x1, 2047 | 0x7ff08513 | 0x7ff08513 | sí |
| andi x8, x3, 255 | 0x0ff1f413 | 0x0ff1f413 | sí |
| andi x30, x1, -209 | 0xf2f0ff13 | 0xf2f0ff13 | sí |
| andi x27, x30, -2048 | 0x800f7d93 | 0x800f7d93 | sí |
| lw x29, 8(x30) | 0x008f2e83 | 0x008f2e83 | sí |
| lw x30, -1049(x14) | 0xbe772f03 | 0xbe772f03 | sí |
| lw x5, 0(x0) | 0x00002283 | 0x00002283 | sí |
| lb x2, 1705(x9) | 0x6a948103 | 0x6a948103 | sí |
| lb x25, -389(x27) | 0xe7bd8c83 | 0xe7bd8c83 | sí |
| lb x18, -2048(x17) | 0x80088903 | 0x80088903 | sí |
| sw x16, 100(x31) | 0x070fa223 | 0x070fa223 | sí |
| sw x31, -411(x23) | 0xe7fba2a3 | 0xe7fba2a3 | sí |
| sw x8, 0(x2) | 0x00812023 | 0x00812023 | sí |
| sb x6, 72(x28) | 0x046e0423 | 0x046e0423 | sí |
| sb x18, -100(x20) | 0xf92a0e23 | 0xf92a0e23 | sí |
| sb x28, 2047(x11) | 0x7fc58fa3 | 0x7fc58fa3 | sí |
| beq x31, x23, 16 | 0x017f8863 | 0x017f8863 | sí |
| beq x30, x4, -80 | 0xfa4f08e3 | 0xfa4f08e3 | sí |
| beq x1, x2, 0 | 0x00208063 | 0x00208063 | sí |
| bne x12, x15, 16 | 0x00f61863 | 0x00f61863 | sí |
| bne x17, x22, -16 | 0xff6898e3 | 0xff6898e3 | sí |
| bne x5, x0, 60 | 0x02029e63 | 0x02029e63 | sí |

**Resumen:** 36/36 coinciden.
