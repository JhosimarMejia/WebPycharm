#!/bin/bash
set -u

TIENDA="/tiendas/tienda_libros"

# Comprobar jq (para mostrar campos)
if ! command -v jq >/dev/null 2>&1; then
  echo "❌ Falta jq. Instala con: sudo apt install jq"
  exit 1
fi

clear
read -p "Indica el codigo (sin .json): " codigo

# Validación básica
if [[ -z "${codigo}" ]]; then
  read -n1 -p "❌ Codigo vacio. Pulsa una tecla..."
  exit 10
fi

# Buscar archivo por nombre exacto: 978000012.json
ruta=$(find "$TIENDA" -type f -name "${codigo}.json" 2>/dev/null | head -n 1)

if [[ -z "${ruta}" ]]; then
  read -n1 -p "❌ No se encuentra el codigo ${codigo}. Pulsa una tecla..."
  exit 20
fi

clear
echo "✅ Encontrado: $ruta"
echo

# Mostrar contenido “bonito” (adaptado a tus claves actuales)
titulo=$(jq -r '.titulo // "N/A"' "$ruta")
autor=$(jq -r '.autor // "N/A"' "$ruta")
genero=$(jq -r '.genero // "N/A"' "$ruta")

echo "📘 Titulo:  $titulo"
echo "✍  Autor:   $autor"
echo "🏷  Genero:  $genero"
echo

echo "¿Que deseas hacer?"
echo "  v) Ver JSON completo"
echo "  b) Borrar"
echo "  q) Volver"
read -n1 -p "Opcion: " op
echo

case "$op" in
  v|V)
    clear
    cat "$ruta"
    echo
    read -n1 -p "Pulsa una tecla para volver..."
    ;;
  b|B)
    echo
    read -n1 -p "¿Realmente deseas eliminarlo? [S/N]: " conf
    echo
    if [[ "$conf" == "S" || "$conf" == "s" ]]; then
      rm -f "$ruta"
      read -n1 -p "✅ Eliminado. Pulsa una tecla..."
    else
      read -n1 -p "Cancelado. Pulsa una tecla..."
    fi
    ;;
  *)
    # volver
    ;;
esac

exit 0
