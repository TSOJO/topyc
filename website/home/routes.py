from flask import Blueprint, render_template
from flask_login import current_user

from website.model import db, Module, Task, Submission
from isolate_wrapper import Verdict

home_bp = Blueprint(
    'home_bp', __name__, template_folder='templates', static_folder='static'
)

@home_bp.route('/')
def home():
    modules = Module.query.order_by(Module.number).all()
    user_done_tasks_query = db.session.query(Task).join(Submission).filter(Submission.user == current_user, Submission.overall_verdict == Verdict.AC).distinct()
    user_done_tasks = [r for r in user_done_tasks_query]
    user_done_modules = [m for m in modules if all(t in user_done_tasks for t in m.tasks)]
    return render_template('home.html', modules=modules, user_done_tasks=user_done_tasks, user_done_modules=user_done_modules)
