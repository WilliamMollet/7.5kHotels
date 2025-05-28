from flask import Flask

# Initialisation de l'application Flask
app = Flask(__name__)

# Définition d'une route simple
@app.route('/')
def hello_world():
    return 'Hello, Flask!'

# Lancement du serveur
if __name__ == '__main__':
    app.run(debug=True)
