from flask import Blueprint, render_template
from website.model import db, Task

task_bp = Blueprint(
    'task_bp', __name__, template_folder='templates', static_folder='static', static_url_path='/task/static'
)

@task_bp.route('/<module_id>/<task_number>')
def task(module_id, task_number):
    task = db.first_or_404(
        Task.query.filter_by(
            module_id=module_id, 
            task_number=task_number
        )
    )
    return render_template('task.html', task=task)
