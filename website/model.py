from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    module_id = db.Column(db.ForeignKey('module.id'), nullable=False)
    number = db.Column(db.INTEGER, nullable=False)
    title = db.Column(db.TEXT)
    description = db.Column(db.TEXT)
    required_keywords = db.Column(db.ARRAY(db.TEXT))
    
    module = db.relationship('Module', back_populates='tasks')
    testcases = db.relationship('Testcase', back_populates='task', cascade='all, delete')

class Module(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    number = db.Column(db.INTEGER, nullable=False)
    name = db.Column(db.TEXT)
    
    tasks = db.relationship('Task', back_populates='module', cascade='all, delete')

class Testcase(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    task_id = db.Column(db.ForeignKey('task.id'), nullable=False)
    input = db.Column(db.TEXT)
    answer_keywords = db.Column(db.ARRAY(db.TEXT))
    
    task = db.relationship('Task', back_populates='testcases')

class User(db.Model, UserMixin):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    email = db.Column(db.TEXT, nullable=False, unique=True)
    password_hash = db.Column(db.TEXT, nullable=False)
    name = db.Column(db.TEXT, nullable=False)
    is_admin = db.Column(db.BOOLEAN, nullable=False)
    group_id = db.Column(db.ForeignKey('group.id'))
    
    group = db.relationship('Group', back_populates='users')

class Group(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    name = db.Column(db.TEXT)
    
    users = db.relationship('User', back_populates='group')

# TODO: User: ID, admin?, email, name, group
# TODO: Group: ID, name, users
# TODO: Submission: ID, user id, task id, time, overall verdict, (results)
# TODO: Result: ID, submission id, testcase ID, verdict, message