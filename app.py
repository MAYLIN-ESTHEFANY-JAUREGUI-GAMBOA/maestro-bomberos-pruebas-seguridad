import os
import re
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

load_dotenv()

db = SQLAlchemy()

ESPECIALIDADES = {"Rescate", "Incendios", "Primeros auxilios"}


class Bombero(db.Model):
    __tablename__ = "bomberos"

    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(8), unique=True, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(80), nullable=False)
    estado = db.Column(db.Boolean, default=True, nullable=False)


def _respuesta_bombero(bombero):
    return {
        "id": bombero.id,
        "dni": bombero.dni,
        "nombres": bombero.nombres,
        "apellidos": bombero.apellidos,
        "especialidad": bombero.especialidad,
        "estado": bombero.estado,
    }


def _validar_datos(datos):
    if not isinstance(datos, dict):
        return None, "Envía los datos del bombero en formato JSON."

    campos = ("dni", "nombres", "apellidos", "especialidad")
    valores = {
        campo: datos.get(campo).strip()
        if isinstance(datos.get(campo), str)
        else ""
        for campo in campos
    }

    if not all(valores.values()):
        return None, "Completa todos los campos obligatorios."
    if not re.fullmatch(r"\d{8}", valores["dni"]):
        return None, "El DNI debe contener exactamente 8 dígitos."
    if len(valores["nombres"]) > 100 or len(valores["apellidos"]) > 100:
        return None, "Nombres y apellidos no pueden superar los 100 caracteres."
    if valores["especialidad"] not in ESPECIALIDADES:
        return None, "Selecciona una especialidad válida."

    return valores, None


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    database_url = os.getenv("DATABASE_URL") or (
        "sqlite:///" + str(Path(app.instance_path) / "maestro_bomberos.db")
    )
    if database_url.startswith("postgresql://"):
        database_url = "postgresql+psycopg2://" + database_url[len("postgresql://") :]
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY") or "dev-only-change-me",
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JSON_AS_ASCII=False,
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    @app.after_request
    def aplicar_cabeceras_seguridad(respuesta):
        respuesta.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; script-src 'self'; "
            "img-src 'self' data:; font-src 'self'; connect-src 'self'; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        respuesta.headers["X-Content-Type-Options"] = "nosniff"
        respuesta.headers["X-Frame-Options"] = "DENY"
        respuesta.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        respuesta.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        respuesta.headers["Cache-Control"] = "no-store" if request.path.startswith("/api/") else (
            "no-cache, no-store, must-revalidate"
        )
        return respuesta

    @app.get("/favicon.ico")
    def favicon():
        return send_from_directory(app.static_folder, "favicon.svg", mimetype="image/svg+xml")

    @app.get("/")
    def inicio():
        return render_template("index.html")

    @app.get("/api/bomberos")
    def listar_bomberos():
        consulta = Bombero.query
        estado = request.args.get("estado")
        if estado == "activo":
            consulta = consulta.filter_by(estado=True)
        elif estado == "inactivo":
            consulta = consulta.filter_by(estado=False)
        bomberos = consulta.order_by(Bombero.id.desc()).all()
        return jsonify([_respuesta_bombero(bombero) for bombero in bomberos])

    @app.post("/api/bomberos")
    def registrar_bombero():
        datos, error = _validar_datos(request.get_json(silent=True))
        if error:
            return jsonify({"mensaje": error}), 400
        if Bombero.query.filter_by(dni=datos["dni"]).first():
            return jsonify({"mensaje": "Ese DNI ya está registrado."}), 409

        bombero = Bombero(**datos)
        db.session.add(bombero)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"mensaje": "Ese DNI ya está registrado."}), 409
        return jsonify(
            {"mensaje": "Bombero registrado correctamente.", "bombero": _respuesta_bombero(bombero)}
        ), 201

    @app.get("/api/bomberos/<int:bombero_id>")
    def consultar_bombero(bombero_id):
        bombero = db.session.get(Bombero, bombero_id)
        if not bombero:
            return jsonify({"mensaje": "Bombero no encontrado."}), 404
        return jsonify(_respuesta_bombero(bombero))

    @app.put("/api/bomberos/<int:bombero_id>")
    def actualizar_bombero(bombero_id):
        bombero = db.session.get(Bombero, bombero_id)
        if not bombero:
            return jsonify({"mensaje": "Bombero no encontrado."}), 404
        datos, error = _validar_datos(request.get_json(silent=True))
        if error:
            return jsonify({"mensaje": error}), 400
        duplicado = Bombero.query.filter(
            Bombero.dni == datos["dni"], Bombero.id != bombero_id
        ).first()
        if duplicado:
            return jsonify({"mensaje": "Ese DNI ya está registrado."}), 409

        for campo, valor in datos.items():
            setattr(bombero, campo, valor)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"mensaje": "Ese DNI ya está registrado."}), 409
        return jsonify(
            {"mensaje": "Datos actualizados correctamente.", "bombero": _respuesta_bombero(bombero)}
        )

    @app.patch("/api/bomberos/<int:bombero_id>/estado")
    def cambiar_estado(bombero_id):
        bombero = db.session.get(Bombero, bombero_id)
        if not bombero:
            return jsonify({"mensaje": "Bombero no encontrado."}), 404
        datos = request.get_json(silent=True)
        if not isinstance(datos, dict) or not isinstance(datos.get("estado"), bool):
            return jsonify({"mensaje": "El estado debe ser verdadero o falso."}), 400
        bombero.estado = datos["estado"]
        db.session.commit()
        return jsonify({"mensaje": "Estado actualizado correctamente."})

    @app.delete("/api/bomberos/<int:bombero_id>")
    def eliminar_bombero(bombero_id):
        bombero = db.session.get(Bombero, bombero_id)
        if not bombero:
            return jsonify({"mensaje": "Bombero no encontrado."}), 404
        db.session.delete(bombero)
        db.session.commit()
        return jsonify({"mensaje": "Registro eliminado correctamente."})

    return app


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
