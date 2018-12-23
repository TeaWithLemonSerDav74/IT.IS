from flask import Flask, render_template, request, redirect, url_for
from db import get_db, close_db
from datetime import datetime
import os
import json

app = Flask(__name__)
#app.config["DATABASE"] = os.path.join(app.root_path, 'log_parser\database.sqlite')
app.config.from_pyfile('config.py')
app.teardown_appcontext(close_db)

@app.route("/")
@app.route("/main")
@app.route("/report/")
def app_main():
    return render_template("report_picker.html")


@app.route("/report/hits-per-country/")
def report_hits_per_country_general():
    return redirect(url_for('report_hits_per_country', limit=10))


@app.route("/report/hits-per-country/<int:limit>/")
def report_hits_per_country(limit):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM hits_per_country ORDER BY amount DESC LIMIT ?", (limit,))
    return render_template("report_template.html", report='hits-per-country', data=cursor.fetchall(), limit=limit)


@app.route("/report/unpaid-carts/", methods=['GET', 'POST'])
def report_unpaid_carts():
    if "start-date" in request.form and "end-date" in request.form:
        start_date = request.form["start-date"]
        end_date = request.form["end-date"]
        if start_date >= end_date:
            return render_template("report_template.html", report='error', message='Начальное время должно быть раньше конечного.')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM carts WHERE creation_date > ? AND creation_date < ? AND payment_date > ?",
                       (start_date, end_date, end_date))
        data = cursor.fetchone()[0]
        return render_template("report_template.html", report='unpaid-carts', data=data, start_date=start_date, end_date=end_date)
    else:
        return render_template("report_template.html", report='unpaid-carts')


@app.route("/report/load/", methods=['GET', 'POST'])
def report_load():
    if "start-date" in request.form and "end-date" in request.form:
        start_date = datetime.fromisoformat(request.form["start-date"]).replace(minute=0, second=0)
        end_date = datetime.fromisoformat(request.form["end-date"]).replace(minute=0, second=0)
        if start_date >= end_date:
            return render_template("report_template.html", report='error',
                                   message='Начальное время должно быть раньше конечного.')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM hits_per_hour WHERE ? <= time AND time < ?",
                       (start_date.isoformat(sep=' '), end_date.isoformat(sep=' ')))
        data = cursor.fetchall()
        if len(data) == 0:
            return render_template("report_template.html", report='error',
                                   message='Для указанного промежутка времени данных нет.')
        data = convert_rows_to_chartjs(data)
        return render_template("report_template.html", report='load', data=data, start_date=start_date, end_date=end_date)
    else:
        return render_template("report_template.html", report='load')


def convert_rows_to_chartjs(rows):
    chart_data = dict()

    chart_data['type'] = 'bar' if len(rows) < 72 else 'line'
    chart_data['data'] = {
        'labels': [row['time'] for row in rows],
        'datasets': [{
            'label': "Число запросов за час",
            'data': [row['amount'] for row in rows],
            'backgroundColor': 'rgba(240, 240, 240)',
            'borderColor': 'rgba(255, 255, 255)',
            'borderWidth': 1
        }]
    }
    chart_data['options'] = {
        'scales': {
            'yAxes': [{
                'ticks': {
                    'beginAtZero': True
                }
            }]
        }
    }

    #return json.dumps(chart_data)
    return chart_data