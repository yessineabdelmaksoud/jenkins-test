from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    raise ValueError("💥 Erreur simulée !") 
    return "Hello, Jenkins Pipeline!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
