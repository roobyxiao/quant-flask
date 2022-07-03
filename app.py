from flask import Flask, request

import baostock as bs
import pandas as pd
import tushare as ts
import datetime

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/calendar', methods=["GET", "POST"])
def calender():
    bs.login()
    if request.method == "POST":
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
    else:
        start_date = request.args.get("start_date")
        end_date = request.form.get("end_date")
    data_list = []
    rs = bs.query_trade_dates(start_date, end_date)
    result_json = {'error_code': rs.error_code, 'data': []}
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    bs.logout()
    result_json['data'] = result.to_dict(orient='records')
    return result_json


@app.route('/stock', methods=["GET", "POST"])
def stock():
    bs.login()
    data_list = []
    rs = bs.query_stock_basic()
    result_json = {'error_code': rs.error_code, 'data': []}
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    bs.logout()
    result_json['data'] = result.to_dict(orient='records')
    return result_json

@app.route('/ts_stock', methods=["GET", "POST"])
def ts_stock():
    pro = ts.pro_api()
    df = pro.stock_basic(exchange='', list_status='', fields='ts_code,market')
    result_json = {'error_code': 0, 'data': []}
    result_json['data'] = df.to_dict(orient='records')
    return result_json

@app.route('/daily', methods=["GET", "POST"])
def daily():
    bs.login()
    if request.method == "POST":
        code = request.form.get("code")
        start_date = request.form.get("start_date")
    else:
        code = request.args.get("code")
        start_date = request.form.get("start_date")
    data_list = []
    rs = bs.query_history_k_data_plus(code,
                                      "date,code,open,high,low,close,preclose,volume,amount,turn,tradestatus,pctChg,isST",
                                      start_date,
                                      frequency="d", adjustflag="3")
    result_json = {'error_code': rs.error_code, 'data': []}
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    bs.logout()
    result_json['data'] = result.to_dict(orient='records')
    return result_json


@app.route('/limit', methods=["GET", "POST"])
def limit():
    pro = ts.pro_api()
    if request.method == "POST":
        trade_date = request.form.get("trade_date")
        ts_code = request.form.get("ts_code")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
    else:
        trade_date = request.args.get("trade_date")
        ts_code = request.args.get("ts_code")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
    if trade_date is not None:
        trade_time = datetime.datetime.strptime(trade_date, '%Y-%m-%d')
        trade_date = trade_time.strftime('%Y%m%d')
        df = pro.stk_limit(trade_date=trade_date)
    else:
        start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        start_date = start_time.strftime('%Y%m%d')
        end_date = end_time.strftime('%Y%m%d')
        df = pro.stk_limit(ts_code=ts_code, start_date=start_date, end_date=end_date)
    result_json = {'error_code': 0, 'data': []}
    result_json['data'] = df.to_dict(orient='records')
    return result_json

if __name__ == '__main__':
    ts.set_token('76b081c2a64f4f213a2bbe0f15ad6966fe49ebea1237b1ac607f4ef5')
    app.run()
