from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    module_id = db.Column(db.ForeignKey('module.id'))
    task_number = db.Column(db.INTEGER)
    title = db.Column(db.TEXT)
    description = db.Column(db.TEXT)
    required_keywords = db.Column(db.ARRAY(db.TEXT))
    
    module = db.relationship('Module', back_populates='tasks')
    testcases = db.relationship('Testcase', back_populates='task', cascade='all, delete')
    
    __table_args__ = (
        db.UniqueConstraint(module_id, task_number),
    )

class Module(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.TEXT)
    
    tasks = db.relationship('Task', back_populates='module', cascade='all, delete')

class Testcase(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    task_id = db.Column(db.ForeignKey('task.id'))
    input = db.Column(db.TEXT)
    answer_keywords = db.Column(db.ARRAY(db.TEXT))
    
    task = db.relationship('Task', back_populates='testcases')

# TODO: User: ID, admin?, email, name, group
# TODO: Group: ID, name, users
# TODO: Submission: ID, user id, task id, time, overall verdict, (results)
# TODO: Result: ID, submission id, testcase ID, verdict, message