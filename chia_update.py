import os
import sys
import requests
import yaml
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QAbstractItemView, QCheckBox, QMenu

from chia_update_UI import Ui_MainWindow


class MyUi(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

    def setupUi(self, MainWindow):
        super(MyUi, self).setupUi(MainWindow)

        tb = self.tableWidget
        tb.horizontalHeader().resizeSection(0, 10)
        tb.horizontalHeader().resizeSection(1, 150)
        tb.horizontalHeader().setStyleSheet("QHeaderView::section{background:rgb(245,245,245);}")
        tb.verticalHeader().setStyleSheet("QHeaderView::section{background:rgb(245,245,245);}")
        # tb.clicked.connect(table_clicked)

        tb.setContextMenuPolicy(Qt.CustomContextMenu)
        tb.customContextMenuRequested.connect(self.generateMenu)

    def generateMenu(self, pos):
        tb = self.tableWidget

        menu = QMenu()
        item1 = menu.addAction("刷新")
        item2 = menu.addAction("删除")
        screenPos = tb.mapToGlobal(pos)

        action = menu.exec(screenPos)
        if action == item1:
            deal_yaml()
        if action == item2:
            # del_host()
            num = tb.rowCount()
            if num != 0:
                p = tb.currentRow()
                for i in range(p, num - 1):
                    # print('%d' % i)
                    for j in range(1, tb.columnCount()):
                        print("%d %d" % (i, j))
                        # print(tb.item(i, j).text())
                        item = QTableWidgetItem(tb.item(i + 1, j).text())
                        item.setTextAlignment(Qt.AlignCenter)
                        tb.setItem(i, j, item)
                tb.setRowCount(num - 1)


class UpdateThead(QThread):
    _signal = pyqtSignal(object)

    def __init__(self):
        super(UpdateThead, self).__init__()

    def run(self) -> None:
        global host_list
        print(host_list)

        for url in host_list:
            try:
                url = "http://%s/upgrade" % url[0]
                print(url)
                # url = "http://192.168.0.73:5000/"
                res = requests.get(url)
                print(res.content.decode('utf-8'))
                self._signal.emit("%s %s" % (url, res.content.decode('utf-8')))
            except:
                print("网络错误")
                self._signal.emit("%s 网络错误" % url)


def signal_accept(message):
    print(message)
    ui.textBrowser.append(message)


def start_update():
    ui.textBrowser.setText('')
    update_Thead.start()


def deal_yaml():
    global host_list
    file = "./prometheus.yml"
    if os.path.exists(file):
        f = open(file, 'r', encoding='utf-8')
        f_ = yaml.safe_load(f)
        f_ = f_['scrape_configs'][1]['static_configs']
        print(f_[0]['targets'])
        print(type(f_[0]['targets']))
        table = ui.tableWidget
        num = 0
        for host in f_:
            # print("%s %s" % (host['targets'][0], host['labels']['host']))
            local_list = [host['targets'][0], host['labels']['host']]
            host_list.append(local_list)

            table.setRowCount(num + 1)
            cb = QCheckBox()
            cb.setStyleSheet('QCheckBox{margin:6px};')
            table.setCellWidget(num, 0, cb)

            item = QTableWidgetItem(str(host['targets'][0]))
            item.setTextAlignment(Qt.AlignCenter)
            # item.setFlags(QtCore.Qt.ItemFlag(63))   # 单元格可编辑
            table.setItem(num, 1, item)

            item = QTableWidgetItem(str(host['labels']['host']))
            item.setTextAlignment(Qt.AlignCenter)
            # item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            table.setItem(num, 2, item)

            num += 1
        f.close()
    else:
        print("文件不存在")


def table_clicked():
    table = ui.tableWidget
    num = table.currentRow()
    print(table.item(num, 1).text())


def add_host():
    table = ui.tableWidget
    num = table.rowCount()
    table.setRowCount(num + 1)
    cb = QCheckBox()
    cb.setStyleSheet('QCheckBox{margin:6px};')
    table.setCellWidget(num, 0, cb)

    item = QTableWidgetItem('')
    item.setTextAlignment(Qt.AlignCenter)
    # item.setFlags(QtCore.Qt.ItemFlag(63))   # 单元格可编辑
    table.setItem(num, 1, item)

    item = QTableWidgetItem('')
    item.setTextAlignment(Qt.AlignCenter)
    # item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
    table.setItem(num, 2, item)


def save_host():
    global host_list
    table = ui.tableWidget
    num = table.rowCount()
    if num == 0:
        return
    host_list = []
    host_l = []
    for i in range(0, num):
        host = [table.item(i, 1).text(), table.item(i, 2).text()]
        host_list.append(host)

        h = {'targets': [table.item(i, 1).text()], 'labels': {'host': table.item(i, 2).text()}}
        host_l.append(h)
    print(host_list)

    file = "./prometheus.yml"
    if os.path.exists(file):
        f = open(file, 'r', encoding='utf-8')
        chia_conf = yaml.safe_load(f)
        f.close()

        chia_conf['scrape_configs'][1]['static_configs'] = host_l
        print(chia_conf)

        with open(file, "w", encoding="utf-8") as f:
            yaml.dump(chia_conf, f, allow_unicode=True)
            ui.textBrowser.setText("保存服务器完成")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = MyUi()
    ui.setupUi(MainWindow)
    MainWindow.show()

    global host_list
    host_list = []

    deal_yaml()

    update_Thead = UpdateThead()
    update_Thead._signal.connect(signal_accept)

    ui.pushButton_update.clicked.connect(start_update)
    ui.pushButton_add.clicked.connect(add_host)
    ui.pushButton_save.clicked.connect(save_host)

    sys.exit(app.exec_())
