"""REST API entry point."""
from flask import Flask
from controllers.users import users_bp

app = Flask(__name__)
app.register_blueprint(users_bp)

if __name__ == "__main__":
    app.run(debug=True)
