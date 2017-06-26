

'''
6/13/2017
changed output file structure to be a document with all of the associated rows, use slicers to subset to particular KPIs so we can look at rows indvidually

NOTES: Consider constructing R markdown or something similar for internal usage

6/9/2017
The purpose of this file is to generate the monthly KPIs

KPI 1 OTIF: based on the Order last delivery year month
KPI 2 PE Turnaround: PE Response Date is used to subset it and measured as the difference between PE actionable and PE sent date
KPI 3 PO Turnaround: subset on PO Sent to Vendor Date and PQ Actionable date to PO Sent to vendor date. A concern with this one
    is that the same date that is used to measure

KPI 4 FLT: measured against an external FLT matrix maintained by Ben Smith. It is a liability because lanes are added by hand and
    needs to be adjusted over time by Ben and downloaded from Knowledge Tree, same subset as OTIF (based on order last delivery year month)
    calculate actual lead time based on difference between Vendor Inco Fulfilment date and D1 date
KPI 5: same as before but just looking for those that were late... I think we placed a restraint on it looking at just ones outside of the bound for KPI 4

KPI 6 actual vs planned cost: period is set by Order last delivery month, planned costs are currently provided by Nikolai on the freight team.. they have lots of issues..
    Grant provides the actual costs from the finance team
KPI 7 within planned cost: looking for rows where the actual costs exceed the planned costs



To do as of 3/6/17
    Add the KPIs 6 and 7. but need the reporting format to be standardized. aim for week of 3/6 to do it

The purpose of this document is to generate the 7 KPIs for VPP reporting.
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
#matrix_file = 'PAD COR 5_11_17.csv'

#save_loc = MC_directory+month_year_file
#save_name = "KPIs_5_11_2017_v1.csv"
#save_yes_no = 'yes'
#dat = pd.read_csv(MC_directory + matrix_file)


#set once
#KPI 1

def run_kpis(matrix_file, dat, reporting_yr_month,save_loc,save_name,save_yes_no= 'yes'):


    reporting_order_month = reporting_yr_month
    #reporting_order_month = '2017-01'
    month_kpi = reporting_order_month[-2:]
    year_kpi = reporting_order_month[:4]

    ### KPI 6 #3 month lag
    #2 month lag
    def get_kpi_6(month,year):
        switch_list = ['01', '02']

        if month in switch_list:
            #print 'hello world'
            if month == '01':
                month_6 = '11'
                year_6 = int(year) - 1
                year_6 = str(year_6)
            if month == '02':
                month_6 = '12'
                year_6 = int(year) - 1
                year_6 = str(year_6)
        else:
            month_6 = int(month)-2
            month_6 = '0'+str(month_6)
            year_6 = year

        kpi_6_month_year = year_6+'-'+month_6
        return  kpi_6_month_year

    reporting_order_month_kpi6 = get_kpi_6(month_kpi,year_kpi)

    #KPI 4 and 5

    #matrix = pd.read_csv('C:/Users/585000/Desktop/PCFSM/FLT matrix calculations/flt_v8_3_mar_21_2017.csv')
    #new as of april 19
    #matrix = pd.read_csv('C:/Users/585000/Desktop/PCFSM/FLT matrix calculations/PPM Waiver and Transportation LT Matrix 2017Q2_4_19.csv')

    #new matrix for q1 and q2 of 2017
    #matrix_loc = 'C:/Users/585000/Desktop/PCFSM/FLT matrix calculations/quarter_matricies/matrix_tests/matrix_test_5.csv'
    #adjusted 6_12_17
    matrix_loc = 'C:/Users/585000/Desktop/PCFSM/FLT matrix calculations/quarter_matricies/matrix_tests/matrix_test_7.csv'

    matrix = pd.read_csv(matrix_loc)
    ### CAN ADJUST THE BRIDGE TO INCLUDE MULTIPLE
    bridge = pd.read_csv('C:/Users/585000/Desktop/PCFSM/FLT matrix calculations/bridge.csv')
    matrix_var_name = 'Full Lead Time (not including production)'
    # name in olde
    # r        'Lead Time: ASN Creation > ATP Date (Days+2 Days)'


    #### GET planned costs ####
    # referencing a google sheet which I maintain in my email drive, will need to have this coppied over for maintinance
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('C:/Users/585000/Desktop/Python Projects/PPM USAID/spreadsheets/client_secret_2.json', scope)

    gc = gspread.authorize(credentials)
    #1de7aqLFFSDAdrPYfdCS2WEye_zyqeoYlOViVlN6k3JY
    #wks = gc.open_by_key("1YzwH02udyNTTjM6pXXBQ7qruwuQixG7tc3CKwrgPs3M").get_worksheet(1)
    wks = gc.open_by_key("1de7aqLFFSDAdrPYfdCS2WEye_zyqeoYlOViVlN6k3JY").get_worksheet(0)

    type(wks.col_values(5)) #5 6 8

    test = wks.export()
    test = test.replace('"','')
    test = test.split('\r\n')
    '''
    asn = pd.DataFrame([sub.replace(",",'') for sub in wks.col_values(6)])
    asn.columns = asn.iloc[0]
    asn = asn.ix[1:]
    planned = pd.DataFrame([sub.replace(",",'')  for sub in wks.col_values(7)])
    planned.columns = planned.iloc[0]
    planned = planned.ix[1:]
    actual = pd.DataFrame([sub.replace(",",'')  for sub in wks.col_values(9)])
    actual.columns = actual.iloc[0]
    actual = actual.ix[1:]
    '''
    asn = pd.DataFrame([sub.replace(",",'') for sub in wks.col_values(1)])
    asn.columns = asn.iloc[0]
    asn = asn.ix[1:]
    planned = pd.DataFrame([sub.replace(",",'')  for sub in wks.col_values(2)])
    planned.columns = planned.iloc[0]
    planned = planned.ix[1:]
    actual = pd.DataFrame([sub.replace(",",'')  for sub in wks.col_values(3)])
    actual.columns = actual.iloc[0]
    actual = actual.ix[1:]

    spreadsheet = pd.DataFrame()#[asn['Shipment#'],planned['Planned Cost'],actual['Total Freight Cost']],axis=1)
    spreadsheet['Shipment#'] = asn['Shipment#']
    spreadsheet['Planned Cost'] = planned['Planned Cost']
    spreadsheet['Total Freight Cost'] = actual['Total Freight Cost']
    spreadsheet['Total Freight Cost'] = spreadsheet['Total Freight Cost'].str.replace('#N/A', '0')
    #spreadsheet['Total Freight Cost'] = spreadsheet['Total Freight Cost'].str.replace('', '0')

    spreadsheet['slicer'] = 0
    for index, row in spreadsheet.iterrows():
        if row['Shipment#'] =='' and row['Planned Cost'] =='' and row['Total Freight Cost'] =='' :
            spreadsheet.loc[index,'slicer'] = 1

    spreadsheet = spreadsheet[spreadsheet['slicer']== 0 ]
    spreadsheet.drop(['slicer'], axis=1, inplace=True)

    spreadsheet['Total Freight Cost'] = spreadsheet['Total Freight Cost'].apply(pd.to_numeric, args=('coerce',))
    spreadsheet['Planned Cost'] = spreadsheet['Planned Cost'].apply(pd.to_numeric, args=('coerce',))


    #############################
    #clean matrix and bridge
    for index, row in matrix.iterrows():
        matrix.loc[index,'lane_id'] = str(row['lane_id']).upper()

    start_time = time.time()

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

    ### merge in costs#####


    #########################
    '''
    dat['Order Last Delivery Recorded Year - Month'].isnull().sum()
    dat['Order Last Delivery Recorded Year - Month']=dat['Order Last Delivery Recorded Year - Month'].fillna("NANNN")
    dat = dat[dat['Order Last Delivery Recorded Year - Month'].str.contains(reporting_order_month_kpi6)]
    '''
    #Part 2: Mark which ones for which KPI
        # for now will mark with N number cols 0 or 1 where N is number of KPI 5 for now?
        #Mark all rows which apply to a KPI
    dat['Order Last Delivery Recorded Year - Month'].isnull().sum()
    dat['Order Last Delivery Recorded Year - Month']=dat['Order Last Delivery Recorded Year - Month'].fillna("NANNN")
    dat['KPI 1 OTIF'] = np.where(dat['Order Last Delivery Recorded Year - Month'].str.contains(reporting_order_month),1,0)


    #dat['14 counter'] = np.where(dat['COTD Category']=='14 Days or Less',1,0)


    ### 1/19 changed PE sent to PE Response Date per instructions
    ### marking rows which fall into KPIs 2 and 3
    dat['KPI 2 PE Turnaround'] = 0
    dat['KPI 3 PO Turnaround'] = 0
    po_list =[]
    pe_list =[]
    for index, row in dat.iterrows():
        d= str(row['PE Response Date'])
        d2= str(row['PO Sent to Vendor Date'])

        #new idea to test 5/4
        #d2 = str(row['PO Vendor Confirmed Date'])
        in_pe = int(row['KPI 2 PE Turnaround'])
        pe_num = str(row['PE#'])

        in_po = int(row['KPI 3 PO Turnaround'])
        po_num = str(row['Order#'])

        if d != 'nan':
            d = datetime.strptime(d, "%m/%d/%Y")

            if d.strftime("%m, %Y") == month_kpi+', '+year_kpi:
                if pe_num not in pe_list:
                    dat.loc[index,'KPI 2 PE Turnaround'] = 1
                    pe_list.append(pe_num)

        if d2 != 'nan':
            d2 = datetime.strptime(d2, "%m/%d/%Y")
            if d2.strftime("%m, %Y") == month_kpi+', '+year_kpi:
                if po_num not in po_list:
                    dat.loc[index,'KPI 3 PO Turnaround'] = 1
                    po_list.append(po_num)

    #4, 5, 6, and 7 use same month criteria as KPI 1
    dat['KPI 4 FLT'] = np.where(
                dat['Order Last Delivery Recorded Year - Month'].str.contains(reporting_order_month), 1, 0)

    #set this one after kpi 4
    dat['KPI 5 FLT var>0'] = 0
    dat['KPI 6 freight_costs'] = np.where(dat['Order Last Delivery Recorded Year - Month'].str.contains(reporting_order_month_kpi6),1,0)
    dat['KPI 7 fc var>0'] = 0
    #print dat['KPI 6 freight_costs'].value_counts()

    dat['slicer_1'] = 1
    for index, row in dat.iterrows():

        if row['KPI 1 OTIF'] != 1 and row['KPI 2 PE Turnaround'] != 1 and row['KPI 3 PO Turnaround']!= 1 and row['KPI 4 FLT']!=1 and row['KPI 6 freight_costs'] != 1:
            dat.loc[index, 'slicer_1'] = 0

    #dat should not be a subset of only those that appear in any given KPI
    dat =dat[dat['slicer_1']==1]
    dat.drop(['slicer_1','Ta0'], axis=1, inplace=True)

    # for KPI 4 and 5
    dat = pd.merge(dat,bridge,how='left', on='Order Pick Up Country Name')
    #Asia-Afghanistan-Air-CIP
    #CHECK THAT IT IS SHIP TO COUNTRY NAME
    for index, row in dat.iterrows():
        a = str(row['Origin Region'])+'-'+str(row['Ship To Country Name'])+'-'+str(row['Shipment Mode'])+'-'+str(row['Client INCO Term'])

        dat.loc[index, 'Origin+Dest+Mode+INCO'] = a.upper()
        #print a.upper()

    ######################################################
    #### This section needs updating as new lanes are added and matrixes are updated by Ben smith

    dat = pd.merge(dat,matrix,how='left', left_on='Origin+Dest+Mode+INCO',right_on='lane_id')
    #Order Created Date
    col_keeper = ['-01','-02','-03','-04']
    qtr_col_names = list(matrix.columns)
    toss_col = []
    for col in qtr_col_names:
        test = 0
        for keep in col_keeper:

            if keep in col:
                test = 1
        if test == 0:
            toss_col.append(col)
            #qtr_col_names.remove(col)
            #print qtr_col_names
    toss_col.append('2017-01 leadtimes') #use this as default
    qtr_col_names = [item for item in qtr_col_names if item not in toss_col]


    dat['PO Sent to Vendor Date'] = dat['PO Sent to Vendor Date'].fillna('')

    for index, row in dat.iterrows():
        col_indicator = 0
        order_create_date = str(row['PO Sent to Vendor Date'])
        if order_create_date != '':
            order_create_date = order_create_date.split('/')
            if str(order_create_date[0]) == '4' or str(order_create_date[0]) == '5' or str(order_create_date[0]) == '6':
                #print 'hello'
                order_create_qtr = str(order_create_date[2])+'-02'
                #print order_create_qtr
            elif str(order_create_date[0]) == '7' or str(order_create_date[0]) == '8' or str(order_create_date[0]) == '9':
                order_create_qtr = str(order_create_date[2])+'-03'
            elif str(order_create_date[0]) == '10' or str(order_create_date[0]) == '11' or str(order_create_date[0]) == '12':
                order_create_qtr = str(order_create_date[2]) + '-04'
            else:
                order_create_qtr = str(order_create_date[2]) + '-01'

        if order_create_date == '':
            order_create_qtr = 'null_zz'

        for col_name in qtr_col_names:
            col_name = str(col_name)

            if col_indicator == 1:
                continue
            if order_create_qtr in col_name:

                #print order_create_qtr,col_name
                dat.loc[index, matrix_var_name] = row[col_name]
                col_indicator = 1

        if col_indicator == 0:
            #print order_create_qtr

            dat.loc[index,matrix_var_name] = row['2017-01 leadtimes']


    ###################################################### NEEED TO UPDATE!


    #me being lame and doing percents the long way
    # calculation using COTD category, which is a calculated field between D1 and client promised date
    cotd_list = []
    i = 1
    for index, row in dat.iterrows():
        cotd = str(row['COTD Category'])

        if row['KPI 1 OTIF'] == 1:
            cotd_list.append(cotd)
            if cotd == '14 Days or Less':
                dat.loc[index,'14 counter'] = 1
            if cotd ==  '15-30 Days':
                dat.loc[index,'15 counter'] = 1
            if cotd == '31 Days or More':
                i+=1
                dat.loc[index,'31 counter'] = 1
            if cotd == 'Unknown':
                dat.loc[index,'unkown counter'] = 1


    c14 = dat['14 counter'].sum()
    c15 = dat['15 counter'].sum()
    c31 = dat['31 counter'].sum()
    #generate the statistic
    otif = float(c14)/(c14+c15+c31)


    # switched PE and PO to use days_between function rather than business days:
    def business_days_between(d1, d2):
        d1 = datetime.strptime(d1, "%m/%d/%Y")
        d2 = datetime.strptime(d2, "%m/%d/%Y")
        return networkdays(d1, d2)


    def days_between(d1, d2):

        d1 = datetime.strptime(d1, "%m/%d/%Y")
        d2 = datetime.strptime(d2, "%m/%d/%Y")
        return (d2 - d1).days


    pe_to_list = []
    po_to_list = []
    kpi_4_list = []
    nanz = 0
    counter = 0
    kpi_4_list_full = []


    #calculations for KPI 2, 3, and 4
    for index, row in dat.iterrows():
        pe_actionable = str(row['PE Actionable Date'])
        pe_sent = str(row['PE Sent Date'])

        pq_actionable = str(row['PQ Actionable Date'])
        pq_sent = str(row['PO Sent to Vendor Date'])

        vendor_fil_date = str(row['Vendor INCO Fulfillment Date'])
        d1 = str(row['Shipment Delivered Date'])

        #for the ones which are ok, unflag them. Basically start with all that fit in KPI and remove those that are ok
        if row['KPI 1 OTIF'] == 1 and str(row['COTD Category'])=='14 Days or Less':
            dat.loc[index,'KPI 1 OTIF'] = 'within'

        #calculate KPI 2, and mark those that fall as less than 3 days since those are within bounds
        if row['KPI 2 PE Turnaround'] == 1 and pe_actionable != 'nan' and pe_sent != 'nan':
            pe_turnaround_time = days_between(pe_actionable, pe_sent)
            pe_to_list.append(pe_turnaround_time)

            if pe_turnaround_time >3:
                dat.loc[index, 'pe_turnaround'] = pe_turnaround_time
            if pe_turnaround_time<= 3:
                dat.loc[index, 'KPI 2 PE Turnaround'] = 'within'
                dat.loc[index, 'pe_turnaround'] = pe_turnaround_time

        # for KPI 3 the target is within 7 days
        if row['KPI 3 PO Turnaround'] == 1 and pq_actionable != 'nan' and pq_sent != 'nan':
            pq_turnaround_time = days_between(pq_actionable, pq_sent)
            po_to_list.append(pq_turnaround_time)

            if pq_turnaround_time > 7:
                dat.loc[index, 'po_turnaround'] = pq_turnaround_time
            if pq_turnaround_time <= 7:
                dat.loc[index, 'KPI 3 PO Turnaround'] = 'within'
                dat.loc[index, 'po_turnaround'] = pq_turnaround_time

        # this one is a bit convoluted because the business teams didnt want to
        # have to look at all of the rows not within KPI... because life is hard?
        if row['KPI 4 FLT'] == 1 and  vendor_fil_date != 'nan' and d1 != 'nan':
            flt = days_between(vendor_fil_date,d1)
            plt = str(row[matrix_var_name])
            kpi_4_list_full.append((flt-float(plt))/float(plt))

            #have had issues with nan rows. and it is fairly common to see new rows
            if plt == 'nan' or flt =='nan':
                nanz +=1
                flt_vs_plt = 'nan'
                flt_minus_plt ='nan'
                dat.loc[index, 'flt_vs_plt'] = flt_vs_plt
                dat.loc[index, 'flt_-_plt'] = flt_minus_plt

                #dat.loc[index, 'flt']
            # if the variation is within 125 of 0 then dont have to report them
            else:
                counter += 1
                plt = float(plt)
                flt_vs_plt = str((flt - plt) / plt)
                # print(flt_vs_plt,flt_vs_plt == 0.0)
                flt_minus_plt = flt - plt
                if flt < 0:
                    dat.loc[index, 'flt_vs_plt'] = 'flt less than 0, check vendor inco and D1 dates'
                    dat.loc[index, 'flt_-_plt'] = ''
                if flt >= 0:
                    dat.loc[index, 'flt_vs_plt'] = flt_vs_plt
                    dat.loc[index, 'flt_-_plt'] = flt_minus_plt
                    kpi_4_list.append(flt_vs_plt)

                if flt_vs_plt <= .12 and flt_vs_plt >= (-.12):
                    dat.loc[index, 'KPI 4 FLT'] = 'within'

    # additional chec added later to check if the flt- plt is within 14 days.. mirrors the COTD category buffer of 28 days (14 on either side)
    for index, row in dat.iterrows():
        if row['KPI 4 FLT'] == 1:
            flt_minus_plt = row['flt_-_plt']
            if flt_minus_plt <= 14 and flt_minus_plt >= -14:
                dat.loc[index, 'KPI 4 FLT'] = 'within'

    order_list = []
    #this one may have to be taken out. effort to reduce number of rows that are put in for root cause analysis...
    #
    '''
    for index,row in dat.iterrows():
        order_num = row['Order#']
        if row['KPI 4 FLT'] == 1:
            if order_num in order_list:
                dat.loc[index, 'KPI 4 FLT'] = 'within'
            else:
                order_list.append(order_num)
    '''

    # KPI 5 is based on KPI 4 outputs so just check whether the calculations are under 0
    # this could be made more efficient... but with the current setup it only has to iterate over a few hundred rows so it is computationally light
    for index,row in dat.iterrows():
        if row['KPI 4 FLT'] == 1 or row['KPI 4 FLT'] == 'within':
            if row['flt_vs_plt'] >0:
                dat.loc[index, 'KPI 5 FLT var>0'] = 1
            else:
                dat.loc[index, 'KPI 5 FLT var>0'] = 'within'

    #### KPI 6 for testing
    kpi_6_list = []
    kpi_6_dict = {}
    #print(dat['FB Demurrage'].isnull().sum())
    dat['FB Demurrage'] = dat['FB Demurrage'].fillna(0)
    dat['FB Mod Fda'] = dat['FB Mod Fda'].fillna(0)
    dat = pd.merge(dat,spreadsheet,how='left',on='Shipment#',indicator=True)

    i=0
    z =0

    #calculating kpi 6 and 7
    #
    for index,row in dat.iterrows():

        planned = row['Planned Cost']
        total_fc = row['Total Freight Cost']

        if row['KPI 6 freight_costs'] == 1:
            if  planned !=0 and total_fc != 0:
                i+=1
                if math.isnan(planned)!= True and  math.isnan(total_fc)!= True:
                    z+=1
                    #total freight costs are the freight costs minus the side costs and mod fda costs since we are not responsible for paying those
                    # and they do not count against our totals for KPI purposes
                    side_costs = row['FB Demurrage'] + row['FB Mod Fda']
                    total_freight  = (float(total_fc) - float(side_costs))

                    bvp = (total_freight - planned) / planned

                    kpi_6_dict[row['Shipment#']] = bvp
                    dat.loc[index,'book_actual_vs_planned'] = bvp
                    dat.loc[index,'side_costs'] = side_costs

                    kpi_6_list.append(bvp)
                    #if bvp <=.1 and bvp >=-.1:
                    #    dat.loc[index, 'KPI 6 freight_costs'] = 0

    #print i,z
    #dat['KPI 7 fc var>0']
    # only marks ones which are outside of the
    if 'book_actual_vs_planned' in dat.columns:
        for index,row in dat.iterrows():
            if row['KPI 6 freight_costs'] == 1:
                if row['book_actual_vs_planned'] <= 0:
                    dat.loc[index, 'KPI 7 fc var>0'] = 'within'
                else:
                    dat.loc[index, 'KPI 7 fc var>0'] = 1
    if 'book_actual_vs_planned' not in dat.columns:
        dat['KPI 7 fc var>0'] = 0

    #remove rows which we dont need
    dat['slicer_1'] = 1
    for index, row in dat.iterrows():

        if row['KPI 6 freight_costs'] == 0 and row['KPI 1 OTIF'] == 0 and row['KPI 2 PE Turnaround'] == 0 and row['KPI 3 PO Turnaround']== 0 and row['KPI 4 FLT']== 0:
            dat.loc[index, 'slicer_1'] = 0

    #dat should not be a subset of only those that appear in any given KPI
    dat =dat[dat['slicer_1']==1]

    #KPI outputs
    otif = otif
    pe_turnaround = np.median(pe_to_list)
    po_turnaround = np.median(po_to_list)

    #remove nan from kpi4
    kpi_4_list = [float(i) for i in kpi_4_list]
    kpi_4_eval = np.median(kpi_4_list)

    kpi_5_eval_fail = float(sum(i > 0 for i in kpi_4_list)) / len(kpi_4_list) #how many above 0
    kpi_5_eval_pass_per =  float(sum(i <= 0 for i in kpi_4_list)) / len(kpi_4_list) #how many within
    kpi_5_eval_pass =  int(sum(i <= 0 for i in kpi_4_list))

    kpi_6_list =[float(i) for i in kpi_6_list]
    kpi_6_eval = np.median(kpi_6_list)

    if len(kpi_6_list) ==0:
        kpi_7_eval_pass_per = 0
        kpi_7_eval_pass = "Nope.... No Planned or Actual Cost pairs"

    if len(kpi_6_list) !=0:

        kpi_7_eval_pass_per =  float(sum(i <= 0 for i in kpi_6_list)) / len(kpi_6_list) #how many within
        kpi_7_eval_pass =  int(sum(i <= 0 for i in kpi_6_list))


    print('############################## KPI OUTPUTS ##############################')
    print 'date: ' +str(time.strftime("%b %d, %Y"))
    print reporting_order_month
    print matrix_file
    print
    print("OTIF: %.4f%%" % (otif*100)+" or " +str(c14)+' out of ' +str((c14+c15+c31)) +" target >= 85%" )
    print
    print("PE Turnaround: "+ str(pe_turnaround) +" target <= 3 days" + " N="+str(len(pe_to_list)))
    print
    print("PO Turnaround: "+ str(po_turnaround) +" target <= 7 days" + " N="+str(len(po_to_list)))
    print
    print("FLT: %.4f%%" % (kpi_4_eval*100)+" total of "+str(len(kpi_4_list)) +" target -12% <= x <= 12% "+str(nanz))
    print
    print("Within Lead Times: %.2f%%" % (kpi_5_eval_pass_per*100) +' or '+str(kpi_5_eval_pass)+ ' out of '+str(len(kpi_4_list))+" target >=75%")
    print
    print('Freight Costs: ' +str(kpi_6_eval) +" target median +- 10% N= "+str(len(kpi_6_list)))
    print
    print("Within Freight Costs: %.2f%%" % (kpi_7_eval_pass_per*100) +' or '+str(kpi_7_eval_pass)+ ' out of '+str(len(kpi_6_list))+" target >=75%")
    print('############################## KPI OUTPUTS ##############################')



    dat.drop(['slicer_1','Origin Region', 'Origin'	,'Dest',	'Mode',	'Client Incoterm',
              '14 counter',	'15 counter',	'31 counter' , '2017-01 leadtimes','2017-02 leadtimes'], axis=1, inplace=True)

    if matrix_var_name == 'Lead Time: ASN Creation > ATP Date (Days+2 Days)':
        dat.rename(columns = {'Lead Time: ASN Creation > ATP Date (Days+2 Days)':'Planned Lead Time'}, inplace = True)

    if save_yes_no == 'yes':

        dat.to_csv(save_loc+save_name,index=False)

    print("--- %s seconds ---" % (time.time() - start_time))

    #return kpi_4_list