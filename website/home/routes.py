from flask import Blueprint, render_template
from website.model import Task, Module

home_bp = Blueprint(
    'home_bp', __name__, template_folder='templates', static_folder='static'
)

@home_bp.route('/')
def home():
    modules = Module.query.order_by(Module.number).all()
    return render_template('home.html', modules=modules)
