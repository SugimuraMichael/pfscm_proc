
'''
calculate dem savings for uganda since it has a diff setup
19,000 per month for a warehouse,

also takes into account air vs ocean... and calculates savings....


'''
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


def calc_uganda_warehouse_savings(dat,warehouse_cost = 19000, years = ['2017']):
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

    unique_months = dat['Delivery Recorded Year - Month'].nunique()

    dat = dat[dat['Ship To Country Name'] == 'Uganda']

    #mode = 'Ocean|Air'
    #dat = dat[dat['Shipment Mode'].str.contains(mode)]
    #print dat['Shipment Mode'].value_counts()
    dat['Import Waiver Requested Date'] = dat['Import Waiver Requested Date'].fillna('')
    dat['Import Waiver Received Date'] = dat['Import Waiver Received Date'].fillna('')
    dat['Shipment Arrived at Port Date'] = dat['Shipment Arrived at Port Date'].fillna('')
    dat['Delivery Recorded Date'] = dat['Delivery Recorded Date'].fillna('')
    dat['FB Weight'] = dat['FB Weight'].fillna(0)

    dat['waiver_time'] = 0
    dat['customs'] = 0
    dat['dem_cost_hypothetical'] = 0
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
            if row['Shipment Mode'] == 'Ocean':
                if int(customs) > 7:
                    dem_avoided = (customs - 7) * 250
                    dat.loc[index,'dem_cost_hypothetical'] = dem_avoided
            if row['Shipment Mode'] == 'AIR':
                if int(customs) > 3:
                    weight = row['FB Weight']
                    if weight == 0:
                        weight = 1
                    dem_avoided = (customs - 3) * (.03*weight)
                    #print 'air',dem_avoided
                    dat.loc[index,'dem_cost_hypothetical'] = dem_avoided



    agg_funcs = {'FB Weight': [np.sum, np.size], 'waiver_time': np.mean, 'customs': np.mean, 'dem_cost_hypothetical': np.sum,
                 }
    dat = pd.DataFrame(
        dat.groupby(['Ship To Country Name', 'Order Pick Up Country Name','Shipment Mode']).agg(
                agg_funcs).reset_index().reset_index())

    dat2 = pd.DataFrame()
    dat2['Ship To Country Name'] = dat['Ship To Country Name']
    #dat2['Order Pick Up Country Name'] = dat['Order Pick Up Country Name']
    dat2['Shipment Mode'] = dat['Shipment Mode']
    dat2['FB Weight_sum'] = dat['FB Weight']['sum']
    dat2['FB Weight_N'] = dat['FB Weight']['size']
    dat2['waiver_time_mean'] = dat['waiver_time']
    dat2['customs_mean'] = dat['customs']
    dat2['dem_cost_hypothetical'] = dat['dem_cost_hypothetical']

    warehouse_cost_total = unique_months*warehouse_cost
    dat2['warehouse costs'] = unique_months*warehouse_cost
    #dat2['net_cost_avoided'] = dat['dem_cost_hypothetical'] - unique_months*warehouse_cost
    dat2['waiver_time_mean'] = dat2['waiver_time_mean'].fillna('')
    dat2['customs_mean'] = dat2['customs_mean'].fillna('')


    del dat
    return dat2 ,warehouse_cost_total, unique_months



dd,total_warehouse,unique_months = calc_uganda_warehouse_savings(dat,years=['2016','2017'])

print 'cost avoided with Uganda warehouse is ' + str(dd['dem_cost_hypothetical'].sum() - total_warehouse)
print 'total demurrage using Air (FB weight * .03 *days over 3) and Ocean (days over 7 * 250) is '+ str(dd['dem_cost_hypothetical'].sum())
print 'total warehouse fees are ' + str(total_warehouse) + ' number of months '+ str(unique_months)

#dd['Ship To Country Name']