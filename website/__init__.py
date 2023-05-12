from flask import Flask

def init_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    
    from website.home.routes import home_bp
    from website.task.routes import task_bp
    from website.api import api_bp
    
    app.register_blueprint(home_bp, url_prefix='/')
    app.register_blueprint(task_bp, url_prefix='/')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from .model import db
    db.init_app(app)
    
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
    from website.model import Task, Module, Testcase
    
    modules = [
        Module(
            module_number=3,
            name='Selection'
        ),
        Module(
            module_number=1,
            name='Input'
        )
    ]
    
    tasks = [
        Task(
            module_id=1,
            task_number=2,
            title='Age',
            description='Ask the user for their age. If their age is greater than 50, print \'You are old\'. If their age is between 18 and 50, print \'You are an adult\'. If their age is below 18, print \'You are a child\'.',
            required_keywords=['if', 'elif', 'else'],
        ),
        Task(
            module_id=2,
            task_number=1,
            title='something',
            description='something something',
            required_keywords=['asdf']
        ),
        Task(
            module_id=2,
            task_number=1,
            title='somethingelse',
            description='something something',
            required_keywords=['asdf']
        )
    ]
    
    testcases = [
        Testcase(
            task_id=1,
            input='15',
            answer_keywords=['child']
        ),
        Testcase(
            task_id=1,
            input='20',
            answer_keywords=['adult']
        ),
        Testcase(
            task_id=1,
            input='100',
            answer_keywords=['old']
        )
    ]
    
    db.session.add_all([*modules, *tasks, *testcases])
    db.session.commit()
