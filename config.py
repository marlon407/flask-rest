from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

config = {
    'SECRET_KEY': 'mysupersecretkey',
    'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/test.db'
}
