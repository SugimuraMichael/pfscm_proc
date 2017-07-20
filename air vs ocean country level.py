import pandas as pd
import numpy as np



#doesnt change
directory = 'C:/Users/585000/Desktop/PCFSM/2017 KPIs/'
#ADJUST: monthy_year
#month_year_file = 'april 2017/'
#ADJUST: FILE NAME

### USE PAD COR not pad cor ppm
matrix_file = 'PAD COR 7_10_17.csv'

save_loc = 'C:/Users/585000/Desktop/PCFSM/cost_saving/'
dat = pd.read_csv(directory+matrix_file)



#qtr must be given in a 01 02 03 04 format. or it could handle a list of them
def calc_rates(dat,year,qtr='all'):
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

    dat = dat[dat['year'] == str(year)]



    #2016
    country_list = ['Mozambique', 'Tanzania', 'Uganda', 'Nigeria', 'Malawi', 'Ghana',
                    'Zimbabwe', 'Zambia', 'Guinea', "C\xf4te d'Ivoire"]

    #2015
    #country_list = ['Mozambique', 'Tanzania', 'Uganda', 'Nigeria', 'Malawi', 'Ghana', 'Cameroon',
    #                    'Zimbabwe', 'Zambia', "C\xf4te d'Ivoire"]

    pattern = '|'.join(country_list)
    dat['Ship To Country Name'] = dat['Ship To Country Name'].fillna('')
    dat = dat[dat['Ship To Country Name'].str.contains(pattern)]


    # will subset down to only the quarter in question, if the qtr is set to all... then it will take
    # all 4 qtrs... aka this part wont be run.
    # if a value for qtr is set, then it will do the normal pattern thing... and since it is after
    # it has been filtered for country and year, it means it should just be the entries which match, all 3 criteria
    if qtr != 'all':
        pattern = '|'.join(qtr)

        dat['qtr'] = dat['Order Last Delivery Recorded Qtr'].str[-2:]
        dat['qtr'] = dat['qtr'].fillna('')
        dat = dat[dat['qtr'].str.contains(pattern)]

    #dat = pd.DataFrame(dat.groupby(['Ship To Country Name'])['FB Weight',
    #                                 ].sum().reset_index())

    #result = dat.sort(['FB Weight'], ascending=[0])
    #result.head(10)

    '''
    Method:
    subset to a time/subset of lanes/countries
    Calculate Freight Cost per Kilo (FCPK) for every lane within a time period, compare time periods to see costs
    using the different FCPK to get a comparison,


    '''

    dat = pd.DataFrame(
        dat.groupby(['Ship To Country Name', 'Order Pick Up Country Name', 'Shipment Mode','Client INCO Term'])['FB Weight',
                                                                                             'FB Allocated Freight',
                                                                                             'FB Demurrage',
                                                                                             'FB Mod Fda'].sum().reset_index())

    dat['freight cost per kilo'] = (dat['FB Allocated Freight'] - (
        dat['FB Demurrage'] + dat['FB Mod Fda'])) / dat['FB Weight']


    return dat


dat_2015 = calc_rates(dat,2015)
dat_2016 = calc_rates(dat,2016)

dat_2017 = calc_rates(dat,2017,['01'])


dat_2017['id'] =dat_2017['Ship To Country Name']+ dat_2017['Order Pick Up Country Name']+ dat_2017['Shipment Mode'] +dat_2017['Client INCO Term']
dat_2016['id'] =dat_2016['Ship To Country Name']+ dat_2016['Order Pick Up Country Name']+ dat_2016['Shipment Mode']+dat_2016['Client INCO Term']
#dat_2015['id'] =dat_2015['Ship To Country Name']+ dat_2015['Order Pick Up Country Name']+ dat_2015['Shipment Mode']+dat_2015['Client INCO Term']

#>>> df.rename(index=str, columns={"A": "a", "B": "c"})

dat_2016 = dat_2016.rename(index=str, columns={'FB Weight':'FB Weight_16', 'FB Allocated Freight':'FB Allocated Freight_16',
                                    'FB Demurrage':'FB Demurrage_16', 'FB Mod Fda':'FB Mod Fda_16',
                                    'freight cost per kilo':'freight cost per kilo_16'})

#dat_2015 = dat_2015.rename(index=str, columns={'FB Weight':'FB Weight_15', 'FB Allocated Freight':'FB Allocated Freight_15',
#                                    'FB Demurrage':'FB Demurrage_15', 'FB Mod Fda':'FB Mod Fda_15',
#                                    'freight cost per kilo':'freight cost per kilo_15'})
dat_2017 = dat_2017.rename(index=str, columns={'FB Weight':'FB Weight_17', 'FB Allocated Freight':'FB Allocated Freight_17',
                                    'FB Demurrage':'FB Demurrage_17', 'FB Mod Fda':'FB Mod Fda_17',
                                    'freight cost per kilo':'freight cost per kilo_17'})

result = pd.merge(dat_2017,dat_2016,on='id',how='left')

result.drop(['Ship To Country Name_y', 'Order Pick Up Country Name_y','Shipment Mode_y'], axis=1, inplace=True)

#dat.drop(['slicer_1','Ta0'], axis=1, inplace=True)
#result = pd.merge(result,dat_2015,on='id',how='left')

#result.drop(['Ship To Country Name','Order Pick Up Country Name','Shipment Mode'], axis = 1, inplace=True)


#                                            2016 rate                      2017 total weight
result['2017 w 2016 rates'] = result['freight cost per kilo_16'] * result['FB Weight_17'] #gives cost to ship current stuff w/ 2016 rates
result['2016 w 2017 rates'] = result['freight cost per kilo_17'] * result['FB Weight_16']

#What it would cost to ship what PFSCM has shipped in 2017 using 2016 rates, as compared to what it actually cost. Positive number is savings
result['allocated fright delta 2017w2016 rates minus actual 2017'] = result['2017 w 2016 rates'] - (result['FB Allocated Freight_17'] -(result['FB Demurrage_17'] + result['FB Mod Fda_17']))
# if this is a positive number, it means it costs more to ship things with last year's rates
#What it would cost to ship what PFSCM has shipped in 2017 using 2016 rates, as compared to what it actually cost. Positive number is savings
#What it would cost to ship what PFSCM shipped in 2016 using 2017 as compared to what it cost in 2016. Negative number shows savings
result['allocated fright delta 2016w2017 rates minus actual 2016'] = result['2016 w 2017 rates'] - (result['FB Allocated Freight_16'] -(result['FB Demurrage_16'] + result['FB Mod Fda_16']))


# if this is a negative number, it means that this years costs are higher

result = result[np.isfinite(result['allocated fright delta 2016w2017 rates minus actual 2016'])]
#result = result[np.isfinite(result['allocated fright delta 2015w2017 rates minus actual 2015'])]
result.to_csv(save_loc+'7_10 2017_Q1_cost savings.csv')

'''

'''
 #2017 vs 2015
'''

result_17v15 = pd.merge(dat_2017,dat_2015,on='id',how='left')
result_17v15.drop(['Ship To Country Name_y', 'Order Pick Up Country Name_y','Shipment Mode_y'], axis=1, inplace=True)


result_17v15['2017 w 2015 rates'] = result_17v15['freight cost per kilo_15'] * result_17v15['FB Weight_17'] #gives cost to ship current stuff w/ 2016 rates
result_17v15['2015 w 2017 rates'] = result_17v15['freight cost per kilo_17'] * result_17v15['FB Weight_15']


result_17v15['allocated fright delta 2017w2015 rates minus actual 2017'] = result_17v15['2017 w 2015 rates'] - (result_17v15['FB Allocated Freight_17'] -(result_17v15['FB Demurrage_17'] + result_17v15['FB Mod Fda_17']))
result_17v15['allocated fright delta 2015w2017 rates minus actual 2015'] = result_17v15['2015 w 2017 rates'] - (result_17v15['FB Allocated Freight_15'] -(result_17v15['FB Demurrage_15'] + result_17v15['FB Mod Fda_15']))

result_17v15 = result_17v15[np.isfinite(result_17v15['allocated fright delta 2015w2017 rates minus actual 2015'])]

result_17v15_clone =  result_17v15[result_17v15['Shipment Mode_x']=="Ocean"]


result_17v15.to_csv('C:/Users/585000/Desktop/PCFSM/rate_checkv2015_all.csv')

mode_test = pd.DataFrame(
    result_17v15.groupby(['Shipment Mode_x'])['FB Weight_17','FB Weight_15'].sum().reset_index())

weight17 = mode_test['FB Weight_17'].sum()
weight15 = mode_test['FB Weight_15'].sum()

mode_test['perc_breakdown_17'] = mode_test['FB Weight_17']/weight17
mode_test['perc_breakdown_15'] = mode_test['FB Weight_15']/weight15




directory = 'C:/Users/585000/Desktop/PCFSM/2017 KPIs/'




# checking all


zzz = pd.DataFrame(
    dat_2016.groupby(['Ship To Country Name']).size().reset_index())



'''
#broader lanes
'''

import pandas as pd
import numpy as np



def calc_rates(dat,year):
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
    dat = dat[dat['year'] == str(year)]

    #2016
    country_list = ['Mozambique', 'Tanzania', 'Uganda', 'Nigeria', 'Malawi', 'Ghana',
                    'Zimbabwe', 'Zambia', 'Guinea', "C\xf4te d'Ivoire"]

    #2015
    #country_list = ['Mozambique', 'Tanzania', 'Uganda', 'Nigeria', 'Malawi', 'Ghana', 'Cameroon',
    #                    'Zimbabwe', 'Zambia', "C\xf4te d'Ivoire"]

    pattern = '|'.join(country_list)
    dat['Ship To Country Name'] = dat['Ship To Country Name'].fillna('')
    dat = dat[dat['Ship To Country Name'].str.contains(pattern)]

    #dat = pd.DataFrame(dat.groupby(['Ship To Country Name'])['FB Weight',
    #                                 ].sum().reset_index())

    #result = dat.sort(['FB Weight'], ascending=[0])
    #result.head(10)


    dat = pd.DataFrame(
        dat.groupby(['Ship To Country Name', 'Order Pick Up Country Name','Shipment Mode','Client INCO Term'])['FB Weight',
                                                                                             'FB Allocated Freight',
                                                                                             'FB Demurrage',
                                                                                             'FB Mod Fda'].sum().reset_index())

    dat['freight cost per kilo'] = (dat['FB Allocated Freight'] - (
        dat['FB Demurrage'] + dat['FB Mod Fda'])) / dat['FB Weight']


    return dat


dat_2015 = calc_rates(dat,2015)
dat_2017 = calc_rates(dat,2017)
dat_2016 = calc_rates(dat,2016)

dat_2017['id'] =dat_2017['Ship To Country Name']+ dat_2017['Shipment Mode']
dat_2016['id'] =dat_2016['Ship To Country Name']+ dat_2016['Shipment Mode']

dat_2015['id'] =dat_2015['Ship To Country Name']+ dat_2015['Order Pick Up Country Name']+ dat_2015['Shipment Mode']

#>>> df.rename(index=str, columns={"A": "a", "B": "c"})

dat_2016 = dat_2016.rename(index=str, columns={'FB Weight':'FB Weight_16', 'FB Allocated Freight':'FB Allocated Freight_16',
                                    'FB Demurrage':'FB Demurrage_16', 'FB Mod Fda':'FB Mod Fda_16',
                                    'freight cost per kilo':'freight cost per kilo_16'})

dat_2015 = dat_2015.rename(index=str, columns={'FB Weight':'FB Weight_15', 'FB Allocated Freight':'FB Allocated Freight_15',
                                    'FB Demurrage':'FB Demurrage_15', 'FB Mod Fda':'FB Mod Fda_15',
                                    'freight cost per kilo':'freight cost per kilo_15'})
dat_2017 = dat_2017.rename(index=str, columns={'FB Weight':'FB Weight_17', 'FB Allocated Freight':'FB Allocated Freight_17',
                                    'FB Demurrage':'FB Demurrage_17', 'FB Mod Fda':'FB Mod Fda_17',
                                    'freight cost per kilo':'freight cost per kilo_17'})

#result = pd.merge(dat_2017,dat_2016,on='id',how='left')

result.drop(['Ship To Country Name_y', 'Shipment Mode_y'], axis=1, inplace=True)
#dat.drop(['slicer_1','Ta0'], axis=1, inplace=True)
#result = pd.merge(result,dat_2015,on='id',how='left')

#result.drop(['Ship To Country Name','Order Pick Up Country Name','Shipment Mode'], axis = 1, inplace=True)


#                                            2016 rate                      2017 total weight
result['2017 w 2016 rates'] = result['freight cost per kilo_16'] * result['FB Weight_17'] #gives cost to ship current stuff w/ 2016 rates
result['2016 w 2017 rates'] = result['freight cost per kilo_17'] * result['FB Weight_16']

#What it would cost to ship what PFSCM has shipped in 2017 using 2016 rates, as compared to what it actually cost. Positive number is savings
result['allocated fright delta 2017w2016 rates minus actual 2017'] = result['2017 w 2016 rates'] - (result['FB Allocated Freight_17'] -(result['FB Demurrage_17'] + result['FB Mod Fda_17']))
# if this is a positive number, it means it costs more to ship things with last year's rates
#What it would cost to ship what PFSCM has shipped in 2017 using 2016 rates, as compared to what it actually cost. Positive number is savings
#What it would cost to ship what PFSCM shipped in 2016 using 2017 as compared to what it cost in 2016. Negative number shows savings
result['allocated fright delta 2016w2017 rates minus actual 2016'] = result['2016 w 2017 rates'] - (result['FB Allocated Freight_16'] -(result['FB Demurrage_16'] + result['FB Mod Fda_16']))


# if this is a negative number, it means that this years costs are higher

result = result[np.isfinite(result['allocated fright delta 2016w2017 rates minus actual 2016'])]
#result = result[np.isfinite(result['allocated fright delta 2015w2017 rates minus actual 2015'])]
country_list = ['Mozambique', 'Tanzania', 'Uganda', 'Nigeria', 'Malawi', 'Ghana',
                'Zimbabwe', 'Zambia', 'Guinea', "C\xf4te d'Ivoire"]

slicer = 0
for index, row in dat_2016.iterrows():
    if row['Ship To Country Name'] in country_list:
        dat_2016.loc[index,'slicer'] = 1
    else:
        dat_2016.loc[index, 'slicer'] = 0
dat_2016.to_csv('C:/Users/585000/Desktop/PCFSM/rate_2016_all_v2.csv')







#######################################################


dat_main = pd.read_excel('C:/Users/585000/Desktop/PCFSM/thing for wesley.xlsx')

dat_2 = pd.read_excel('C:/Users/585000/Desktop/PCFSM/thing2.xlsx')

dat_main['id'] = dat_main['Ship To Country']+dat_main['Order Pick Up Country']+dat_main['Shipment Mode']+dat_main['Client INCO Term']
dat_2['id'] = dat_2.id+dat_2['Client INCO Term_y']

result = pd.merge(dat_main,dat_2,on='id',how='left')
result.to_excel('C:/Users/585000/Desktop/PCFSM/thing4.xlsx')

'''