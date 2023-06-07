from flask import Blueprint, render_template
from website.model import db, Task, Lesson
from isolate_wrapper import Verdict

task_bp = Blueprint(
    'task_bp', __name__, template_folder='templates', static_folder='static', static_url_path='/task/static'
)

@task_bp.route('/<module_number>/<task_number>')
def task(module_number, task_number):
    task = db.first_or_404(
        Task.query.filter(
            Task.module.has(number=module_number),
            Task.number==task_number
        )
    )
    verdict_map = {v.name: v.value for v in Verdict}
    return render_template('task.html', task=task, verdict_map=verdict_map)

@task_bp.route('/<module_number>/lesson')
def lesson(module_number):
    lesson = db.first_or_404(
        Lesson.query.filter(
            Lesson.module.has(number=module_number)
        )
    )
    print(lesson.text)
    return render_template('lesson.html', lesson=lesson)
