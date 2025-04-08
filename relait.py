from flask import Flask, request, jsonify

app = Flask(__name__)

serveurs = []
clients = []
messages = []
mot_de_passe = "SERVEUR"

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "Disponible" if serveurs else "Indisponible"})

@app.route("/connect", methods=["POST"])
def connecter():
    data = request.get_json()
    role = data.get("role")
    mdp = data.get("mot_de_passe")

    if role == "serveur" and mdp == mot_de_passe:
        serveurs.append(request.remote_addr)
        return jsonify({"message": f"Serveur {request.remote_addr} connecté"}), 200
    elif role == "client":
        clients.append(request.remote_addr)
        return jsonify({"message": f"Client {request.remote_addr} connecté"}), 200
    else:
        return jsonify({"message": "Requête invalide"}), 400

@app.route("/send", methods=["POST"])
def envoyer():
    data = request.get_json()
    role = data.get("role")
    contenu = data.get("message")

    if not contenu:
        return jsonify({"message": "Message vide"}), 400

    messages.append((role, contenu))
    return jsonify({"message": "Message relayé"}), 200

@app.route("/messages", methods=["GET"])
def recevoir():
    return jsonify(messages)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4400)
