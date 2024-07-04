from flask import Blueprint, render_template
from itertools import groupby
from .db import db, RecordsModel
import calendar
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
import sqlalchemy
matplotlib.use('Agg')

bp = Blueprint('graphics', __name__, url_prefix='/graphics')


@bp.route('/')
def graphics():
    records_list = [r for r, in db.session.execute(db.select(RecordsModel).order_by(RecordsModel.date.desc()))]
    records_by_month = group_records_by_month(records_list)
    totals_by_month = {calendar.month_name[month]: get_totals_by_month(month) for month in records_by_month}
    income_expense_graphics = get_income_expense_graphics(totals_by_month)
    return render_template('graphics.html', income_expense_graphics=income_expense_graphics)


def group_records_by_month(records_list: list):

    records_by_month = dict()
    for (month, items) in groupby(records_list, lambda x: x.date.month):
        records_by_month[month] = list(items)
    # calendar.month_name[name] to get month name from integer
    return records_by_month


def get_totals_by_month(month: int):
    records_expense_fran = [r for r, in db.session.execute(db.select(RecordsModel).filter(
        sqlalchemy.extract('month', RecordsModel.date) == month,
        RecordsModel.is_expense == True,
        RecordsModel.reporter == "FRAN"
    ))]
    records_expense_paula = [r for r, in db.session.execute(db.select(RecordsModel).filter(
        sqlalchemy.extract('month', RecordsModel.date) == month,
        RecordsModel.is_expense == True,
        RecordsModel.reporter == "PAULA"
    ))]
    records_income_fran = [r for r, in db.session.execute(db.select(RecordsModel).filter(
        sqlalchemy.extract('month', RecordsModel.date) == month,
        RecordsModel.is_expense == False,
        RecordsModel.reporter == "FRAN"
    ))]
    records_income_paula = [r for r, in db.session.execute(db.select(RecordsModel).filter(
        sqlalchemy.extract('month', RecordsModel.date) == month,
        RecordsModel.is_expense == False,
        RecordsModel.reporter == "PAULA"
    ))]

    total_expense = {
        "FRAN": sum(rec.amount for rec in records_expense_fran),
        "PAULA": sum(rec.amount for rec in records_expense_paula)
    }
    total_income = {
        "FRAN": sum(rec.amount for rec in records_income_fran),
        "PAULA": sum(rec.amount for rec in records_income_paula)
    }
    return {"E": total_expense, "I": total_income}


def get_income_expense_graphics(totals_by_month):
    figs = dict()
    for month, totals in totals_by_month.items():
        fig, ax = plt.subplots()
        fig.suptitle(month)
        vals_fran = totals["E"]["FRAN"], totals["I"]["FRAN"]
        vals_paula = totals["E"]["PAULA"], totals["I"]["PAULA"]
        ax.bar(list(totals.keys()), vals_fran, label="Fran")
        ax.bar(list(totals.keys()), vals_paula, bottom=vals_fran, label="Paula")
        buf = BytesIO()
        plt.savefig(buf, format="png")
        figs[month] = base64.b64encode(buf.getbuffer()).decode("ascii")
        buf.close()
    return figs



# def sample_figures():
#     fig1, fig2 = plt.figure(1), plt.figure(2)
#     fig1.subplots(1,2), fig2.subplots(3, 1)
#     buf1, buf2 = BytesIO(), BytesIO()
#     fig1.savefig(buf1, format="png")
#     fig2.savefig(buf2, format="png")
#     fig_html1 = base64.b64encode(buf1.getvalue()).decode("ascii")
#     fig_html2 = base64.b64encode(buf2.getvalue()).decode("ascii")



