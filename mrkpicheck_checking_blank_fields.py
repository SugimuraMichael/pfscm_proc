
import pandas as pd
import numpy as np
import datetime

import time
from datetime import datetime

'''
combine the PE and PO into here
broaden the PO scopes... SO THE PO check now includes the seperate PO check that was being done in the other
Checking blanks for PE and PO dates.
'''

#doesnt change
#directory = 'C:/Users/585000/Desktop/PCFSM/2017 KPIs/supplier performance checks/'
#save_loc = directory

#doc_no = 'PPM_LI_FT P_MAR01_2017_v1.csv'
#save_name = 'supplier_checks_5_5_2017_v1.xlsx'
#matrix_file = 'PAD COR 5_01_17.csv'

#dat2 = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/'+matrix_file, encoding = 'latin-1')
####################### FOR Vendor Promised Date Comparison

##########################################################
def check_for_blanks(dat,DATE_TO_COMPARE,save_name,save_loc, period ='2017',reporting_period='2017-01'):
    DATE_TO_COMPARE = DATE_TO_COMPARE
    #                                                CHANGE THIS
    VPD_comparison_date = datetime.strptime(DATE_TO_COMPARE, "%m/%d/%Y").date()
    dat['Ta0'] = 0
    #print 'wut'
    for index, row in dat.iterrows():
        a = str(row['Project Code'])
        a = a[-3:]
        if a == 'TA0':
            dat.loc[index, 'Ta0'] = 1

    dat = dat[dat['Ta0'] == 0]

    ## NEED TO FIX
    dat = dat[dat['Client Type'] != 'NGF']

    dat = dat[dat['Managed By - Project'] != 'SCMS']
    dat = dat[dat['Order Short Closed'] != "Yes"]
    dat['comments'] = ''
    #print 'why'

    #pattern = '|'.join(years)

    #dat['PR Received Date'] = dat['PR Received Date'].fillna('')
    #dat2.shape
    #dat = dat[dat['PR Received Date'].str.contains(pattern)]
    #print dat.shape
    #print 'into abyss'

    dat['identifier'] = dat['PE#']+dat['PQ#']+dat['Order#']+dat['Shipment#']+dat['PQ Buyer'].astype(str)
    dat2 = dat.copy()

    #dat2 = dat2[dat2['PO_CREATE_DATE']==2017]
    dat2['Vendor Promised Date'] = dat2['Vendor Promised Date'].fillna('')
    dat2['Vendor INCO Fulfillment Date'] = dat2['Vendor INCO Fulfillment Date'].fillna('')
    dat2['PO Sent to Vendor Date'] = dat2['PO Sent to Vendor Date'].fillna('')
    dat2['PO Vendor Confirmed Date'] = dat2['PO Vendor Confirmed Date'].fillna('')
    dat2['Order Created Date'] = dat2['Order Created Date'].fillna('')
    dat2['PQ Actionable Date'] = dat2['PQ Actionable Date'].fillna('')

    dat2['PQ Last Client Response Date'] = dat2['PQ Last Client Response Date'].fillna('')
    dat2['PQ Proceed To PO/SO Date'] = dat2['PQ Proceed To PO/SO Date'].fillna('')
    dat2['Order Created Date'] = dat2['Order Created Date'].fillna('')
    dat2['PQ Last Client Response Date'] = dat2['PQ Last Client Response Date'].fillna('')
    dat2['PQ First Response Date'] = dat2['PQ First Response Date'].fillna('')
    dat2['PQ Create Date'] = dat2['PQ Create Date'].fillna('')
    dat2['PR Received Date'] = dat2['PR Received Date'].fillna('')
    dat2['PQ First Approved Date'] = dat2['PQ First Approved Date'].fillna('')
    dat2['PR Received Date'] = dat2['PR Received Date'].fillna('')


    dat2['id'] = dat2['PR Received Date'] + dat2['PQ Last Client Response Date'] + dat2['PQ Proceed To PO/SO Date'] + \
                 dat2['Order Created Date'] + dat2['PQ Last Client Response Date'] + dat2['PQ First Response Date'] + \
                 dat2['PQ Create Date'] + dat2['PQ First Approved Date']

    dat2 = dat2[dat2['id'].str.contains(period)==True]

    dat2['slicer_1'] = 0

    #print 'vendor and PO loop'

    for index, row in dat2.iterrows():
        vpd = str(row['Vendor Promised Date'])
        export =str(row['Vendor INCO Fulfillment Date'])
        po_conf = str(row['PO Vendor Confirmed Date'])
        po_sent = str(row['PO Sent to Vendor Date'])
        pq_action = str(row['PQ Actionable Date'])


        if vpd != '':
            vpd2 = datetime.strptime(vpd, "%m/%d/%Y").date()
        if vpd2 == 'nan':
            print vpd, type(vpd)
            dat2.loc[index, 'slicer_1'] = 1
            continue

        if vpd == '' and export != '':
            dat2.loc[index, 'slicer_1'] = 1
        if vpd2 < VPD_comparison_date:
            if export == '':
                dat2.loc[index, 'slicer_1'] = 1
        if po_sent == '' and po_conf != '':
            dat2.loc[index, 'slicer_1'] = 1


    #print 'checking to see where not applicable'

    dat2 = dat2[dat2['slicer_1']==1]
    po_list = dat2['identifier'].tolist()
    PO_cols = ['Grant#',
     'PE#',
     'PQ#',
     'Order#',
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
    print
    print 'number of POs is ' + str(dat2.shape[0])+' '+str(len(po_list))
    print
    writer = pd.ExcelWriter(save_loc + save_name)

    readme = pd.read_csv('C:/Users/585000/Desktop/PCFSM/monthly reporting files/readme_supplier_performance.csv')

    readme.to_excel(writer, 'Readme', index=False)
    dat2.to_excel(writer, 'Supplier Date Checks', index=False)

    del dat2

    dat2 = dat.copy()

    # dat2 = dat2[dat2['PO_CREATE_DATE']==2017]
    dat2['Vendor Promised Date'] = dat2['Vendor Promised Date'].fillna('')
    dat2['Vendor INCO Fulfillment Date'] = dat2['Vendor INCO Fulfillment Date'].fillna('')
    dat2['PO Sent to Vendor Date'] = dat2['PO Sent to Vendor Date'].fillna('')
    dat2['PO Vendor Confirmed Date'] = dat2['PO Vendor Confirmed Date'].fillna('')
    dat2['Order Created Date'] = dat2['Order Created Date'].fillna('')
    dat2['PQ Actionable Date'] = dat2['PQ Actionable Date'].fillna('')

    dat2['PQ Last Client Response Date'] = dat2['PQ Last Client Response Date'].fillna('')
    dat2['PQ Proceed To PO/SO Date'] = dat2['PQ Proceed To PO/SO Date'].fillna('')
    dat2['Order Created Date'] = dat2['Order Created Date'].fillna('')
    dat2['PQ Last Client Response Date'] = dat2['PQ Last Client Response Date'].fillna('')
    dat2['PQ First Response Date'] = dat2['PQ First Response Date'].fillna('')
    dat2['PQ Create Date'] = dat2['PQ Create Date'].fillna('')
    dat2['PR Received Date'] = dat2['PR Received Date'].fillna('')
    dat2['PQ First Approved Date'] = dat2['PQ First Approved Date'].fillna('')
    dat2['PR Received Date'] = dat2['PR Received Date'].fillna('')

    dat2['id'] = dat2['PR Received Date'] + dat2['PQ Last Client Response Date'] + dat2['PQ Proceed To PO/SO Date'] + \
                 dat2['Order Created Date'] + dat2['PQ Last Client Response Date'] + dat2['PQ First Response Date'] + \
                 dat2['PQ Create Date'] + dat2['PQ First Approved Date']

    dat2 = dat2[dat2['id'].str.contains(period) == True]

    dat2['slicer_1'] = 0

    # print 'vendor and PO loop'
    month_kpi = reporting_period[-2:]
    year_kpi = reporting_period[:4]

    for index, row in dat2.iterrows():
        vpd = str(row['Vendor Promised Date'])
        export = str(row['Vendor INCO Fulfillment Date'])
        po_conf = str(row['PO Vendor Confirmed Date'])
        po_sent = str(row['PO Sent to Vendor Date'])
        pq_action = str(row['PQ Actionable Date'])


        if po_sent == '':
            dat2.loc[index,'slicer_1'] = 1
                #print i
                #i += 1
        if po_sent != '':
            d2 = datetime.strptime(po_sent, "%m/%d/%Y")
            if d2.strftime("%m, %Y") == month_kpi+', '+year_kpi:

                if pq_action =='':
                    dat2.loc[index, 'slicer_1'] = 1

    # print 'checking to see where not applicable'


    dat2 = dat2[dat2['slicer_1'] == 1]

    dat2['slicer_1'] = 1
    for index, row in dat2.iterrows():

        id = row['identifier']

        for po_ids in po_list:
            if id == po_ids:
                #print id, po_ids
                dat2.loc[index, 'slicer_1'] = 0

    dat2 = dat2[dat2['slicer_1'] == 1]


    PO_cols = ['Grant#',
               'PE#',
               'PQ#',
               'Order#',
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
    print 'number of POs is ' + str(dat2.shape[0])
    print
    dat2.to_excel(writer, 'PO Turnaround Checks', index=False)

    del dat2
    dat2 = dat.copy()
    #PE Actionable Date	PE Expiry Date	PE Estimate Ready Date	PE Sent Date
    dat2['PE Response Date'] = dat2['PE Response Date'].fillna('')
    dat2['PE Actionable Date'] = dat2['PE Actionable Date'].fillna('')
    dat2['PE Expiry Date'] = dat2['PE Expiry Date'].fillna('')
    dat2['PE Estimate Ready Date'] = dat2['PE Estimate Ready Date'].fillna('')
    dat2['PE Sent Date'] = dat2['PE Sent Date'].fillna('')
    dat2['PE Create Date'] = dat2['PE Create Date'].fillna('')
    dat2['PR Last Submitted Date'] = dat2['PR Last Submitted Date'].fillna('')
    dat2['PR Received Date'] = dat2['PR Received Date'].fillna('')

    dat2['id'] = dat2['PR Received Date'] + dat2['PE Actionable Date'] + dat2['PE Expiry Date'] + \
                 dat2['PE Estimate Ready Date'] + dat2['PE Sent Date'] + dat2['PE Create Date'] + \
                 dat2['PR Last Submitted Date']

    dat2 = dat2[dat2['id'].str.contains(period)==True]

    dat2['slicer_1'] = 0

    i = 1
    for index, row in dat2.iterrows():

        if row['PE Response Date'] == '':
            dat2.loc[index,'slicer_1'] = 1
                #print i
                #i += 1
        if row['PE Response Date'] != '':

            d2 = datetime.strptime(row['PE Response Date'], "%m/%d/%Y")
            if d2.strftime("%m, %Y") == month_kpi + ', ' + year_kpi:
                #print 'hello world',i
                i+=1
                #print row['PE Response Date'],row['PE Actionable Date'],row['PE Sent Date']
                if row['PE Actionable Date'] == '' or row['PE Sent Date'] == '':
                    dat2.loc[index, 'slicer_1'] = 1

    dat2 = dat2[dat2['slicer_1']==1]

    pe_col_list =['Grant#',
     'Project Code',
     'PE#',
     'PQ#',
     'Contract Type',
     'PQ Buyer',
     'PQ Product Group',
     'PR Received Date',
     'PR Last Submitted Date',
     'PE Create Date',
     'PE Actionable Date',
     'PE Expiry Date',
     'PE Estimate Ready Date',
     'PE Sent Date',
     'PE Response Date',
     'PE Proceed To PQ Date',
        'comments']

    dat2 = dat2[pe_col_list]
    #dat2.to_excel(save_loc+'PEs_'+save_name+'.xlsx',index = False)
    print 'number of PEs is ' +str(dat2.shape[0])
    dat2.to_excel(writer, 'PE Turnaround Checks', index=False)

    writer.save()





