#!/bin/bash
set -u

BASE="/tiendas/tienda_libros"

E_NOEXISTE=20
E_CANCELADO=40
E_BORRADO=30

read -p "Indica el codigo (sin .json): " codigo

if [[ -z "${codigo}" ]]; then
  echo "❌ Codigo vacio"
  exit 10
fi

ruta=$(find "$BASE" -type f -name "${codigo}.json" 2>/dev/null | head -n 1)

if [[ -z "$ruta" ]]; then
  echo "❌ No existe el codigo ${codigo}"
  exit $E_NOEXISTE
fi

echo
echo "Encontrado: $ruta"
echo
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
