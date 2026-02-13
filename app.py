from flask import Flask, render_template, make_response, redirect, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route('/form_login')
def login():
    return render_template('login_template.html')

@app.route("/saludo/<nombre>")
def saludo(nombre):
    return f"HOLA {nombre} !"


@app.route('/sign_in', methods=['POST'])  # Define la ruta para el método POST en /sign_in
def sign_in():
    # Obtener los datos del formulario (login y contraseña)
    login = request.form['login']  # Obtiene el valor del campo 'login' (correo o usuario)
    passwd = request.form['passwd']  # Obtiene el valor del campo 'passwd' (contraseña)

    # Imprimir el usuario y la contraseña en la consola (para propósitos de depuración)
    print(f'Usuario: {login}')  # Muestra el login (usuario o correo)
    print(f'Contraseña: {passwd}')  # Muestra la contraseña

    # Crear una respuesta de redirección a la página '/login_ok'
    response = make_response(redirect('/login_ok'))  # Redirige a la página '/login_ok'

    # Establecer una cookie con el token JWT (ejemplo en este caso)
    response.set_cookie('token', 'esto es un token de ejemplo')  # Se establece una cookie llamada 'token'

    # Establecer una cookie con el nombre de usuario (ejemplo en este caso)
    response.set_cookie('userlogin', 'el usuario')  # Se establece una cookie llamada 'userlogin'

    # Devolver la respuesta con las cookies configuradas
    return response  # Retorna la respuesta con las cookies y la redirección


if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 80)