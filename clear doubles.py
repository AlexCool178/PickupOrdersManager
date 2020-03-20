import os
import cx_Oracle

os.environ["NLS_LANG"] = "AMERICAN.AL32UTF8"

db = 'wms/oracle@192.168.40.20/wmsdb'


def build_order_details_query(order):
    return f'SELECT vona.NAME_CONT, vona.NAME_LOC, vona.SKU_CODE, ' \
        f'vona.SKU_NAME, vona.LOAD_QTY, vona.SKU_MULTIPLICITY ' \
        f'FROM V_OP_NOW_ATK vona WHERE vona.ORDER_SDID = \'{order}\' ' \
        f'ORDER BY 1'


def get_data(order):
    with cx_Oracle.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute(build_order_details_query(order))
        res = [rec for rec in cursor.fetchall()]
    print(res)
    for row in res:
        list(row)
    print(res)


get_data('20М034880998')
