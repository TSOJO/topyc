from flask import Blueprint, render_template, abort, url_for
from flask_login import current_user

from website.model import db, Task, Lesson
from website.util import get_previous_task, get_next_task
from isolate_wrapper import Verdict

task_bp = Blueprint(
    'task_bp', __name__, template_folder='templates', static_folder='static', static_url_path='/task/static'
)

@task_bp.route('/<module_number>/<task_number>')
def task(module_number, task_number):
    if not current_user.is_admin and not current_user.group:
        abort(403, description='You must be in a group to do tasks. Join a group <a href="' + url_for('user_bp.settings') + '" class="text-decoration-none">here</a>.')
    
    
    task = db.first_or_404(
        Task.query.filter(
            Task.module.has(number=module_number),
            Task.number==task_number
        )
    )
    
    if not (current_user.is_admin or task.module.is_visible):
        abort(403, description='The module to which this task belongs is marked as invisible by an admin.')
        
    verdict_map = {v.name: v.value for v in Verdict}
    previous_task = get_previous_task(task)
    next_task = get_next_task(task)
    return render_template(
        'task.html',
        task=task,
        verdict_map=verdict_map,
        previous_task=previous_task,
        next_task=next_task
    )

@task_bp.route('/<module_number>/lesson')
def lesson(module_number):
    lesson = db.first_or_404(
        Lesson.query.filter(
            Lesson.module.has(number=module_number)
        )
    )
    return render_template('lesson.html', lesson=lesson)
