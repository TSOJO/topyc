from flask import Blueprint, render_template, abort, request, flash
from flask_login import current_user

from website.model import db, User, Group, Task, Module

admin_bp = Blueprint(
    'admin_bp', __name__, template_folder='templates', static_folder='static'
)

@admin_bp.before_request
def unauthorised():
    if not current_user.is_admin:
        abort(403, description='Admin account required to access this page.')

@admin_bp.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        if request.form['action'] == 'change_group':
            user_id = request.form['user_id']
            group_id = request.form['group_id']
            
            user = User.query.get(user_id)
            user.group = Group.query.get(group_id)
        
        elif request.form['action'] == 'delete_user':
            user_id = request.form['user_id']
            db.session.delete(User.query.get(user_id))
            
        db.session.commit()
        flash('Saved', 'success')
    users_page = db.paginate(db.select(User).order_by(User.email))  # defaults to 20 per page and gets page number from `request.args`
    groups = Group.query.all()
    return render_template('users.html', users_page=users_page, groups=groups)

@admin_bp.route('/user/progress/<user_id>')
def user_progress(user_id):
    user = User.query.get(user_id)
    tasks = Task.query.all()
    modules = Module.query.all()
    return render_template('user_progress.html', user=user, tasks=tasks, modules=modules)

@admin_bp.route('/groups')
def groups():
    groups = Group.query.order_by(Group.name).all()
    return render_template('admin.html', groups=groups)

@admin_bp.route('/<group_id>')
def progress(group_id):
    return 'ha'

@admin_bp.route('/<group_id>/edit')
def edit_group(group_id):
    return 'he'

@admin_bp.route('/tasks')
def tasks():
    return 'hehe'
