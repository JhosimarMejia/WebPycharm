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

echo "Genero: $ruta"
echo "⚠️ Esto borrara TODOS los autores y libros dentro."

# Confirmación doble (tipo examen)
read -n1 -p "¿Seguro? [S/N]: " conf1
echo
if [[ "$conf1" != "S" && "$conf1" != "s" ]]; then
  echo "Cancelado"
  exit $E_CANCELADO
fi

read -n1 -p "¿Confirmar de nuevo? [S/N]: " conf2
echo
if [[ "$conf2" == "S" || "$conf2" == "s" ]]; then
  rm -r "$ruta"
  echo "✅ Genero eliminado"
  exit $E_BORRADO
else
  echo "Cancelado"
  exit $E_CANCELADO
fi
