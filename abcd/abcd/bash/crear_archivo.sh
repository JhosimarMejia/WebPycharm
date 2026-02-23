#!/bin/bash
set -u

BASE="$1"
GENERO="$2"
AUTOR="$3"
ISBN="$4"

# Códigos de salida (tipo examen)
E_USO=1
E_VACIO=10
E_INVALIDO=11
E_NOBASE=12
E_EXISTE=20

# 1) Comprobar argumentos
if [[ -z "${BASE:-}" || -z "${GENERO:-}" || -z "${AUTOR:-}" || -z "${ISBN:-}" ]]; then
  echo "USO|$0 <base> <genero> <autor> <isbn>" >&2
  exit $E_USO
fi

# 2) Validación simple de género/autor (solo letras, números y _)
# (como tú ya normalizas en Python, deberían venir limpios)
regex_nombre='^[a-z0-9_]+$'
if [[ ! "$GENERO" =~ $regex_nombre || ! "$AUTOR" =~ $regex_nombre ]]; then
  echo "INVALIDO|Genero/Autor solo pueden contener a-z 0-9 _" >&2
  exit $E_INVALIDO
fi

# 3) Validación ISBN: 978 + 6 dígitos (ajusta si cambias formato)
regex_isbn='^978[0-9]{6}$'
if [[ ! "$ISBN" =~ $regex_isbn ]]; then
  echo "INVALIDO|ISBN debe tener formato 978XXXXXX (6 digitos)" >&2
  exit $E_INVALIDO
fi

# 4) Base debe existir
if [[ ! -d "$BASE" ]]; then
  echo "NOBASE|No existe el directorio base: $BASE" >&2
  exit $E_NOBASE
fi

# 5) Crear ruta y archivo
RUTA="$BASE/$GENERO/$AUTOR"
ARCHIVO="$RUTA/$ISBN.json"

mkdir -p "$RUTA"

if [[ -e "$ARCHIVO" ]]; then
  echo "EXISTE|$ARCHIVO"
  exit $E_EXISTE
fi

touch "$ARCHIVO"
echo "CREADO|$ARCHIVO"
exit 0
