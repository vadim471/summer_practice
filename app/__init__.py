from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/apartment'

    db.init_app(app)

    login_manager = LoginManager()
    #login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .routes import routes as routes_blueprint
    app.register_blueprint(routes_blueprint)

    with app.app_context():
        db.create_all()


    return app


