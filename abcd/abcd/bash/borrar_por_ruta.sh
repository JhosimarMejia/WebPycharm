#!/bin/bash
set -u

ruta="${1:-}"

E_INVALIDA=20
E_BORRADO=30
E_CANCELADO=40

if [[ -z "$ruta" || ! -f "$ruta" ]]; then
  echo "❌ Ruta invalida"
  exit $E_INVALIDA
fi

echo "Archivo: $ruta"
read -n1 -p "¿Eliminar definitivamente? [S/N]: " conf
echo

if [[ "$conf" == "S" || "$conf" == "s" ]]; then
  rm -f "$ruta"
  echo "✅ Eliminado"
  exit $E_BORRADO
else
  echo "Cancelado"
  exit $E_CANCELADO
fi
