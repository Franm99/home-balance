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
plt.rcParams["font.family"] = "Gadugi"

bp = Blueprint('graphics', __name__, url_prefix='/graphics')


@bp.route('/')
def graphics():
    graphics_dict = compute_graphics()
    savings = compute_savings()
    return render_template('graphics.html', graphics=graphics_dict, savings=savings)


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
                expenses_by_tag_and_month[month_int][expense.tag.capitalize()] = expense.amount
            else:
                expenses_by_tag_and_month[month_int][expense.tag.capitalize()] += expense.amount

    return expenses_by_tag_and_month


def get_expenses_by_tag_graph():
    expenses_by_tag_and_month = get_expenses_by_tag_and_month()
    figs = dict()

    for month, expenses in expenses_by_tag_and_month.items():
        fig, ax = plt.subplots()
        ax.barh(expenses.keys(), expenses.values(), height=0.75, color="#DD7373")
        fig.set_figwidth(8)
        fig.set_figheight(5)
        ax.set_xlim(0, 1000)
        ax.set_facecolor("white")
        _, x_max = plt.xlim()
        plt.xlim(0, x_max + 10)
        for idx, amount in enumerate(expenses.values()):
            ax.text(amount + 20, idx, str(amount), ha='left', va='center')
        buf = BytesIO()
        plt.savefig(buf, format="png", transparent=True)
        figs[month] = base64.b64encode(buf.getbuffer()).decode("ascii")
        buf.close()
        plt.close()
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
    return {"Gasto": total_expense, "Ingreso": total_income}


def get_income_expense_graphics():
    records_list = [r for r, in db.session.execute(db.select(RecordsModel).order_by(RecordsModel.date.desc()))]
    records_by_month = group_records_by_month(records_list)
    totals_by_month = {calendar.month_name[month]: get_totals_by_month(month) for month in records_by_month}

    figs = dict()
    for month, totals in totals_by_month.items():
        fig, ax = plt.subplots()
        vals_fran = totals["Gasto"]["FRAN"], totals["Ingreso"]["FRAN"]
        vals_paula = totals["Gasto"]["PAULA"], totals["Ingreso"]["PAULA"]
        pos = [0.6, 1]
        ax.bar(pos, vals_fran, label="Fran", width=0.3, color="#3423A6")
        ax.bar(pos, vals_paula, bottom=vals_fran, label="Paula", width=0.3, color="#4DAA57")
        ax.set_xticks(pos, list(totals.keys()))
        ax.set_facecolor("white")
        fig.set_figwidth(4)
        fig.set_figheight(5)
        for bar in ax.patches:
            ax.text(bar.get_x() + bar.get_width() / 2.0,
                    bar.get_height() / 2.0 + bar.get_y(),
                    round(bar.get_height(), 2), ha="center",
                    color="w", weight="bold", size=10)
        ax.legend()

        buf = BytesIO()
        plt.savefig(buf, format="png", transparent=True)
        figs[month] = base64.b64encode(buf.getbuffer()).decode("ascii")
        buf.close()
        plt.close()
    return figs


def compute_savings():
    savings_by_month = dict()
    records_list = [r for r, in db.session.execute(db.select(RecordsModel).order_by(RecordsModel.date.desc()))]
    records_by_month = group_records_by_month(records_list)
    for month in records_by_month:
        total_expense = sum(r.amount for r in records_by_month[month] if r.is_expense)
        total_income = sum(r.amount for r in records_by_month[month] if not r.is_expense)
        savings = total_income - total_expense
        savings_pctg = savings / (total_expense + total_income)
        savings_by_month[calendar.month_name[month]] = str(round(savings, 2)), str(round(savings_pctg * 100, 2))
    return savings_by_month
