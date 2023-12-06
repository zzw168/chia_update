import sys
import time
import datetime
from gevent import pywsgi

import requests
import pymysql
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from flask import Flask, request, json  # 路由挂载包

import danz_stats_ui

# host = '127.0.0.1'
host = '45.195.198.171'
user = 'danzhu'
password = 'KEm6kyfSjCGkbMGw'
database = 'danzhu'

# pip install -U --pre setuptools
http = Flask(__name__)  # 路由变量


# http = Flask(__name__, instance_relative_config=True)
# http.config.from_object('http.ini')


@http.route('/db_data', methods=['POST', 'GET'])  # 排名接口
def db_data():
    No_msg = []
    bs_msg = []
    sd_msg = []
    if request.method == "POST":
        my_json = request.get_json()
        # message = request.get_data()
        print(my_json)
        if my_json:
            game_hall_id = my_json['game_hall_id']
        else:
            return 'Please enter the room number !'
    else:
        game_hall_id = 2
    try:
        if not db_message or db_message == '':
            return '数据库出错'
        for i in range(0, len(db_message)):
            if game_hall_id == db_message[i][6]:
                if db_message[i][2]:
                    s = db_message[i][2]
                    num_list = s.split(',')
                    print(num_list)
                    for j in range(0, len(num_list)):
                        if len(No_msg) < len(num_list):
                            No_msg.append({'hall_id': game_hall_id,
                                           'rank': '%s' % str(j + 1),
                                           'result': '0',
                                           'nums': 0,
                                           })
                        if No_msg[j]['result'] == str(num_list[j]):  # 如果已经赋值，则对比，相同则累加
                            No_msg[j]['nums'] = No_msg[j]['nums'] + 1
                        else:
                            No_msg[j]['result'] = str(num_list[j])
                            No_msg[j]['nums'] = 1

                        if num_list[j].isdigit():
                            if len(bs_msg) < len(num_list):
                                bs_msg.append({'hall_id': game_hall_id,
                                               'rank': '%s' % str(j + 1),
                                               'result': '0',
                                               'nums': 0,
                                               })
                            if (bs_msg[j]['result'] == 'Small' and int(num_list[j]) <= 3) or (
                                    bs_msg[j]['result'] == 'Big' and int(num_list[j]) > 3):  # 如果已经赋值，则对比，相同则累加
                                bs_msg[j]['nums'] = bs_msg[j]['nums'] + 1
                            else:
                                if int(num_list[j]) <= 3:
                                    bs_msg[j]['result'] = str('Small')
                                else:
                                    bs_msg[j]['result'] = str('Big')
                                bs_msg[j]['nums'] = 1

                            if len(sd_msg) < len(num_list):
                                sd_msg.append({'hall_id': game_hall_id,
                                               'rank': '%s' % str(j + 1),
                                               'result': '0',
                                               'nums': 0,
                                               })
                            if (sd_msg[j]['result'] == 'Single' and int(num_list[j]) % 2 == 1) or (
                                    sd_msg[j]['result'] == 'Double' and int(num_list[j]) % 2 == 0):  # 如果已经赋值，则对比，相同则累加
                                sd_msg[j]['nums'] = sd_msg[j]['nums'] + 1
                            else:
                                if int(num_list[j]) % 2 == 1:
                                    sd_msg[j]['result'] = str('Single')
                                else:
                                    sd_msg[j]['result'] = str('Double')
                                sd_msg[j]['nums'] = 1
    except:
        pass
    No_msg = No_msg + bs_msg + sd_msg
    for i in range(0, len(No_msg)):  # 冒泡排序
        temp = No_msg[i]
        for j in range(i, len(No_msg)):
            if No_msg[j]['nums'] > No_msg[i]['nums']:
                No_msg[i] = No_msg[j]
                No_msg[j] = temp
    print(No_msg)
    res_msg = []
    for i in range(0, len(No_msg)):
        if No_msg[i]['nums'] >= 2:
            res_msg.append(No_msg[i])
    print(res_msg)
    # ret_msg = json.dumps(ret_msg)
    # print(ret_msg, type(ret_msg))
    return res_msg


def post_json():  # 测试接收客户机数据
    userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    header = {
        # "origin": "https://passport.mafengwo.cn",
        "Referer": '127.0.0.1',
        'User-Agent': userAgent,
    }
    postData = {
        'game_hall_id': 5,
    }
    s = requests.session()
    # res = s.post(postUrl, data=postData, headers=header, timeout=5)
    res = s.post('http://127.0.0.1:1314/db_data', json=postData, headers=header)
    print(res.content)
    print(type(res.content))


class My_Gui(danz_stats_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)


def db_run(sql):  # 运行数据库操作
    try:
        db = pymysql.connect(user=user, password=password, host=host,
                             database=database)
        cur = db.cursor()
        # print(sql)

        cur.execute(sql)
        db.commit()
    except:
        db.rollback()
    finally:
        cur.close()
        db.close()


# try:
#     # 打开数据库连接
#     db = pymysql.connect(user=user, password=password, host=host,
#                          database=database)
#     # 使用 cursor() 方法创建一个游标对象 cursor
#     cursor = db.cursor()
# except:
#     print('数据库链接出错！')


def db_select(sql):  # 查询数据库操作
    try:
        # 打开数据库连接
        db = pymysql.connect(user=user, password=password, host=host,
                             database=database)
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = db.cursor()
    except:
        print('数据库链接出错！')
        results = 3
        return results
    try:
        # SQL 查询语句
        # sql = "SELECT * FROM %s WHERE ip='%s'" % ('userlist', ip)
        # print(sql)

        # 执行SQL语句
        cursor.execute(sql)

        # 获取所有记录列表
        results = cursor.fetchall()
    except:
        print('数据库出错！')
        results = 3
    finally:
        cursor.close()
        db.close()
    return results


def update_userlist():  # 主动更新用户列表数据
    global db_message
    table = 'dz_qh'
    # 获得当前时间
    now = datetime.datetime.now()
    # 转换为指定的格式:
    qh = now.strftime("%Y%m%d")
    # qh = '20230906'
    sql = 'SELECT * FROM %s WHERE qh LIKE "%s%%"' % (table, qh)
    # sql = 'SELECT * FROM %s WHERE (qh LIKE "%s%%" || qh LIKE "%s%%") ' % (table, qh1, qh)
    # sql = 'SELECT * FROM %s' % table
    db_message = db_select(sql)
    # db_message = json.dumps(db_message)
    # print(db_message, type(db_message))
    return db_message


def signal_accept_data(message_list):
    print(message_list)
    if message_list == 3:
        print('ok')
        return
    ui.textEdit_2.clear()
    for s in message_list:
        if s[2]:
            ui.textEdit_2.append(s[2])


class http_Thread(QThread):  # 接口服务
    _signal = pyqtSignal(object)  # 定义信号类型为整型

    def __init__(self):
        super(http_Thread, self).__init__()
        self.run_flg = False

    def run(self):
        # http.run('0.0.0.0')  # 启动运行端口接收服务
        server = pywsgi.WSGIServer(('0.0.0.0', 1314), http)
        server.serve_forever()


class data_Thread(QThread):  # 查询数据服务
    _signal = pyqtSignal(object)  # 定义信号类型为整型

    def __init__(self):
        super(data_Thread, self).__init__()
        self.run_flg = False

    def run(self):
        while True:
            if self.run_flg:
                message_list = update_userlist()
                self._signal.emit(message_list)  # 发射信号，把出错数据发送到列表窗口
                time.sleep(30)


def start_collectdata():
    if thread_data.run_flg == False:
        thread_data.run_flg = True
        thread_data.start()
        ui.pushButton.setText("暂停获取")
        ui.textEdit_2.append('开始获取操作。。。。。。')
    else:
        thread_data.run_flg = not (thread_data.run_flg)
        ui.pushButton.setText("启动获取")
        ui.textEdit_2.append('暂停获取。。。。。。')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = My_Gui()
    ui.setupUi(MainWindow)
    MainWindow.show()

    session = requests.session()
    global db_message
    db_message = None

    thread_data = data_Thread()  # 开启线程
    # thread_data.setDaemon(True)  # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
    thread_data._signal.connect(signal_accept_data)
    thread_data.run_flg = False

    Thread_http = http_Thread()  # 开启线程
    Thread_http._signal.connect(signal_accept_data)
    Thread_http.run_flg = False
    Thread_http.start()

    ui.pushButton.clicked.connect(start_collectdata)
    ui.pushButton_2.clicked.connect(post_json)

    sys.exit(app.exec_())
