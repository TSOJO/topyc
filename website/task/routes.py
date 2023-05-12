from flask import Blueprint, render_template
from website.model import db, Task

task_bp = Blueprint(
    'task_bp', __name__, template_folder='templates', static_folder='static', static_url_path='/task/static'
)

@task_bp.route('/<module_number>/<task_number>')
def task(module_number, task_number):
    task = db.first_or_404(
        Task.query.filter(
            Task.module.has(module_number=module_number),
            Task.task_number==task_number
        )
    )
    return render_template('task.html', task=task)
