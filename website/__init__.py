from flask import Flask

def init_app():
    app = Flask(__name__)
    
    from .task.routes import task_bp
    from .api import api_bp
    
    app.register_blueprint(task_bp, url_prefix='/task')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
