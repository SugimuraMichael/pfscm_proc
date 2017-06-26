


import pandas as pd
import numpy as np
import datetime
from collections import defaultdict
import time
from datetime import datetime, timedelta
from workdays import networkdays
import time
'''




'''

#matrix_file = 'PAD COR 5_23_17.csv'

#save_loc = 'C:/Users/585000/Desktop/PCFSM/monthly reporting files/LSU/'

#matrix_file2 = matrix_file[:-4]
#save_name = matrix_file2+'_VIFD_report.xlsx'
#matrix_file = 'PAD COR 5_23_17.csv'

#dat2 = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/'+matrix_file, encoding = 'latin-1')
####################### FOR Vendor Promised Date Comparison
def vipd_checks_vs_po_create(dat2,DATE_TO_COMPARE,save_loc='',save_name=''):
    DATE_TO_COMPARE = DATE_TO_COMPARE#'05/24/2017'
    #one_week = one_week
    #one_week = one_week.lower()
    N = 3
    comp_day = datetime.strptime(DATE_TO_COMPARE, "%m/%d/%Y").date()
    #if one_week == 'yes':
    #    N = 7

    #date_N_days_ago = comp_day - timedelta(days=N)

    # switched PE and PO to use days_between function rather than business days:
    def business_days_between(d1, d2):
        d1 = datetime.strptime(d1, "%m/%d/%Y")
        d2 = datetime.strptime(d2, "%m/%d/%Y")
        return networkdays(d1, d2)

    ##########################################################

    dat2['Ta0'] = 0
    for index, row in dat2.iterrows():
        a = str(row['Project Code'])
        a = a[-3:]
        if a == 'TA0':
            dat2.loc[index, 'Ta0'] = 1

    dat2 = dat2[dat2['Ta0'] == 0]

    ## NEED TO FIX
    dat2 = dat2[dat2['Client Type'] != 'NGF']

    dat2 = dat2[dat2['Managed By - Project']!= 'SCMS']
    dat2 = dat2[dat2['Order Short Closed'] != "Yes"]

    #dat2 = dat2[dat2['PO_CREATE_DATE']==2017]
    dat2['Vendor INCO Fulfillment Date'] = dat2['Vendor INCO Fulfillment Date'].fillna('')
    dat2['Order Created Date'] = dat2['Order Created Date'].fillna('')

    dat2['PO_create_check'] = 0
    dat2['comments'] = ''

    for index, row in dat2.iterrows():
        export =str(row['Vendor INCO Fulfillment Date'])

        po_create = str(row['Order Created Date'])
        if export != '':
            x = business_days_between(export,DATE_TO_COMPARE)

            if x > N:
                if po_create == '':

                    dat2.loc[index, 'PO_create_check'] = 1


    dat2 = dat2[dat2['PO_create_check']==1]

    #dat2.drop(['slicer','Ta0'], axis=1, inplace=True)

    PO_cols = ['Grant#',
     'PE#',
     'PQ#',
     'Order#',
    'Shipment#',
     'Order Type',
     'Order Short Closed',
     'Order Point of Contact',
     'PQ Buyer',
     'PQ Product Group',
     'Managed By',
     'PR Received Date',
     'PE Create Date',
     'PE Actionable Date',
     'PE Sent Date',
     'PE Response Date',
     'PE Proceed To PQ Date',
     'PQ Create Date',
     'PQ Actionable Date',
     'PQ Proceed To PO/SO Date',
     'Order Created Date',
     'PO Sent to Vendor Date',
     'PO Vendor Confirmed Date',
     'Vendor Promised Date',
    'Vendor INCO Fulfillment Date',
     'Current Shipment Milestone',
     'comments']

    dat2 = dat2[PO_cols]

    writer = pd.ExcelWriter(save_loc + save_name)

    readme = pd.read_csv('C:/Users/585000/Desktop/PCFSM/monthly reporting files/VIFD_PO_Create_readme.csv')

    readme.to_excel(writer, 'Readme', index=False)
    dat2.to_excel(writer, 'Order Create Check', index=False)

