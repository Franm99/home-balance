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
    graphics_dict = compute_graphics()
    return render_template('graphics.html', graphics=graphics_dict)


def group_records_by_month(records_list: list):
    records_by_month = dict()
    for (month, items) in groupby(records_list, lambda x: x.date.month):
        records_by_month[month] = list(items)
    # calendar.month_name[name] to get month name from integer
    return records_by_month


def get_total_by_month(month: int, is_expense: bool, reporter: str):
    return [r for r, in db.session.execute(db.select(RecordsModel).filter(
        sqlalchemy.extract('month', RecordsModel.date) == month,
        RecordsModel.is_expense == is_expense,
        RecordsModel.reporter == reporter
    ))]


def get_expenses_by_tag_and_month():
    expenses_records = [r for r, in db.session.execute(
        db.select(RecordsModel).filter(
            RecordsModel.is_expense == True
        ).order_by(
            RecordsModel.date.desc()
        )
    )]

    expenses_by_tag_and_month = dict()
    for (month, expenses) in groupby(expenses_records, lambda x: x.date.month):
        month_int = calendar.month_name[month]
        expenses_by_tag_and_month[month_int] = dict()
        for expense in expenses:
            if expense.tag not in expenses_by_tag_and_month[month_int]:
                expenses_by_tag_and_month[month_int][expense.tag] = expense.amount
            else:
                expenses_by_tag_and_month[month_int][expense.tag] += expense.amount

    return expenses_by_tag_and_month


def get_expenses_by_tag_graph():
    expenses_by_tag_and_month = get_expenses_by_tag_and_month()
    figs = dict()

    for month, expenses in expenses_by_tag_and_month.items():
        fig, ax = plt.subplots()
        ax.barh(expenses.keys(), expenses.values(), height=0.75, color="red")
        _, x_max = plt.xlim()
        plt.xlim(0, x_max + 10)
        for idx, amount in enumerate(expenses.values()):
            ax.text(amount + 100, idx, str(amount), ha='left', va='center')
        buf = BytesIO()
        plt.savefig(buf, format="png")
        figs[month] = base64.b64encode(buf.getbuffer()).decode("ascii")
        buf.close()
    return figs


def compute_graphics():
    income_expense_graphics = get_income_expense_graphics()
    expense_by_tag_graphics = get_expenses_by_tag_graph()
    graphics = dict()
    for month in income_expense_graphics:
        graphics[month] = income_expense_graphics[month], expense_by_tag_graphics[month]
    return graphics

def get_totals_by_month(month: int):
    records_expense_fran = get_total_by_month(month, True, "FRAN")
    records_expense_paula = get_total_by_month(month, True, "PAULA")
    records_income_fran = get_total_by_month(month, False, "FRAN")
    records_income_paula = get_total_by_month(month, False, "PAULA")

    total_expense = {
        "FRAN": sum(rec.amount for rec in records_expense_fran),
        "PAULA": sum(rec.amount for rec in records_expense_paula)
    }
    total_income = {
        "FRAN": sum(rec.amount for rec in records_income_fran),
        "PAULA": sum(rec.amount for rec in records_income_paula)
    }
    return {"E": total_expense, "I": total_income}


def get_income_expense_graphics():
    records_list = [r for r, in db.session.execute(db.select(RecordsModel).order_by(RecordsModel.date.desc()))]
    records_by_month = group_records_by_month(records_list)
    totals_by_month = {calendar.month_name[month]: get_totals_by_month(month) for month in records_by_month}

    figs = dict()
    for month, totals in totals_by_month.items():
        fig, ax = plt.subplots()
        vals_fran = totals["E"]["FRAN"], totals["I"]["FRAN"]
        vals_paula = totals["E"]["PAULA"], totals["I"]["PAULA"]
        ax.bar(list(totals.keys()), vals_fran, label="Fran")
        ax.bar(list(totals.keys()), vals_paula, bottom=vals_fran, label="Paula")
        for bar in ax.patches:
            ax.text(bar.get_x() + bar.get_width() / 2.0,
                    bar.get_height() / 2.0 + bar.get_y(),
                    bar.get_height(), ha="center",
                    color="w", weight="bold", size=10)
        ax.legend()

        buf = BytesIO()
        plt.savefig(buf, format="png")
        figs[month] = base64.b64encode(buf.getbuffer()).decode("ascii")
        buf.close()
    return figs


def get_all_tags_in_month(month: int):
    return [r for r, in db.session.execute(db.select(RecordsModel).where(RecordsModel))]


def get_total_by_tag(month: int, tag: str):
    return [r for r, in db.session.execute(db.select(RecordsModel).filter(

    ))]