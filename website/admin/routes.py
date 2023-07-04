from flask import Blueprint, render_template, abort, request, flash, send_file, redirect, url_for
from flask_login import current_user
from io import BytesIO
from openpyxl import Workbook
import json
import zipfile
from werkzeug.security import generate_password_hash

from website.model import db, User, Group, Task, Module, Submission, Testcase, Lesson
from website.util import generate_password, send_email
from isolate_wrapper import Verdict

admin_bp = Blueprint(
    'admin_bp', __name__, template_folder='templates', static_folder='static'
)

@admin_bp.before_request
def unauthorised():
    if not current_user.is_admin:
        abort(403, description='Admin account required to access this page.')
        
@admin_bp.route('/submission/<submission_id>')
def submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    verdict_map = {v.name: v.value for v in Verdict}
    verdict_map['AC'] = 'Correct'
    return render_template('submission.html', submission=submission, verdict_map=verdict_map)

@admin_bp.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        if request.form['action'] == 'change_name':
            name = request.form['name']
            user_id = request.form['user_id']
            
            user = User.query.get(user_id)
            user.name = name
            
        elif request.form['action'] == 'change_group':
            user_id = request.form['user_id']
            group_id = request.form['group_id']
            
            user = User.query.get(user_id)
            user.group = Group.query.get(group_id)
        
        elif request.form['action'] == 'delete_user':
            user_id = request.form['user_id']
            db.session.delete(User.query.get(user_id))
        
        elif request.form['action'] == 'update_admin':
            user_id = request.form['user_id']
            
            user = User.query.get(user_id)
            user.is_admin = 'admin_check' in request.form
        
        elif request.form['action'] == 'reset_password':
            user_id = request.form['user_id']
            user = User.query.get(user_id)
            
            password = generate_password()
            password_hash = generate_password_hash(password)
            user.password_hash = password_hash
            
            send_email(
                to_email=user.email,
                subject='Your new ToPyC password',
                body=f'Hi {user.name},\nYour new password is: {password}\nBest regards,\nToPyC'
            )
            
            flash(f'<span>Password reset successfully; the new password has been sent to {user.email}. {user.name}\'s new password is:<br /><strong class=\"consolas\">{password}</strong><br />This is the last time you will see it!</span>', 'success')            
            
        db.session.commit()
        flash('Saved', 'success')
        
    users_page = db.paginate(db.select(User).order_by(User.email))  # defaults to 20 per page and gets page number from `request.args`
    groups = Group.query.all()
    return render_template('users.html', users_page=users_page, groups=groups)

@admin_bp.route('/user/progress/<user_id>')
def user_progress(user_id):
    user = User.query.get_or_404(user_id)
    tasks = Task.query.all()
    modules = Module.query.all()
    correct_tasks = db.session.query(Task) \
                                        .join(Submission) \
                                        .filter(Submission.user_id == user_id,
                                                Submission.overall_verdict == Verdict.AC) \
                                        .distinct()
    tasks_with_submissions = db.session.query(Task) \
                                                .join(Submission) \
                                                .filter(Task.submissions,
                                                        Submission.user_id == user_id) \
                                                .distinct()
    verdict_map = {v.name: v.value for v in Verdict}
    verdict_map['AC'] = 'Correct'
    
    return render_template(
        'user_progress.html',
        user=user,
        tasks=tasks,
        modules=modules,
        correct_tasks=correct_tasks,
        tasks_with_submissions=tasks_with_submissions,
        verdict_map=verdict_map
    )

@admin_bp.route('/groups', methods=['GET', 'POST'])
def groups():
    if request.method == 'POST':
        if request.form['action'] == 'delete_group':
            group_id = request.form['group_id']
            db.session.delete(Group.query.get(group_id))
            
        db.session.commit()
        flash('Group deleted', 'success')
        
    groups = Group.query.order_by(Group.name).all()
    return render_template('groups.html', groups=groups)

@admin_bp.route('/new-group', methods=['POST'])
def new_group():
    group_name = request.form['group_name']
    group = Group(
        name=group_name
    )
    db.session.add(group)
    db.session.commit()
    flash('Saved', 'success')
    return redirect(url_for('admin_bp.groups'))

def get_group_excel(group):
    wb = Workbook()
    ws = wb.active
    
    modules = Module.query.order_by(Module.number).all()
    sorted_tasks = []
    for module in modules:
        for task in sorted(module.tasks, key=lambda t: t.number):
            sorted_tasks.append(task)
    
    ws.append([''] + [f'{task.module.number}.{task.number}: {task.name}' for task in sorted_tasks])
    
    for user in sorted(group.users, key=lambda u: u.email):
        correct_tasks = db.session.query(Task) \
                                            .join(Submission) \
                                            .filter(Submission.user_id == user.id,
                                                    Submission.overall_verdict == Verdict.AC) \
                                            .distinct()
        tasks_with_submissions = db.session.query(Task) \
                                            .join(Submission) \
                                            .filter(Task.submissions,
                                                    Submission.user_id == user.id) \
                                            .distinct()
        
        user_row = [user.email]
        for task in sorted_tasks:
            if task in correct_tasks:
                user_row.append('Correct')
            elif task in tasks_with_submissions:
                user_row.append('Attempted')
            else:
                user_row.append('Not attempted')
        ws.append(user_row)
    
    return wb

@admin_bp.route('/group/<group_id>/download')
def download_group_excel(group_id):
    group = Group.query.get_or_404(group_id)
    
    file_stream = BytesIO()
    wb = get_group_excel(group)
    wb.save(file_stream)
    file_stream.seek(0)
    
    return send_file(
        file_stream,
        as_attachment=True,
        download_name=f'{group.name}.xlsx'
    )

@admin_bp.route('/backup-restore', methods=['GET', 'POST'])
def backup_restore():
    if request.method == 'POST':
        modules_json = request.form['modules']
        tasks_json = request.form['tasks']
        lessons_json = request.form['lessons']
        
        try:
            for module in Module.query.all():
                db.session.delete(module)
            
            for module in json.loads(modules_json):
                db.session.add(Module(**module))
            for task in json.loads(tasks_json):
                db.session.add(Task(**task))
            for lesson in json.loads(lessons_json):
                db.session.add(Lesson(**lesson))
            
            db.session.commit()
        except Exception as e:
            flash(f'<span><strong>Restore cancelled. Something went wrong:</strong><br />{e}<br /><strong>Make sure you are pasting the .json files exactly.</strong></span>', 'error')
            db.session.rollback()
        else:
            flash('Backup restored', 'success')
        
    return render_template('backup_restore.html')

def table_to_json(table):
    return json.dumps(
        [dict((col, getattr(row, col)) for col in row.__table__.columns.keys()) for row in table.query.all()],
        indent=4
    )

@admin_bp.route('/download-backup')
def download_backup():
    file_stream = BytesIO()
    
    with zipfile.ZipFile(file_stream, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_name, table in [
            ('tasks.json', Task),
            ('lessons.json', Lesson),
            ('modules.json', Module)
        ]:
            zipf.writestr(file_name, table_to_json(table))
    
    file_stream.seek(0)
    
    return send_file(
        file_stream,
        as_attachment=True,
        download_name='backup.zip'
    )

@admin_bp.route('/group/<group_id>', methods=['GET', 'POST'])
def group_progress(group_id):
    if request.method == 'POST':
        if request.form['action'] == 'remove_user':
            user_id = request.form['user_id']
            user = User.query.get(user_id)
            user.group_id = None
        
        db.session.commit()
        flash('User removed', 'success')
    
    group = Group.query.get_or_404(group_id)
    tasks = Task.query.all()
    modules = Module.query.all()
    correct_tasks = {}
    attempted_tasks = {}
    
    all_user_tasks = db.session.query(User, Task) \
                                    .select_from(User) \
                                    .join(Submission) \
                                    .join(Task) \
                                    .join(Group) \
                                    .filter(Group.id == group.id)
                                    
    correct_user_tasks = all_user_tasks.filter(Submission.overall_verdict == Verdict.AC).distinct()
    for user, task in correct_user_tasks:
        if user.id not in correct_tasks:
            correct_tasks[user.id] = set()
        correct_tasks[user.id].add(task)
        
    # Attempted means the user has submitted something. May or may not be correct.
    # If user has not submitted anything to the task, then the Task will not be joined as it is joined from Submission.
    attempted_user_tasks = all_user_tasks.distinct()
    for user, task in attempted_user_tasks:
        if user.id not in attempted_tasks:
            attempted_tasks[user.id] = set()
        attempted_tasks[user.id].add(task)
        
    verdict_map = {v.name: v.value for v in Verdict}
    verdict_map['AC'] = 'Correct'
    
    return render_template(
        'group_progress.html',
        group=group,
        tasks=tasks,
        modules=modules,
        correct_tasks=correct_tasks,
        attempted_tasks=attempted_tasks,
        verdict_map=verdict_map
    )

@admin_bp.route('/new-module', methods=['POST'])
def new_module():
    module_number = request.form['module_number']
    module_name = request.form['module_name']
    
    module = Module(
        number=module_number,
        name=module_name,
        is_visible=True
    )
    
    db.session.add(module)
    db.session.commit()
    flash('Module created', 'success')
    return redirect(url_for('home_bp.home'))

@admin_bp.route('/edit-module', methods=['POST'])
def edit_module():
    module_id = request.form['module_id']
    module_number = request.form['module_number']
    module_name = request.form['module_name']
    module_visible = 'module_visible' in request.form
    
    module = Module.query.get_or_404(module_id)
    module.number = module_number
    module.name = module_name
    module.is_visible = module_visible

    db.session.commit()
    flash('Module saved', 'success')
    return redirect(url_for('home_bp.home'))

@admin_bp.route('/delete-module', methods=['POST'])
def delete_module():
    module_id = request.form['module_id']
    module = Module.query.get_or_404(module_id)
    
    db.session.delete(module)
    db.session.commit()
    
    flash('Module deleted', 'success')
    return redirect(url_for('home_bp.home'))

@admin_bp.route('/new-task', methods=['POST'])
def new_task():
    module_id = request.form['module_id']
    task_number = request.form['task_number']
    
    task = Task(
        number=task_number,
        module_id=module_id
    )
    
    db.session.add(task)
    db.session.commit()
    flash('Task created', 'success')
    return redirect(url_for('admin_bp.edit_task', task_id=task.id))

@admin_bp.route('/task/<task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if request.method == 'POST':
        task.module_id = request.form['module_id']
        task.number = request.form['number']
        task.name = request.form['name']
        task.description = request.form['description']
        raw_required_keywords = request.form['required_keywords'].split('\n')
        task.required_keywords = [x.strip() for x in raw_required_keywords]
        
        task.testcases = []
        for k, v in request.form.items():
            if k.startswith('input'):
                # 'Y\r\nN' -> 'Y\nN'
                v = '\n'.join([x.strip() for x in v.split()])
                # Form input names are e.g., input2, answer2, etc.
                raw_answer_keywords = request.form[k.replace('input', 'answer')].strip().split('\n')
                answer_keywords = [x.strip() for x in raw_answer_keywords]
                is_ordered = k.replace('input', 'ordered') in request.form
                task.testcases.append(Testcase(
                    input=v,
                    answer_keywords=answer_keywords,
                    is_ordered=is_ordered
                ))
        
        db.session.commit()
        flash('Task saved', 'success')
        
    modules = Module.query.all()
    return render_template('edit_task.html', task=task, modules=modules)

@admin_bp.route('/delete-task', methods=['POST'])
def delete_task():
    task_id = request.form['task_id']
    task = Task.query.get_or_404(task_id)
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted', 'success')
    return redirect(url_for('home_bp.home'))

@admin_bp.route('/new-lesson', methods=['POST'])
def new_lesson():
    module_id = request.form['module_id']
    module = Module.query.get_or_404(module_id)
    
    lesson = Lesson(module_id=module_id)
    
    db.session.add(lesson)
    db.session.commit()
    flash('Lesson created', 'success')
    
    return redirect(url_for('admin_bp.edit_lesson', lesson_id=lesson.id))

@admin_bp.route('/lesson/<lesson_id>/edit', methods=['GET', 'POST'])
def edit_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    
    if request.method == 'POST':
        text = request.form['text']
        
        lesson.text = text
        db.session.commit()
        flash('Lesson saved', 'success')
    
    return render_template('edit_lesson.html', lesson=lesson)

@admin_bp.route('/delete-lesson', methods=['POST'])
def delete_lesson():
    lesson_id = request.form['lesson_id']
    lesson = Lesson.query.get_or_404(lesson_id)
    
    db.session.delete(lesson)
    db.session.commit()
    
    flash('Lesson deleted', 'success')
    return redirect(url_for('home_bp.home'))
