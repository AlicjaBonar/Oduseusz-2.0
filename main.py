from flask import Flask, jsonify, request, g
from app.database.database import SessionLocal, Base, engine
from app.models import User  # przykładowy model

app = Flask(__name__)

# Tworzymy tabele, jeśli nie istnieją
Base.metadata.create_all(bind=engine)

# 🔹 Otwieramy sesję przed każdym żądaniem
@app.before_request
def create_session():
    g.db = SessionLocal()

# 🔹 Zamykanie sesji po zakończeniu żądania
@app.teardown_request
def shutdown_session(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# 🔹 Przykład: dodanie użytkownika
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    user = User(username=data["username"], email=data["email"])
    g.db.add(user)
    g.db.commit()
    return jsonify({"id": user.id, "username": user.username, "email": user.email})

# 🔹 Przykład: pobranie użytkowników
@app.route("/users", methods=["GET"])
def get_users():
    users = g.db.query(User).all()
    return jsonify([{"id": u.id, "username": u.username, "email": u.email} for u in users])

if __name__ == "__main__":
    app.run(debug=True)
