import pandas as pd

##dat['UOM2'] = dat['Item UOM'].str.replace('TEST', '')
def replace_SCMS(dat):
    col_list = list(dat.columns)
    if 'Order#' in col_list:
        order_col = "Order#"
    if 'ORDER_NO' in col_list:
        order_col = 'ORDER_NO'

    dat[order_col] = dat[order_col].str.replace('SCMS', 'PO')
    #dat[order_col] = dat[order_col].str.replace('SO', 'PO')
    #dat[order_col] = dat[order_col].str.replace('DSCM', 'PO')
    #dat[order_col] = dat[order_col].str.replace('DPO', 'PO')

    return dat
