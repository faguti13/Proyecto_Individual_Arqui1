# Codificador Educativo de Instrucciones RISC-V

**Curso:** CE-4301 Arquitectura de Computadores I  
**Estudiante:** Fabián Gutiérrez Jiménez — 2023141317  
**II Semestre 2026**

## Preparación del entorno

**Entorno recomendado:** Linux (nativo o **WSL** en Windows). El punto de entrada `run.sh` es un script Bash; la verificación del curso suele ejecutarse en ese tipo de entorno.

Para que `./run.sh "<instruccion>"` funcione en la verificación automática:

1. Tener instalado **Python 3** (solo biblioteca estándar; no se requiere `pip` ni `requirements.txt`).
2. Desde la raíz del repositorio, asegurar permisos de ejecución del punto de entrada:

```bash
chmod +x run.sh
```

No se necesita ninguna otra dependencia ni comando de invocación alternativo. El contrato de entrada/salida es únicamente:

```bash
./run.sh "<instruccion>"
```

La herramienta emite la línea `HEX: 0xXXXXXXXX` requerida por el script de verificación automática (§3.4).

Documentación técnica: [`DOCUMENTACION.md`](./docs/DOCUMENTACION.md).  
Evidencia de validación contra el toolchain: [`VALIDACION.md`](./docs/VALIDACION.md).
