


'''
file to process non PPM for a few managed by groups. It is an ocasional request

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

def run_kpis_nonppm(matrix_file, dat, reporting_yr_month,save_loc,save_name,save_yes_no= 'yes'):
    dat['PE Actionable Date'] = dat['PE Actionable Date'].fillna('')
    dat['PE Sent Date'] = dat['PE Sent Date'].fillna('')
    dat['PE Response Date'] = dat['PE Response Date'].fillna('')
    dat['PQ Actionable Date'] = dat['PQ Actionable Date'].fillna('')
    dat['PO Sent to Vendor Date'] = dat['PO Sent to Vendor Date'].fillna('')
    dat['Vendor INCO Fulfillment Date'] = dat['Vendor INCO Fulfillment Date'].fillna('')
    dat['Shipment Delivered Date'] = dat['Shipment Delivered Date'].fillna('')
    dat['Order Last Del.Rec.Year-Month']=dat['Order Last Del.Rec.Year-Month'].fillna("")


    reporting_order_month = reporting_yr_month
    #reporting_order_month = '2017-01'
    month_kpi = reporting_order_month[-2:]
    year_kpi = reporting_order_month[:4]



    # part 1: Remove rows as required
    #remove the Ta0 items
    dat['T50'] = 0
    for index, row in dat.iterrows():
        a = str(row['Project Code'])
        a = a[-3:]
        if a == 'T50':
            dat.loc[index, 'T50'] = 1

    dat = dat[dat['T50'] == 0]

    ## NEED TO FIX
    #dat = dat[dat['Client Type'] != 'NGF']

    dat = dat[dat['Managed By - Project']!= 'VPP']
    dat = dat[dat['Short Closed'] != "Yes"]

    ### merge in costs#####


    #########################

    #Part 2: Mark which ones for which KPI
        # for now will mark with N number cols 0 or 1 where N is number of KPI 5 for now?
        #Mark all rows which apply to a KPI
    #dat['Order Last Delivery Recorded Year - Month'].isnull().sum()
    #dat['Order Last Delivery Recorded Year - Month']=dat['Order Last Delivery Recorded Year - Month'].fillna("NANNN")
    #dat['KPI 1 OTIF'] = np.where(dat['Order Last Delivery Recorded Year - Month'].str.contains(reporting_order_month),1,0)


    #dat['14 counter'] = np.where(dat['COTD Category']=='14 Days or Less',1,0)


    ### 1/19 changed PE sent to PE Response Date per instructions
    ### marking rows which fall into KPIs 2 and 3

    po_list =[]
    pe_list =[]

    for index, row in dat.iterrows():
        d= str(row['PE Response Date'])
        d2= str(row['PO Sent to Vendor Date'])


        pe_num = str(row['PE#'])

        po_num = str(row['Order#'])

        if d != '':
            d = datetime.strptime(d, "%m/%d/%Y")
            dat.loc[index, 'KPI 2 PE Turnaround month'] = d.strftime("%Y-%m")

        if d2 != '':
            d2 = datetime.strptime(d2, "%m/%d/%Y")
            dat.loc[index, 'KPI 3 PO Turnaround month'] = d2.strftime("%Y-%m")


    ###################################################### NEEED TO UPDATE!


    #me being lame and doing percents the long way
    # calculation using COTD category, which is a calculated field between D1 and client promised date


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



    #calculations for KPI 2, 3, and 4
    for index, row in dat.iterrows():
        pe_actionable = str(row['PE Actionable Date'])
        pe_sent = str(row['PE Sent Date'])

        pq_actionable = str(row['PQ Actionable Date'])
        pq_sent = str(row['PO Sent to Vendor Date'])

        vendor_fil_date = str(row['Vendor INCO Fulfillment Date'])
        d1 = str(row['Shipment Delivered Date'])

        #for the ones which are ok, unflag them. Basically start with all that fit in KPI and remove those that are ok
        #calculate KPI 2, and mark those that fall as less than 3 days since those are within bounds
        if pe_actionable != '' and pe_sent != '':
            pe_turnaround_time = days_between(pe_actionable, pe_sent)
            pe_to_list.append(pe_turnaround_time)
            dat.loc[index, 'pe_turnaround'] = pe_turnaround_time



        # for KPI 3 the target is within 7 days
        if pq_actionable != '' and pq_sent != '':
            pq_turnaround_time = days_between(pq_actionable, pq_sent)
            po_to_list.append(pq_turnaround_time)
            dat.loc[index, 'po_turnaround'] = pq_turnaround_time





    if save_yes_no == 'yes':

        dat.to_csv(save_loc+save_name,index=False)

    print("--- %s seconds ---" % (time.time() - start_time))

    return dat

########################################################################################################################

#def run_kpis(matrix_file, dat, reporting_yr_month,save_loc,save_name,save_yes_no= 'yes'):

import pandas as pd
import numpy as np

from mrkpicheck.data_cleaning import replace_SCMS
import os.path
import os
import time
#doesnt change
MC_directory = 'C:/Users/585000/Desktop/PCFSM/'

### USE PAD COR not pad cor ppm
matrix_file = 'pad_li_6_16'
dat = pd.read_csv(MC_directory + matrix_file+'.csv')

#old_dat= pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/final submissions/Predictive Analysis Dataset_COR_March 2017_pulled 4-13 (1).csv')
#old_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 5_05_17.csv')
old_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 5_11_17.csv')
new_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 6_12_17.csv')


version='test'
month = 'may'

#OPTIONS
save_yes_no = 'yes'
#KPIs
reporting_period = '2017-05'
#checking supply
comparison_date = '06/06/2017'
supply_period = '2017'
#comparing pad cors
compare_reporting_order_month = ['2017-01','2017-02','2017-03','2017-04']
Monday = 'yes'
#PE PO
pe_po_period  = '2017'

save_loc = 'C:/Users/585000/Desktop/PCFSM/monthly reporting files/'+month+'/'+version+'/'
#save names
save_name = "NON_PPM_KPIs_2_"+matrix_file+version+'.csv'
compare_save_name = "change_tracker_"+matrix_file+version+'.xlsx'
supply_save_name = 'kpi_and_supplier_checks_'+matrix_file+version+'.xlsx'
blank_save_name = 'Checking_blanks_'+matrix_file+version+'.xlsx'
checking_vipd_po = matrix_file+version+'_VIFD_report.xlsx'


if not os.path.exists(save_loc):
    os.makedirs(save_loc)
#dat2 = run_kpis(matrix_file, dat, reporting_period, save_loc, save_name, save_yes_no=save_yes_no)

if os.path.isfile(save_loc+save_name) == False:
    dat2 = replace_SCMS(dat)
    dat2 = run_kpis_nonppm(matrix_file, dat, reporting_period, save_loc, save_name, save_yes_no=save_yes_no)

if os.path.isfile(save_loc+save_name) == True:
    print 'hello world'
    dat2 = pd.read_csv(save_loc+save_name)

start_time = time.time()


def generate_individual_kpi_numbers_nonppm(dat, months= ['2017-05']):
    #KPI 1

    otif_final = []
    ontime_number = []
    otif_total_list = []
    pe_time = []
    pe_num = []
    po_time = []
    po_num = []

    value_list= []
    for month in months:
        dat2 = dat.copy()
        reporting_period = [month]
        pattern = '|'.join(reporting_period)
        dat2['Order Last Del.Rec.Year-Month'] = dat2['Order Last Del.Rec.Year-Month'].fillna('')
        dat2 = dat2[dat2['Order Last Del.Rec.Year-Month'].str.contains(pattern)]

        dat2 = dat2[dat2['COTD - Category']!='Unknown']
        otif_dict = dat2['COTD - Category'].value_counts().to_dict()
        otif_total = float(sum(otif_dict.values()))

        ontime = otif_dict['14 Days or Less']/otif_total

        value = dat2['Item Value'].sum()

        del dat2
        dat2 = dat.copy()


        pattern = '|'.join(reporting_period)
        dat2['KPI 2 PE Turnaround month'] = dat2['KPI 2 PE Turnaround month'].fillna('')
        dat2 = dat2[dat2['KPI 2 PE Turnaround month'].str.contains(pattern)]

        dat2 = dat2.drop_duplicates('PE#')

        #dat2['KPI 2 PE Turnaround month'] = dat2['KPI 2 PE Turnaround month'].fillna('')
        #dat2 = dat2[dat2['KPI 2 PE Turnaround month']!='']

        #print dat2['pe_turnaround']
        #print dat2['pe_turnaround'].isnull().sum()



        kpi_2_list = list(dat2['pe_turnaround'])
        kpi_2_list = [x for x in kpi_2_list if str(x) != 'nan']

        kpi_2_list = list(filter(str, kpi_2_list)) # fastest
        pe_turnaround =  np.median(kpi_2_list)
        pe_to_list = dat2.shape[0]

        del dat2
        dat2 = dat.copy()

        pattern = '|'.join(reporting_period)
        dat2['KPI 3 PO Turnaround month'] = dat2['KPI 3 PO Turnaround month'].fillna('')
        dat2 = dat2[dat2['KPI 3 PO Turnaround month'].str.contains(pattern)]

        dat2 = dat2.drop_duplicates('Order#')
        #print dat2.shape
        #for index, row in dat2.iterrows():
        #    print row['po_turnaround'], type(row['po_turnaround'])



        kpi_3_list = list(dat2['po_turnaround'])
        kpi_3_list = [x for x in kpi_3_list if str(x) != 'nan']

        kpi_3_list = list(filter(str, kpi_3_list)) # fastest
        po_turnaround =  np.median(kpi_3_list)
        po_to_list = dat2.shape[0]

        print('############################## KPI OUTPUTS ##############################')
        print 'date: ' + str(time.strftime("%b %d, %Y"))
        print reporting_period
        print matrix_file
        print
        print("OTIF: %.4f%%" % (ontime * 100) + " or " + str(otif_dict['14 Days or Less']) + ' out of ' + str(otif_total) + " target >= 85%")
        print
        print("PE Turnaround: " + str(pe_turnaround) + " target <= 3 days" + " N=" + str(pe_to_list))
        print
        print("PO Turnaround: " + str(po_turnaround) + " target <= 7 days" + " N=" + str(po_to_list))
        print
        print('Value of items this month is '+str(value))
        print('############################## KPI OUTPUTS ##############################')

        otif_final.append(str(ontime * 100)+'%')
        ontime_number.append(otif_dict['14 Days or Less'])
        otif_total_list.append(otif_total)
        pe_time.append(pe_turnaround)
        pe_num.append(pe_to_list)
        po_time.append(po_turnaround)
        po_num.append(po_to_list)
        value_list.append(value)
    dat_kpi = pd.DataFrame({'Reporting period': months,'OTIF Percent':otif_final,'# ontime orders':ontime_number,
                           'total number of orders KPI 1':otif_total_list,'pe turnaround':pe_time,'number of PEs':pe_num,
                           'po turnaround':po_time,'number of POs': po_num,'month value':value_list})

    cols = ['Reporting period','OTIF Percent','# ontime orders','total number of orders KPI 1','pe turnaround',
            'number of PEs','po turnaround','number of POs','month value']
    dat_kpi = dat_kpi[cols]
    return dat_kpi


cats = generate_individual_kpi_numbers_nonppm(dat2, months= ['2017-01','2017-02','2017-03','2017-04','2017-05'])

cats.to_csv(save_loc+matrix_file+'_kpi_outputs_aggregated.csv',index=False)

