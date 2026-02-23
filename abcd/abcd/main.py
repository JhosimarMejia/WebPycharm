import curses
import subprocess
from pathlib import Path
import unicodedata
import json

BASE_TIENDA = Path("/tiendas/tienda_libros")
PROYECTO = Path(__file__).resolve().parent
CONTADOR = PROYECTO / "contador.txt"


def normalizar_nombre(s: str) -> str:
    # 1) quitar espacios extremos y poner en minúsculas
    s = s.strip().lower()

    # 2) quitar acentos: acción -> accion
    s = "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )

    # 3) espacios a guión bajo: literatura juvenil -> literatura_juvenil
    s = s.replace(" ", "_")

    return s



def generar_isbn() -> str:
    if not CONTADOR.exists():
        CONTADOR.write_text("0")

    n = int(CONTADOR.read_text().strip())
    n += 1
    CONTADOR.write_text(str(n))

    return f"978{n:06d}"

def escribir_json(ruta_archivo: str, datos: dict):
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def pedir_texto(terminal, y, x, mensaje) -> str:
    terminal.addstr(y, x, mensaje)
    terminal.refresh()
    curses.echo()  # para que se vea lo que escribes
    texto = terminal.getstr(y, x + len(mensaje), 60).decode("utf-8").strip()
    curses.noecho()
    return texto


def crear_libro(terminal):
    terminal.clear()
    terminal.addstr(0, 0, "CREAR LIBRO.")
    terminal.addstr(1, 0, "Pulsa Enter tras cada campo.")

    genero_raw = pedir_texto(terminal, 3, 0, "Genero: ")
    autor_raw = pedir_texto(terminal, 4, 0, "Autor: ")
    titulo = pedir_texto(terminal, 5, 0, "Titulo: ")

    if not genero_raw or not autor_raw or not titulo:
        terminal.addstr(7, 0, "❌ No se permiten campos vacios. Pulsa una tecla...")
        terminal.getch()
        return

    # Evitar duplicado de género por mayúsculas/acentos
    genero = normalizar_nombre(genero_raw)
    autor = normalizar_nombre(autor_raw)

    ruta_autor = BASE_TIENDA / genero / autor

    titulo_cmp = titulo.strip().lower()

    for f in ruta_autor.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if str(data.get("titulo", "")).strip().lower() == titulo_cmp:
                terminal.addstr(7, 0, "❌ Ya existe un libro con ese titulo para ese autor en ese genero.")
                terminal.getch()
                return
        except Exception:
            # si un json está corrupto, lo ignoramos o podrías avisar
            pass

    # Asegurar base
    BASE_TIENDA.mkdir(exist_ok=True)

    isbn = generar_isbn()

    # Llamar al bash: crea carpetas y archivo vacío
    cmd = ["./scripts/bash/crear_archivo.sh", str(BASE_TIENDA), genero, autor, isbn]
    r = subprocess.run(cmd, capture_output=True, text=True)

    terminal.clear()
    if r.returncode == 0:
        # r.stdout: "CREADO|ruta/del/archivo.json"
        salida = r.stdout.strip()
        _, ruta_json = salida.split("|", 1)

        datos = {
            "isbn": isbn,
            "titulo": titulo,
            "autor": autor_raw,
            "autor_dir": autor,
            "genero": genero_raw,
            "genero_dir": genero
        }

        escribir_json(ruta_json, datos)

        terminal.addstr(0, 0, "✅ Libro creado y JSON guardado")
        terminal.addstr(1, 0, f"Genero : {genero_raw} -> {genero}")
        terminal.addstr(2, 0, f"Autor  : {autor_raw} -> {autor}")
        terminal.addstr(3, 0, f"Titulo : {titulo}")
        terminal.addstr(4, 0, f"ISBN   : {isbn}")
        terminal.addstr(6, 0, f"Archivo: {ruta_json}")
    else:
        terminal.addstr(0, 0, "❌ Error al crear el archivo")
        terminal.addstr(1, 0, (r.stderr.strip() or r.stdout.strip())[:200])


    terminal.addstr(8, 0, "Pulsa una tecla para volver al menu...")
    terminal.getch()

def explorar(terminal):
    limite = BASE_TIENDA.parent          # /tiendas
    ruta = BASE_TIENDA                   # /tiendas/tienda_libros
    seleccion = 0
    offset = 0

    while True:
        terminal.clear()
        terminal.addstr(0, 0, f"📂 Explorador: {ruta}")
        terminal.addstr(1, 0, "Enter: abrir | Backspace: volver | V: ver JSON | D: borrar (libro/autor/genero) | Q: salir")

        if not ruta.exists():
            terminal.addstr(3, 0, "⚠️ La ruta no existe. Pulsa una tecla...")
            terminal.getch()
            return

        # Elementos reales (carpetas primero, luego archivos)
        items = sorted(
            ruta.iterdir(),
            key=lambda p: (p.is_file(), p.name.lower())
        )

        # Lista con entrada "Volver" ficticia
        elementos = [".."] + items

        # --- Scroll ---
        alto = curses.LINES - 4  # líneas disponibles para listar
        if seleccion < offset:
            offset = seleccion
        elif seleccion >= offset + alto:
            offset = seleccion - alto + 1

        visibles = elementos[offset:offset + alto]

        for i, e in enumerate(visibles):
            idx_real = offset + i

            if e == "..":
                nombre = "↩ Volver"
            else:
                nombre = e.name
                if e.is_dir():
                    nombre = f"📁 {nombre}"
                else:
                    nombre = f"📄 {nombre}"

            if idx_real == seleccion:
                terminal.addstr(i + 3, 0, nombre[:curses.COLS - 1], curses.A_REVERSE)
            else:
                terminal.addstr(i + 3, 0, nombre[:curses.COLS - 1])

        terminal.refresh()
        tecla = terminal.getch()

        # salir explorador
        if tecla in (ord("q"), ord("Q")):
            return

        # mover selección
        if tecla == curses.KEY_DOWN and seleccion < len(elementos) - 1:
            seleccion += 1
        elif tecla == curses.KEY_UP and seleccion > 0:
            seleccion -= 1

        # volver (Backspace)
        elif tecla in (curses.KEY_BACKSPACE, 127, 8):
            if ruta != limite:
                ruta = ruta.parent
                seleccion = 0
                offset = 0

        # ver JSON
        elif tecla in (ord("v"), ord("V")):
            elegido = elementos[seleccion]
            if elegido != ".." and elegido.is_file() and elegido.suffix == ".json":
                terminal.clear()
                terminal.addstr(0, 0, f"📄 {elegido.name}")

                try:
                    contenido = elegido.read_text(encoding="utf-8")
                except Exception as ex:
                    contenido = f"Error leyendo archivo: {ex}"

                lineas = contenido.splitlines()
                max_lineas = curses.LINES - 3
                for j, linea in enumerate(lineas[:max_lineas]):
                    terminal.addstr(j + 2, 0, linea[:curses.COLS - 1])

                terminal.addstr(curses.LINES - 1, 0, "Pulsa una tecla para volver...")
                terminal.getch()

        # borrar JSON con tecla D
        elif tecla in (ord("d"), ord("D")):
            elegido = elementos[seleccion]

            if elegido == "..":
                continue

            cmd = None

            # Caso 1: es un libro (archivo .json)
            if elegido.is_file() and elegido.suffix == ".json":
                cmd = ["bash", "./scripts/bash/borrar_por_ruta.sh", str(elegido)]

            # Caso 2: es carpeta (puede ser genero o autor)
            elif elegido.is_dir():

                # 👇 AQUÍ VA LA LÍNEA DEL NIVEL
                nivel = len(elegido.relative_to(BASE_TIENDA).parts)

                if nivel == 1:
                    # Es genero
                    cmd = ["bash", "./scripts/bash/borrar_genero.sh", str(elegido)]
                elif nivel == 2:
                    # Es autor
                    cmd = ["bash", "./scripts/bash/borrar_autor.sh", str(elegido)]
                else:
                    continue

            if cmd is None:
                continue

            curses.endwin()
            r = subprocess.run(cmd)

            terminal = curses.initscr()
            terminal.keypad(True)
            curses.noecho()
            curses.cbreak()
            curses.curs_set(0)

            terminal.clear()
            if r.returncode == 30:
                terminal.addstr(0, 0, "✅ Eliminado correctamente.")
                if seleccion > 0:
                    seleccion -= 1
            elif r.returncode == 40:
                terminal.addstr(0, 0, "Cancelado.")
            else:
                terminal.addstr(0, 0, f"Codigo retorno: {r.returncode}")

            terminal.addstr(2, 0, "Pulsa una tecla para continuar...")
            terminal.getch()





        # entrar con Enter
        elif tecla == ord("\n"):
            elegido = elementos[seleccion]

            if elegido == "..":
                # Permitir salir de tienda_libros hacia /tiendas, pero no más arriba
                if ruta != limite:
                    ruta = ruta.parent
                    seleccion = 0
                    offset = 0

            elif elegido.is_dir():
                ruta = elegido
                seleccion = 0
                offset = 0


def ejecutar_bash_y_volver(terminal, cmd):
    curses.endwin()
    r = subprocess.run(cmd)
    terminal = curses.initscr()
    terminal.keypad(True)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    return terminal, r.returncode


def menu(terminal):
    opciones = ["Crear libro", "Buscar por codigo", "Explorar / Listar", "Salir"]
    seleccion = 0

    while True:
        terminal.clear()
        terminal.addstr(0, 0, "📚 TIENDA DE LIBROS (curses)")
        terminal.addstr(1, 0, "Usa flechas y Enter. (Q para salir)")

        for i, opcion in enumerate(opciones):
            if i == seleccion:
                terminal.addstr(i + 3, 0, opcion, curses.A_REVERSE)
            else:
                terminal.addstr(i + 3, 0, opcion)

        tecla = terminal.getch()

        if tecla in (ord('q'), ord('Q')):
            break
        elif tecla == curses.KEY_DOWN and seleccion < len(opciones) - 1:
            seleccion += 1
        elif tecla == curses.KEY_UP and seleccion > 0:
            seleccion -= 1
        elif tecla == ord('\n'):
            if seleccion == 0:
                crear_libro(terminal)

            elif seleccion == 1:
                terminal, _ = ejecutar_bash_y_volver(terminal, ["bash", "./scripts/bash/buscar_por_codigo.sh"])

            elif seleccion == 2:
                terminal, code = ejecutar_bash_y_volver(terminal, ["bash", "./scripts/bash/borrar_por_codigo.sh"])

                # Mensaje corto tras volver
                terminal.clear()
                if code == 30:
                    terminal.addstr(0, 0, "✅ Libro eliminado.")
                elif code == 40:
                    terminal.addstr(0, 0, "Cancelado.")
                elif code == 20:
                    terminal.addstr(0, 0, "❌ No encontrado.")
                else:
                    terminal.addstr(0, 0, f"Fin de borrado. Codigo: {code}")

                terminal.addstr(2, 0, "Pulsa una tecla para volver al menu...")
                terminal.getch()

            elif seleccion == 3:
                explorar(terminal)

            elif seleccion == 4:
                break




if __name__ == "__main__":
    terminal = curses.initscr()
    terminal.keypad(True)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)

    try:
        menu(terminal)
    finally:
        curses.nocbreak()
        terminal.keypad(False)
        curses.echo()
        curses.endwin()
