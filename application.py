from flask import Flask
from flask_restful import Api

from config import Config
from models import db
from resources.blacklist import BlacklistResource, BlacklistQueryResource
from schemas import ma


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.update(config_overrides or {})

    db.init_app(app)
    ma.init_app(app)

    api = Api(app)
    api.add_resource(BlacklistResource, "/blacklists")
    api.add_resource(BlacklistQueryResource, "/blacklists/<string:email>")

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"db.create_all() failed: {e}")

    return app


application = create_app()

if __name__ == "__main__":
    application.run(debug=False)
