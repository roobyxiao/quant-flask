from flask import Flask

import baostock as bs
import pandas as pd
import json

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/calendar', methods = ["GET", "POST"])
def calender():
    bs.login()
    data_list = []
    rs = bs.query_trade_dates(start_date="2018-01-01")
    result_json = {'error_code': rs.error_code, 'data': []}
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    bs.logout()
    return result_json['data'].append(result.to_dict(orient='index'))

if __name__ == '__main__':
    app.run()
