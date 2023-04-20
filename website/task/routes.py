from flask import Blueprint, render_template

task_bp = Blueprint(
    'task_bp', __name__, template_folder='templates', static_folder='static'
)

class DebugTask:
    def __init__(self):
        self.title = 'Task 4.3: Age'
        self.required_keywords = ['if', 'elif', 'else']
        self.description = 'Ask the user for their age. If their age is greater than 50, print \'You are old\'. If their age is between 18 and 50, print \'You are an adult\'. If their age is below 18, print \'You are a child\'.'

@task_bp.route('/<id>')
def task(id):
    return render_template('task.html', task=DebugTask())
