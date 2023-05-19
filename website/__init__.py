from flask import Flask, request
from flask_login import LoginManager, current_user

from isolate_wrapper import IsolateSandbox

login_manager = LoginManager()

def init_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    
    from website.home.routes import home_bp
    from website.task.routes import task_bp
    from website.user.routes import user_bp
    from website.api import api_bp
    from website.admin.routes import admin_bp
    
    app.register_blueprint(home_bp, url_prefix='/')
    app.register_blueprint(task_bp, url_prefix='/')
    app.register_blueprint(user_bp, url_prefix='/')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from website.model import db, User
    db.init_app(app)
    
    login_manager.init_app(app)
    login_manager.login_view = 'user_bp.login'
    login_manager.login_message_category = 'error'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    @app.before_request
    def restrict():
        allowed_endpoints = (
            login_manager.login_view,  # login page
            'user_bp.register',
            'user_bp.static',
            'static',
        )
        if (not current_user.is_authenticated) and (
            request.endpoint not in allowed_endpoints
        ):
            return login_manager.unauthorized()
    
    with app.app_context():
        db.create_all()
        
        # if app.config['DEV']:
        #     insert_debug_db(db)
            # from website.model import Task, Module, Testcase
            
            # t = Task.query.get(1)
            # db.session.delete(t)
            # db.session.commit()
            # # print(Task.query.get(1).testcases[0].answer_keywords)
    
    return app


def insert_debug_db(db):
    from website.model import Task, Module, Testcase, User, Group
    
    modules = [
        Module(
            number=3,
            name='Selection'
        ),
        Module(
            number=1,
            name='Input'
        ),
        Module(
            number=4,
            name='aswesoemn'
        )
    ]
    
    tasks = [
        Task(
            module_id=1,
            number=2,
            name='Age',
            description='Ask the user for their age. If their age is greater than 50, print \'You are old\'. If their age is between 18 and 50, print \'You are an adult\'. If their age is below 18, print \'You are a child\'.',
            required_keywords=['if', 'elif', 'else'],
        ),
        Task(
            module_id=2,
            number=1,
            name='something',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=2,
            number=2,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=2,
            number=3,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=2,
            number=4,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=1,
            number=2,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=1,
            number=3,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=1,
            number=4,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=1,
            number=5,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=1,
            number=6,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=1,
            number=7,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=1,
            number=8,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=1,
            number=9,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=1,
            number=10,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=1,
            number=11,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=1,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=2,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=3,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=4,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=5,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=6,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=7,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=8,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=9,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=10,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=5,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=6,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=7,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=8,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=9,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=3,
            number=10,
            name='somethingelse',
            description='something something',
            required_keywords=['asdf']
        ),
    ]
    
    testcases = [
        Testcase(
            task_id=1,
            number=1,
            input='15',
            answer_keywords=['child']
        ),
        Testcase(
            task_id=1,
            number=2,
            input='20',
            answer_keywords=['adult']
        ),
        Testcase(
            task_id=1,
            number=3,
            input='100',
            answer_keywords=['old']
        ),
    ]
    
    from werkzeug.security import generate_password_hash
    
    groups = [
        Group(
            name='1F1',
        ),
        Group(
            name='1F2',
        )
    ]
    
    users = [
        User(
            email='john@tonbridge-school.org',
            password_hash=generate_password_hash('john'),
            name='John Stoodunt',
            is_admin=False,
            group_id=1
        ),
        User(
            email='mark@tonbridge-school.org',
            password_hash=generate_password_hash('mark'),
            name='Mark Addmeen',
            is_admin=True,
        )
    ]
    
    db.session.add_all([*modules, *tasks, *testcases, *groups, *users])
    db.session.commit()
