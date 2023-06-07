from flask import Blueprint, render_template, abort, request, flash, send_file, redirect, url_for
from flask_login import current_user
from io import BytesIO
from openpyxl import Workbook

from website.model import db, User, Group, Task, Module, Submission, Testcase, Lesson
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
        if request.form['action'] == 'change_group':
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
        flash('Saved', 'success')
        
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

@admin_bp.route('/group/<group_id>', methods=['GET', 'POST'])
def group_progress(group_id):
    if request.method == 'POST':
        if request.form['action'] == 'remove_user':
            user_id = request.form['user_id']
            user = User.query.get(user_id)
            user.group_id = None
        
        db.session.commit()
        flash('Saved', 'success')
        
    group = Group.query.get_or_404(group_id)
    tasks = Task.query.all()
    modules = Module.query.all()
    correct_tasks = {}
    tasks_with_submissions = {}
    for user in group.users:
        correct_tasks[user.id] = db.session.query(Task) \
                                            .join(Submission) \
                                            .filter(Submission.user_id == user.id,
                                                    Submission.overall_verdict == Verdict.AC) \
                                            .distinct()
        tasks_with_submissions[user.id] = db.session.query(Task) \
                                                    .join(Submission) \
                                                    .filter(Task.submissions,
                                                            Submission.user_id == user.id) \
                                                    .distinct()
    verdict_map = {v.name: v.value for v in Verdict}
    verdict_map['AC'] = 'Correct'

    return render_template(
        'group_progress.html',
        group=group,
        tasks=tasks,
        modules=modules,
        correct_tasks=correct_tasks,
        tasks_with_submissions=tasks_with_submissions,
        verdict_map=verdict_map
    )

@admin_bp.route('/new-module', methods=['POST'])
def new_module():
    module_number = request.form['module_number']
    module_name = request.form['module_name']
    
    module = Module(
        number=module_number,
        name=module_name
    )
    
    db.session.add(module)
    db.session.commit()
    flash('Saved', 'success')
    return redirect(url_for('home_bp.home'))

@admin_bp.route('/edit-module', methods=['POST'])
def edit_module():
    module_id = request.form['module_id']
    module_number = request.form['module_number']
    module_name = request.form['module_name']
    
    module = Module.query.get_or_404(module_id)
    module.number = module_number
    module.name = module_name

    db.session.commit()
    flash('Saved', 'success')
    return redirect(url_for('home_bp.home'))

@admin_bp.route('/delete-module', methods=['POST'])
def delete_module():
    module_id = request.form['module_id']
    module = Module.query.get_or_404(module_id)
    
    db.session.delete(module)
    db.session.commit()
    
    flash('Saved', 'success')
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
    flash('Saved', 'success')
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
                raw_answer_keywords = request.form[k.replace('input', 'answer')].strip().split('\n')
                answer_keywords = [x.strip() for x in raw_answer_keywords]
                task.testcases.append(Testcase(
                    input=v,
                    answer_keywords=answer_keywords
                ))
        
        db.session.commit()
        flash('Saved', 'success')
        
    modules = Module.query.all()
    return render_template('edit_task.html', task=task, modules=modules)

@admin_bp.route('/delete-task', methods=['POST'])
def delete_task():
    task_id = request.form['task_id']
    task = Task.query.get_or_404(task_id)
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Saved', 'success')
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
