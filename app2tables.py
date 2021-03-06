import os
import sys
import gui2
import cx_Oracle

os.environ["NLS_LANG"] = "AMERICAN.AL32UTF8"

db = 'wms/oracle@192.168.40.20/wmsdb'


class MyException(cx_Oracle.Error):
    pass


def build_orders_query(client):
    return f'SELECT ORDER_SDID, ORDER_STATUS, ORDER_CREATED FROM V_OP_NOW_ATK ' \
        f'WHERE CLIENT_CODE = \'{client}\' ' \
        f'GROUP BY ORDER_SDID, ORDER_STATUS, ORDER_CREATED ' \
        f'ORDER BY 3'


def build_client_check_query(client):
    return f'SELECT ID FROM CLIENT WHERE DESCRIPTION = \'{client}\''


def build_check_data_query(client):
    return f'SELECT 1 FROM V_OP_NOW_ATK WHERE CLIENT_CODE = \'{client}\''


def build_order_details_query(order):
    return f'SELECT vona.NAME_CONT, vona.NAME_LOC, vona.SKU_CODE, ' \
        f'vona.SKU_NAME, vona.LOAD_QTY, vona.SKU_MULTIPLICITY ' \
        f'FROM V_OP_NOW_ATK vona WHERE vona.ORDER_SDID = \'{order}\' ' \
        f'ORDER BY 2, 1'


def check_client_name(client):
    return len([s for s in client if not s.isdigit()]) == 0


def check_client_exists(client):
    try:
        with cx_Oracle.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute(build_client_check_query(client))
            id_list = [rec for rec in cursor.fetchall()]
        return len(id_list) > 0
    except MyException:
        ui.label_2.setText('Нет подключения к БД!')


def check_data_exists(client):
    try:
        with cx_Oracle.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute(build_check_data_query(client))
            res = [rec for rec in cursor.fetchall()]
        return len(res) > 0
    except MyException:
        ui.label_2.setText('Нет подключения к БД!')


def get_info(client):
    try:
        with cx_Oracle.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute(build_orders_query(client))
            ui.tableWidget.setRowCount(0)
            for row_number, row_data in enumerate(cursor):
                ui.tableWidget.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    ui.tableWidget.setItem(row_number, column_number, gui2.QtWidgets.QTableWidgetItem(str(data)))
    except MyException:
        ui.label_2.setText('Нет подключения к БД!')


def search_button_press():
    cancel_search()
    ui.tableWidget.setDisabled(True)
    ui.tableWidget_2.setDisabled(True)
    ui.pushButton.setDisabled(True)
    ui.label_3.setText(ui.lineEdit.text())
    client = ui.label_3.text()
    if len(client) == 0:
        ui.label_2.setText('')
        ui.label_3.setText('Номер клиента не может быть пустым!')
        cancel_search()
    else:
        if check_client_name(client):
            if check_client_exists(client):
                if check_data_exists(client):
                    ui.tableWidget.setDisabled(False)
                    get_info(client)
                    ui.label_2.setText('Список заказов по клиенту')
                    ui.tableWidget.setHorizontalHeaderLabels(['Заказ №', 'Статус', 'Дата создания'])
                    ui.tableWidget.horizontalHeader().show()
                    ui.pushButton_2.setDisabled(False)
                    ui.pushButton_3.setDisabled(False)
                else:
                    ui.label_3.setText('Нет заказов по клиенту')
                    cancel_search()
            else:
                ui.label_3.setText('Неверный номер клиента')
                cancel_search()
        else:
            ui.label_3.setText('Введены недопустимые символы')
            cancel_search()
    ui.pushButton.setDisabled(False)


def load_selected_order_info():
    ui.tableWidget_2.clear()
    row = ui.tableWidget.currentRow()
    order = ui.tableWidget.item(row, 0).text()
    ui.label_4.setText(f'Информация по заказу {order}')
    ui.tableWidget_2.setHorizontalHeaderLabels(['Контейнер', 'В ячейке', 'Артикул',
                                                'Наименование', 'Количество', 'Кратность'])
    ui.tableWidget_2.horizontalHeader().show()
    with cx_Oracle.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute(build_order_details_query(order))
        ui.tableWidget_2.setRowCount(0)
        for row_number, row_data in enumerate(cursor):
            ui.tableWidget_2.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                ui.tableWidget_2.setItem(row_number, column_number, gui2.QtWidgets.QTableWidgetItem(str(data)))
    clear_double_recs()
    ui.tableWidget_2.setDisabled(False)
    ui.tableWidget_2.resizeColumnsToContents()
    if ui.tableWidget_2.item(0, 0).text() == 'None':
        ui.tableWidget_2.clear()
        ui.tableWidget_2.setDisabled(True)
        ui.tableWidget_2.horizontalHeader().hide()
        ui.tableWidget_2.setRowCount(0)
        ui.label_4.setText(f'Заказ {order} еще в работе')


def clear_double_recs():
    if ui.tableWidget_2.columnCount() > 1:
        old_cnt_col = [ui.tableWidget_2.item(row, 0).text() for row in range(ui.tableWidget_2.rowCount())]
        old_loc_col = [ui.tableWidget_2.item(row, 1).text() for row in range(ui.tableWidget_2.rowCount())]
        new_cnt_col = []
        pre = None
        for s in old_cnt_col:
            if s == pre:
                new_cnt_col.append('')
            else:
                new_cnt_col.append(s)
                pre = s
        new_loc_col = []
        pre = None
        for s in old_loc_col:
            if s == pre:
                new_loc_col.append('')
            else:
                new_loc_col.append(s)
                pre = s
        for row, data in enumerate(new_cnt_col):
            ui.tableWidget_2.setItem(row, 0, gui2.QtWidgets.QTableWidgetItem(str(data)))
        for row, data in enumerate(new_loc_col):
            if ui.tableWidget_2.item(row, 0).text() == '':
                ui.tableWidget_2.setItem(row, 1, gui2.QtWidgets.QTableWidgetItem(str(data)))


def refresh():
    ui.tableWidget_2.clear()
    ui.tableWidget_2.setDisabled(True)
    ui.label_4.setText('')
    ui.tableWidget_2.horizontalHeader().hide()
    ui.tableWidget_2.setRowCount(0)
    client = ui.label_3.text()
    get_info(client)


def cancel_search():
    ui.label_2.setText('')
    ui.label_4.setText('')
    ui.tableWidget.clear()
    ui.tableWidget_2.clear()
    ui.pushButton_2.setDisabled(True)
    ui.pushButton_3.setDisabled(True)
    ui.tableWidget.horizontalHeader().hide()
    ui.tableWidget_2.horizontalHeader().hide()
    ui.tableWidget.setRowCount(0)
    ui.tableWidget_2.setRowCount(0)


def clear():
    ui.lineEdit.clear()
    ui.tableWidget.clear()
    ui.tableWidget_2.clear()
    ui.label_2.setText('')
    ui.label_3.setText('')
    ui.label_4.setText('')
    ui.pushButton_2.setDisabled(True)
    ui.pushButton_3.setDisabled(True)
    ui.tableWidget.setDisabled(True)
    ui.tableWidget_2.setDisabled(True)
    ui.tableWidget.horizontalHeader().hide()
    ui.tableWidget_2.horizontalHeader().hide()
    ui.tableWidget.setRowCount(0)
    ui.tableWidget_2.setRowCount(0)


app = gui2.QtWidgets.QApplication(sys.argv)
MainWindow = gui2.QtWidgets.QMainWindow()
ui = gui2.Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()
ui.pushButton.clicked.connect(search_button_press)
ui.pushButton_2.clicked.connect(refresh)
ui.pushButton_3.clicked.connect(clear)
ui.tableWidget.cellClicked.connect(load_selected_order_info)
ui.pushButton_2.setDisabled(True)
ui.pushButton_3.setDisabled(True)
ui.tableWidget.setDisabled(True)
ui.tableWidget_2.setDisabled(True)
ui.lineEdit.returnPressed.connect(ui.pushButton.click)
sys.exit(app.exec_())
