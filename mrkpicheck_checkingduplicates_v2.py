

'''
The purpose of this file is to check the PAD COR dataset for duplicate lines based on the three fields that
are used to subset the dataset. the concern here is that if there are duplicate lines with different values then
it can throw off calculations for the different PO or PE related dates where you have to remove duplicates


'''

import pandas as pd

#directory = 'C:/Users/585000/Desktop/PCFSM/2017 KPIs/'
#ADJUST: monthy_year
#month_year_file = 'may 2017/'
#ADJUST: FILE NAME

# USE PAD COR not pad cor ppm
#matrix_file = 'PAD COR 5_11_17.csv'


#dat = pd.read_csv(directory+matrix_file)

'''
period is based on Order Last Delivery date, setting it to 2017 for now.
can be any list. Also needs to be fed a PAD cor dataset

period is used to filter each KPI to rows which would be relevant based on that KPI's date fields
'''
def check_incomplete_duplicates(input_dat, period = ['2016','2017']):
    # POs
    input_dat['PO Sent to Vendor Date'] =     input_dat['PO Sent to Vendor Date'].fillna('')
    input_dat['PE Response Date'] =     input_dat['PE Response Date'].fillna('')

    input_dat['Order Last Delivery Recorded Year - Month'] =     input_dat['Order Last Delivery Recorded Year - Month'].fillna('')

    input_dat['Ta0'] = 0
    for index, row in input_dat.iterrows():
        a = str(row['Project Code'])
        a = a[-3:]
        if a == 'TA0':
            input_dat.loc[index, 'Ta0'] = 1

    input_dat = input_dat[input_dat['Ta0'] == 0]

    ## NEED TO FIX
    input_dat = input_dat[input_dat['Client Type'] != 'NGF']

    input_dat = input_dat[input_dat['Managed By - Project']!= 'SCMS']
    input_dat = input_dat[input_dat['Order Short Closed'] != "Yes"]

    dat = input_dat.copy()

    pattern = '|'.join(period)
    dat['PR Received Date'] = dat['PR Received Date'].fillna("NANNN")

    dat['id'] = dat['PR Received Date'] + dat['PQ Last Client Response Date'] + dat['PQ Proceed To PO/SO Date'] + \
                dat['Order Created Date'] + dat['PQ Last Client Response Date'] + dat['PQ First Response Date'] + \
                dat['PQ Create Date'] + dat['PQ First Approved Date']
    dat['id'] = dat['id'].fillna('')
    dat = dat[dat['id'].str.contains(pattern)]

    dat = pd.DataFrame(dat.groupby(['Order#']).aggregate({
                                    'PO Sent to Vendor Date' : lambda x: x.nunique(),
                                    'Order Last Delivery Recorded Year - Month': lambda x: x.nunique()

                                                          }).reset_index())


    print
    print '#################### DUPLICATION ############################'
    print "OTIF ISSUES"
    print "PO, POsent, Order Last Delivery Recorded Year - Month"
    for index, row in dat.iterrows():
        order = row['Order#']

        posent = row['PO Sent to Vendor Date']
        actionable = row['Order Last Delivery Recorded Year - Month']
        if posent > 1 or actionable > 1:

            print order,  posent , actionable

    del dat
    #PE TURNAROUND
    print
    print "PE TURNAROUND DUPLICATION ISSUES"

    dat = input_dat.copy()

    pattern = '|'.join(period)
    dat['PR Received Date'] = dat['PR Received Date'].fillna("NANNN")

    dat['id'] = dat['PR Received Date'] + dat['PE Actionable Date'] + dat['PE Expiry Date'] + \
                dat['PE Estimate Ready Date'] + dat['PE Sent Date'] + dat['PE Create Date'] + \
                dat['PR Last Submitted Date']
    dat['id'] = dat['id'].fillna('')
    dat = dat[dat['id'].str.contains(pattern)]

    dat = pd.DataFrame(dat.groupby(['PE#']).aggregate({'PE Response Date': lambda x: x.nunique(),

                                                          }).reset_index())
    print "PE, response"
    for index, row in dat.iterrows():
        PE = row['PE#']
        response = row['PE Response Date']



        if response > 1:
            print PE, response

    print
    print "END"
    del dat



#check_incomplete_duplicates(dat)