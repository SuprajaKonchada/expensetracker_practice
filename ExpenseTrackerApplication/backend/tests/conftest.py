import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from app import create_app
import db as db_module


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_expense_tracker.db")


@pytest.fixture
def app(db_path):
    return create_app(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def conn(db_path):
    db_module.init_db(db_path)
    connection = db_module.get_connection(db_path)
    yield connection
    connection.close()
