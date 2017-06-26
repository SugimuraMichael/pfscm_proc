

'''
Submission to Mirjam to help and flag PE and POs
PE sent and PE response dates

Check preceeding date fields and search for 2017 fields??? and then check for blanks....

1) Check for PR Received Date 2016-2017
2) Check remaining 4K ish rows line by line for 2017s
3) flag blanks in requireed rows

4) flag remaining blank rows?

Check the approved dates

PO approval check sent
PE approval check sent

Feedback from Mirjam,
X -save as excel
 -subset to relevant cols
 PO :Grant#	PE#	PQ#	Order#	Order Type	Order Short Closed	Order Point of Contact	PQ Buyer	PQ Product Group	Managed By	PR Received Date	PE Create Date	PE Actionable Date	PE Sent Date	PE Response Date	PE Proceed To PQ Date	PQ Create Date	PQ Actionable Date	PQ Proceed To PO/SO Date	Order Created Date	PO Sent to Vendor Date	PO Vendor Confirmed Date	Vendor Promised Date	comments

 PE: Grant#	Project Code	PE#	PQ#	Contract Type	PQ Buyer	PQ Product Group	PR Received Date	PR Last Submitted Date	PE Create Date	PE Actionable Date	PE Expiry Date	PE Estimate Ready Date	PE Sent Date	PE Response Date	PE Proceed To PQ Date

'''



import numpy as np
from workdays import networkdays
import time
from datetime import datetime
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import math
from collections import Counter
#doesnt change
#MC_directory = 'C:/Users/585000/Desktop/PCFSM/2017 KPIs/'
#ADJUST: monthy_year
#month_year_file = 'may 2017/'
#ADJUST: FILE NAME

### USE PAD COR not pad cor ppm
#matrix_file = 'PAD COR 5_01_17.csv'

#save_loc = 'C:/Users/585000/Desktop/PCFSM/adhoc reports/'
#save_name = "5_4_2017"

#dat = pd.read_csv(MC_directory+matrix_file)

### STANDARD
def pe_po(dat,save_name,save_loc,period = '2017'):
    # part 1: Remove rows as required
    #remove the Ta0 items
    dat['Ta0'] = 0
    for index, row in dat.iterrows():
        a = str(row['Project Code'])
        a = a[-3:]
        if a == 'TA0':
            dat.loc[index, 'Ta0'] = 1

    dat = dat[dat['Ta0'] == 0]

    ## NEED TO FIX
    dat = dat[dat['Client Type'] != 'NGF']

    dat = dat[dat['Managed By - Project']!= 'SCMS']
    dat = dat[dat['Order Short Closed'] != "Yes"]

    ###


    #pattern = '|'.join(period)
    dat['PR Received Date'] = dat['PR Received Date'].fillna('')
    #dat = dat[dat['PR Received Date'].str.contains(pattern)]
    dat['comments'] = ''
    #PQ Last Client Response Date	PQ Proceed To PO/SO Date	Order Created Date
    i = 1
    dat['PO Sent to Vendor Date'] = dat['PO Sent to Vendor Date'].fillna('')
    dat['PQ Actionable Date'] = dat['PQ Actionable Date'].fillna('')
    dat['slicer_1'] = 0
    dat2 = dat.copy()

    dat2['PQ Last Client Response Date'] = dat2['PQ Last Client Response Date'].fillna('')
    dat2['PQ Proceed To PO/SO Date'] = dat2['PQ Proceed To PO/SO Date'].fillna('')
    dat2['Order Created Date'] =dat2['Order Created Date'].fillna('')
    dat2['PQ Last Client Response Date'] = dat2['PQ Last Client Response Date'].fillna('')
    dat2['PQ First Response Date'] = dat2['PQ First Response Date'].fillna('')
    dat2['PQ Create Date'] = dat2['PQ Create Date'].fillna('')
    dat2['PR Received Date'] = dat2['PR Received Date'].fillna('')
    dat2['PQ First Approved Date'] = dat2['PQ First Approved Date'].fillna('')

    dat2['id'] = dat2['PR Received Date']+dat2['PQ Last Client Response Date']+dat2['PQ Proceed To PO/SO Date']+\
                 dat2['Order Created Date']+dat2['PQ Last Client Response Date']+dat2['PQ First Response Date']+\
                 dat2['PQ Create Date']+dat2['PQ First Approved Date']

    dat2 = dat2[dat2[dat2['id'].str.contains(period)==True]]

    for index, row in dat2.iterrows():

        if row['PO Sent to Vendor Date'] == '':
            dat2.loc[index,'slicer_1'] = 1
                #print i
                #i += 1
        if row['PO Sent to Vendor Date'] != '':
            if row['PQ Actionable Date'] =='':
                dat2.loc[index, 'slicer_1'] = 1

    dat2 = dat2[dat2['slicer_1']==1]
    #get cols
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
     'comments']

    dat2 = dat2[PO_cols]
    #dat2.to_excel(save_loc+'POs_'+save_name+'.xlsx',index = False)
    writer = pd.ExcelWriter(save_loc+save_name)
    dat2.to_excel(writer, 'POs to check', index=False)

    print
    print 'number of POs is ' +str(dat2['Order#'].nunique())
    print
    del dat2

    dat2 = dat.copy()
    #PE Actionable Date	PE Expiry Date	PE Estimate Ready Date	PE Sent Date
    dat2['PE Response Date'] = dat2['PE Response Date'].fillna('')
    dat2['PE Actionable Date'] = dat2['PE Actionable Date'].fillna('')
    dat2['PE Sent Date'] = dat2['PE Sent Date'].fillna('')

    dat2['PE Actionable Date'] = dat2['PE Actionable Date'].fillna('')
    dat2['PE Expiry Date'] = dat2['PE Expiry Date'].fillna('')
    dat2['PE Estimate Ready Date'] =dat2['PE Estimate Ready Date'].fillna('')
    dat2['PE Sent Date'] = dat2['PE Sent Date'].fillna('')
    dat2['PE Create Date'] = dat2['PE Create Date'].fillna('')
    dat2['PR Last Submitted Date'] = dat2['PR Last Submitted Date'].fillna('')
    dat2['PR Received Date'] = dat2['PR Received Date'].fillna('')

    dat2['id'] = dat2['PR Received Date']+dat2['PE Actionable Date']+dat2['PE Expiry Date']+\
                 dat2['PE Estimate Ready Date']+dat2['PE Sent Date']+dat2['PE Create Date']+\
                 dat2['PR Last Submitted Date']

    dat2 = dat2[dat2[dat2['id'].str.contains(period)==True]]

    '''
        pe_actionable = str(row['PE Actionable Date'])
    pe_sent = str(row['PE Sent Date'])
    '''
    for index, row in dat2.iterrows():

        if row['PE Response Date'] == '':
            dat2.loc[index,'slicer_1'] = 1
                #print i
                #i += 1
        if row['PE Response Date'] != '':
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
    print 'number of PEs is ' +str(dat2['PE#'].nunique())
    dat2.to_excel(writer, 'PEs to check', index=False)

    writer.save()

    del dat2
    del dat
