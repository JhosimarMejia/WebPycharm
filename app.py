from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Hello World!</h1>"

@app.route("/saludo/<nombre>")
def saludo(nombre):
    return f"HOLA {nombre} !"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 80)