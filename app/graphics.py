from flask import Blueprint, render_template

bp = Blueprint('graphics', __name__, url_prefix='/graphics')


@bp.route('/')
def graphics():
    return render_template('graphics.html')
