import pandas as pd
import numpy as np
import time
from workdays import networkdays
from datetime import datetime


#doesnt change
directory = 'C:/Users/585000/Desktop/PCFSM/2017 KPIs/'
#ADJUST: monthy_year
#month_year_file = 'april 2017/'
#ADJUST: FILE NAME

### USE PAD COR not pad cor ppm
matrix_file = 'PAD COR 4_17_17.csv'
dem_per_day = 100
dat = pd.read_csv(directory+matrix_file)

# switched PE and PO to use days_between function rather than business days:
def business_days_between(d1, d2):
    d1 = datetime.strptime(d1, "%m/%d/%Y")
    d2 = datetime.strptime(d2, "%m/%d/%Y")
    return networkdays(d1, d2)

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%m/%d/%Y")
    d2 = datetime.strptime(d2, "%m/%d/%Y")
    return (d2 - d1).days


def calc_rates(dat,years = ['2017']):
    dat['Ta0'] = 0
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
    dat = dat[dat['Current Shipment Milestone'] == 'D1']

    dat['year'] = dat['Delivery Recorded Year - Month'].str[:4]
    pattern = '|'.join(years)
    dat['year'] = dat['year'].fillna('')
    dat = dat[dat['year'].str.contains(pattern)]
    #dat = dat[dat['year'] == str(year)]

    country_dict = {'Kenya':17,'Ghana':14,'Tanzania':17,'Nigeria':21}
    print dat.shape

    dat_sub = pd.DataFrame()
    for key in country_dict:
        #print key
        dat2 = dat.copy()
        dat2 = dat2[dat2['Ship To Country Name']== key]
        dat2['free_days'] = country_dict[key]
        #print dat2.shape
        dat_sub = dat_sub.append(dat2,ignore_index=True)
        del dat2
    dat = dat_sub.copy()
    del dat_sub
    #2016
    #country_list = ['Mozambique', 'Tanzania', 'Uganda', 'Nigeria', 'Malawi', 'Ghana',
    #                'Zimbabwe', 'Zambia', 'Guinea', "C\xf4te d'Ivoire"]

    #2015
    #country_list = ['Mozambique', 'Tanzania', 'Uganda', 'Nigeria', 'Malawi', 'Ghana', 'Cameroon',
    #                    'Zimbabwe', 'Zambia', "C\xf4te d'Ivoire"]

    #pattern = '|'.join(country_list)
    #dat['Ship To Country Name'] = dat['Ship To Country Name'].fillna('')
    #dat = dat[dat['Ship To Country Name'].str.contains(pattern)]

    #dat = pd.DataFrame(dat.groupby(['Ship To Country Name'])['FB Weight',
    #                                 ].sum().reset_index())

    #result = dat.sort(['FB Weight'], ascending=[0])
    #result.head(10)


    # IMPORT DATES
    '''
    Import Waiver Requested Date
    Import Waiver Received Date

    CUSTOMS
    Shipment Arrived at Port Date
    D1
    '''

    dat['Import Waiver Requested Date'] = dat['Import Waiver Requested Date'].fillna('')
    dat['Import Waiver Received Date'] = dat['Import Waiver Received Date'].fillna('')
    dat['Shipment Arrived at Port Date'] = dat['Shipment Arrived at Port Date'].fillna('')
    dat['Delivery Recorded Date'] = dat['Delivery Recorded Date'].fillna('')

    dat['waiver_time'] = 0
    dat['customs'] = 0
    dat['dem_avoided'] = 0
    dat['cost_w_free_days'] = 0
    for index, row in dat.iterrows():
        waiver_req = row['Import Waiver Requested Date']
        waiver_rec = row['Import Waiver Received Date']

        port = row['Shipment Arrived at Port Date']
        d1 = row['Delivery Recorded Date']
        waiver_time = 0
        customs = 0
        if waiver_rec != '' and waiver_req != '':
            waiver_time = days_between(waiver_req,waiver_rec)
            dat.loc[index,'waiver_time'] = waiver_time
        if port != '' and d1 != '':
            customs = days_between(port,d1)
            # subtracting 3 because assuming 3 days for delivery
            dat.loc[index,'customs'] = customs - 3
        if customs != 0:
            if int(customs) > 7:
                dem_avoided = (customs - 7) * 250
                dat.loc[index,'dem_avoided'] = dem_avoided
            if customs > row['free_days']:

                dat.loc[index,'cost_w_free_days'] = (customs - row['free_days'])*250
    agg_funcs = {'FB Weight': [np.sum,np.size], 'waiver_time': np.mean,'customs': np.mean,'dem_avoided':np.sum,
                 'cost_w_free_days': np.sum}

    dat = pd.DataFrame(
        dat.groupby(['Ship To Country Name', 'Order Pick Up Country Name', 'Shipment Mode']).agg(agg_funcs).reset_index().reset_index())

    dat2 = pd.DataFrame()
    dat2['Ship To Country Name'] = dat['Ship To Country Name']
    dat2['Order Pick Up Country Name'] = dat['Order Pick Up Country Name']
    dat2['Shipment Mode'] = dat['Shipment Mode']
    dat2['FB Weight_sum'] = dat['FB Weight']['sum']
    dat2['FB Weight_N'] = dat['FB Weight']['size']
    dat2['waiver_time_mean'] = dat['waiver_time']
    dat2['customs_mean'] = dat['customs']
    dat2['dem_avoided'] = dat['dem_avoided']
    dat2['cost_w_free_days'] = dat['cost_w_free_days']
    dat2['net_cost_avoided'] = dat['dem_avoided'] - dat['cost_w_free_days']

    dat2['waiver_time_mean'] = dat2['waiver_time_mean'].fillna('')
    dat2['customs_mean'] = dat2['customs_mean'].fillna('')
    for index, row in dat2.iterrows():
        waiver = row['waiver_time_mean']
        customs = row['customs_mean']
        if waiver == '' and customs == '':
            dat2.loc[index,'without_preemptive_waivers'] = 0

        if waiver == '' and customs != '':
            dat2.loc[index,'without_preemptive_waivers'] = float(customs)
        if waiver != '' and customs == '':
            dat2.loc[index,'without_preemptive_waivers'] = float(waiver)
        if waiver != '' and customs != '':
            dat2.loc[index,'without_preemptive_waivers'] = float(customs) + float(waiver)

    #dat2['without_preemptive_waivers'] = dat2['waiver_time_mean']+dat2['customs_mean']

    del dat
    return dat2



#at = dat[dat['Ship To Country Name']=='Nigeria']
dat_2016 = calc_rates(dat,['2016','2017'])

#pd.DataFrame([dat_2016['Shipment Mode'],dat_2016['FB Weight']['size']])
#dat_2017 = calc_rates(dat,2017)

dat_2016.to_csv('C:/Users/585000/Desktop/PCFSM/dem_savings_2016_v6_w_costs.csv')
#dat_2017.to_csv('C:/Users/585000/Desktop/PCFSM/dem_savings_2017_v1.csv')

