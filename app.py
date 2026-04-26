import os
from flask import Flask
from config.settings import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config.get("UPLOAD_FOLDER", "files/uploads"), exist_ok=True)

    # Register blueprints
    from blueprints.main import main_bp
    from blueprints.flags import flags_bp
    from blueprints.retention import retention_bp
    from blueprints.market_access import market_access_bp
    from blueprints.chat import chat_bp
    from blueprints.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(flags_bp, url_prefix="/flags")
    app.register_blueprint(retention_bp, url_prefix="/retention")
    app.register_blueprint(market_access_bp, url_prefix="/market-access")
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(api_bp, url_prefix="/api")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8513, debug=True)
