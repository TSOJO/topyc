from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import UserMixin

from isolate_wrapper import Verdict

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    module_id = db.Column(db.ForeignKey('module.id'), nullable=False)
    number = db.Column(db.INTEGER, nullable=False)
    name = db.Column(db.TEXT)
    description = db.Column(db.TEXT)
    hint = db.Column(db.TEXT)
    required_keywords = db.Column(db.ARRAY(db.TEXT))
    
    module = db.relationship('Module', back_populates='tasks')
    testcases = db.relationship('Testcase', back_populates='task', cascade='all, delete')
    submissions = db.relationship('Submission', back_populates='task', cascade='all, delete-orphan')

class Lesson(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    module_id = db.Column(db.ForeignKey('module.id'), nullable=False, unique=True)
    text = db.Column(db.TEXT)
    
    module = db.relationship('Module', back_populates='lesson')

module_group_visibility = db.Table(
    'module_group',
    db.Column('module_id', db.ForeignKey('module.id'), primary_key=True),
    db.Column('group_id', db.ForeignKey('group.id'), primary_key=True)
)

class Module(db.Model):
    __tablename__ = 'module'
    
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    number = db.Column(db.INTEGER, nullable=False)
    name = db.Column(db.TEXT)
    
    visible_to = db.relationship('Group', secondary=module_group_visibility)
    tasks = db.relationship('Task', back_populates='module', cascade='all, delete-orphan')
    lesson = db.relationship('Lesson', uselist=False, back_populates='module', cascade='all, delete-orphan')

class Testcase(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    task_id = db.Column(db.ForeignKey('task.id'))
    input = db.Column(db.TEXT)
    answer_keywords = db.Column(db.ARRAY(db.TEXT))
    is_ordered = db.Column(db.BOOLEAN, nullable=False, server_default='false')  # Whether answer keywords are ordered.
    
    task = db.relationship('Task', back_populates='testcases')
    testcase_results = db.relationship('TestcaseResult', back_populates='testcase', cascade='all, delete-orphan')

class User(db.Model, UserMixin):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    email = db.Column(db.TEXT, nullable=False, unique=True)
    password_hash = db.Column(db.TEXT, nullable=False)
    name = db.Column(db.TEXT, nullable=False)
    is_admin = db.Column(db.BOOLEAN, nullable=False)
    group_id = db.Column(db.ForeignKey('group.id'))
    
    group = db.relationship('Group', back_populates='users')
    submissions = db.relationship('Submission', back_populates='user', cascade='all, delete-orphan')

class Group(db.Model):
    __tablename__ = 'group'
    
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    name = db.Column(db.TEXT)
    
    users = db.relationship('User', back_populates='group')

class Submission(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.ForeignKey('task.id'), nullable=False)
    time_submitted = db.Column(db.TIMESTAMP, nullable=False, server_default=func.now())
    overall_verdict = db.Column(db.Enum(Verdict), nullable=False)
    source_code = db.Column(db.TEXT, nullable=False)
    
    user = db.relationship('User', back_populates='submissions')
    task = db.relationship('Task', back_populates='submissions')
    testcase_results = db.relationship('TestcaseResult', back_populates='submission', cascade='all, delete-orphan')

class TestcaseResult(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    submission_id = db.Column(db.ForeignKey('submission.id'))
    testcase_id = db.Column(db.ForeignKey('testcase.id'))
    verdict = db.Column(db.Enum(Verdict))
    output = db.Column(db.TEXT)
    message = db.Column(db.TEXT)
    
    submission = db.relationship('Submission', back_populates='testcase_results')
    testcase = db.relationship('Testcase', back_populates='testcase_results')

