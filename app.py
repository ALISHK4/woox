import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from email_service import send_reservation_email


_DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=_DOTENV_PATH)
print(f"[dotenv] path={_DOTENV_PATH} exists={os.path.exists(_DOTENV_PATH)}")
print("[env] keys:", {k: (os.environ.get(k)[:3] + "***" if os.environ.get(k) else None) for k in [
    "SMTP_HOST", "SMTP_PORT", "SMTP_USER", "TO_EMAIL", "SMTP_USE_TLS"
]})


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False
    # Разрешаем CORS для фронтенда на file:// и localhost
    CORS(app, resources={r"/*": {"origins": ["*"]}})

    @app.get("/health")
    def health() -> tuple:
        return jsonify({"status": "ok"}), 200

    @app.post("/api/reservations")
    def create_reservation() -> tuple:
        data = request.get_json(silent=True) or request.form.to_dict()
        name = data.get("Name", "").strip()
        phone = data.get("Number", "").strip()
        guests = data.get("Guests", "").strip()
        date = data.get("date", "").strip()
        destination = data.get("Destination", "").strip()

        missing = [k for k, v in {
            "Name": name,
            "Number": phone,
            "Guests": guests,
            "date": date,
            "Destination": destination,
        }.items() if not v]
        if missing:
            return jsonify({"ok": False, "error": f"Отсутствуют поля: {', '.join(missing)}"}), 400

        try:
            send_reservation_email(
                name=name,
                phone=phone,
                guests=str(guests),
                date=date,
                destination=destination,
            )
            return jsonify({"ok": True, "message": "Бронирование отправлено"}), 200
        except Exception as exc:
            return jsonify({"ok": False, "error": str(exc)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

