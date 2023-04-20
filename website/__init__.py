from flask import Flask

def init_app():
    app = Flask(__name__)
    
    from .task.routes import task_bp
    
    app.register_blueprint(task_bp, url_prefix='/task')
    
    return app
