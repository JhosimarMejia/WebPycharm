#!/bin/bash
set -u

ruta="${1:-}"

E_INVALIDA=20
E_BORRADO=30
E_CANCELADO=40

if [[ -z "$ruta" || ! -d "$ruta" ]]; then
  echo "❌ Ruta invalida"
  exit $E_INVALIDA
fi

echo "Autor: $ruta"

# Comprobar si tiene archivos
if [[ "$(ls -A "$ruta")" ]]; then
  echo "⚠️ Este autor contiene libros."
fi

read -n1 -p "¿Eliminar completamente? [S/N]: " conf
echo

if [[ "$conf" == "S" || "$conf" == "s" ]]; then
  rm -r "$ruta"
  echo "✅ Autor eliminado"
  exit $E_BORRADO
else
  echo "Cancelado"
  exit $E_CANCELADO
fi
