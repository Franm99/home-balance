from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request
from .db import db, RecordsModel

bp = Blueprint('records', 'records', '/')


@bp.route('/')
def view_records():
    records_table = db.session.execute(db.select(RecordsModel).order_by(RecordsModel.date.desc()))
    return render_template(
        'records.html',
        records_list=[r for r, in records_table]
    )


@bp.route('/add_record', methods=["GET", "POST"])
def add_record():
    if request.method == "POST":
        date_ = datetime.strptime(request.form['from_date'], "%Y-%m-%d").date()
        is_expense = request.form.get('is_expense', "True") == "True"

        record = RecordsModel(
            date=date_,
            is_expense=is_expense,
            amount=request.form["amount"],
            reporter=request.form["reporter"],
            tag=request.form["tag"],
            description=request.form["description"]
        )

        db.session.add(record)
        db.session.commit()
        return redirect(url_for('records.view_records'))
    return render_template('add_record.html')


@bp.route("/remove_record/<int:record_id>", methods=["GET"])
def remove_record(record_id):
    db.session.execute(db.delete(RecordsModel).where(RecordsModel.id == record_id))
    db.session.commit()
    return redirect(url_for('records.view_records'))

#
# @bp.route("/update_record/<int:record_id>", methods=["GET"])
# def update_record(record_id):
    record = db.session.execute(db.select(RecordsModel).where(RecordsModel.id == record_id))




