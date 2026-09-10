"""Flask app factory for the Expense Tracker API."""
import sqlite3
from functools import partial

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

import config
import db
from routes_budgets import budgets_bp
from routes_expenses import expenses_bp
from routes_summary import summary_bp


def create_app(db_path=None):
    """Build and configure the Flask application.

    Initializes the SQLite database, registers the expense/budget/summary blueprints,
    and wires up the health check and global error handlers. `db_path` overrides
    `config.DB_PATH`, primarily for test isolation.
    """
    app = Flask(__name__)
    CORS(app)

    db.init_db(db_path)
    app.config["GET_CONN"] = partial(db.get_connection, db_path)

    app.register_blueprint(expenses_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(summary_bp)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(sqlite3.Error)
    def handle_database_error(err):
        """Log any SQLite error and return a generic 500 response, hiding internal details."""
        app.logger.exception("Database error")
        return jsonify({"error": "A database error occurred."}), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        """Render a standard Flask HTTP exception (e.g. 404) as consistent JSON."""
        return jsonify({"error": err.description}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        """Log any unhandled exception and return a generic 500 response, hiding internal details."""
        app.logger.exception("Unhandled error")
        return jsonify({"error": "An unexpected error occurred."}), 500

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
