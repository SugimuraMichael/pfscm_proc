'''
File to generate freight cost per kilo based freight savings.

2 functions
calc rates breaks down to a subsection of commonly used countries... this can be adjusted to widen or narrow analysis
and sums up the fb booked value, demurage and moh fees and weight per lane. Lane is defined as ship from and ship to countries,
mode, and inco term.

calculate_savings runs calc rates and compares 2 periods. usually set as 2 years and defaults to comparing 2016 to
2017. outputs some statistics, but also a dataset which is essentially a long one... to graph or plot you could groupby
This seemed like the better thing to do rather than looking at a very wide dataset.

'''
import pandas as pd
import numpy as np



#doesnt change
directory = 'C:/Users/585000/Desktop/PCFSM/2017 KPIs/'
#ADJUST: monthy_year
#month_year_file = 'april 2017/'
#ADJUST: FILE NAME

### USE PAD COR not pad cor ppm
matrix_file = 'PAD COR 7_14_17.csv'

save_loc = 'C:/Users/585000/Desktop/PCFSM/cost_saving/'
dat = pd.read_csv(directory+matrix_file)



#qtr must be given in a 01 02 03 04 format. or it could handle a list of them
#period_type qtr or month. basically what kind of breakdown you want to make it by
def calc_rates(dat,year,period_type = 'all'):
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
    #could modify this to take in a list of strings and do the pattern type seach that I normally use
    # that would allow for analysis of multiple years at once
    dat = dat[dat['year'] == str(year)]



    #2016 #defined by top countries in 2016 for comparison
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

    if period_type == 'qtr':
        dat['Order Last Delivery Recorded Qtr'] = dat['Order Last Delivery Recorded Qtr'].fillna('')
        dat = dat[dat['Order Last Delivery Recorded Qtr']!='']

        dat = pd.DataFrame(
            dat.groupby(['Order Last Delivery Recorded Qtr','Ship To Country Name', 'Order Pick Up Country Name', 'Shipment Mode', 'Client INCO Term'])[
                'FB Weight',
                'FB Allocated Freight',
                'FB Demurrage',
                'FB Mod Fda'].sum().reset_index())

        dat['freight cost per kilo'] = (dat['FB Allocated Freight'] - (
            dat['FB Demurrage'] + dat['FB Mod Fda'])) / dat['FB Weight']

        dat['id'] = dat['Ship To Country Name'] + dat['Order Pick Up Country Name'] + dat[
            'Shipment Mode'] + dat['Client INCO Term']

        dat = dat.rename(index=str,
                         columns={'FB Weight': 'FB Weight_' + str('qtr'),
                                  'FB Allocated Freight': 'FB Allocated Freight_' + str('qtr'),
                                  'FB Demurrage': 'FB Demurrage_' + str('qtr'),
                                  'FB Mod Fda': 'FB Mod Fda_' + str('qtr'),
                                  'freight cost per kilo': 'freight cost per kilo_' + str('qtr')})

    if period_type == 'month':
        dat['Order Last Delivery Recorded Year - Month'] = dat['Order Last Delivery Recorded Year - Month'].fillna('')
        dat = dat[dat['Order Last Delivery Recorded Year - Month']!='']

        dat = pd.DataFrame(
            dat.groupby(['Order Last Delivery Recorded Year - Month','Ship To Country Name', 'Order Pick Up Country Name', 'Shipment Mode', 'Client INCO Term'])[
                'FB Weight',
                'FB Allocated Freight',
                'FB Demurrage',
                'FB Mod Fda'].sum().reset_index())

        dat['freight cost per kilo'] = (dat['FB Allocated Freight'] - (
            dat['FB Demurrage'] + dat['FB Mod Fda'])) / dat['FB Weight']

        dat['id'] = dat['Ship To Country Name'] + dat['Order Pick Up Country Name'] + dat[
            'Shipment Mode'] + dat['Client INCO Term']

        dat = dat.rename(index=str,
                         columns={'FB Weight': 'FB Weight_' + str('month'),
                                  'FB Allocated Freight': 'FB Allocated Freight_' + str('month'),
                                  'FB Demurrage': 'FB Demurrage_' + str('month'),
                                  'FB Mod Fda': 'FB Mod Fda_' + str('month'),
                                  'freight cost per kilo': 'freight cost per kilo_' + str('month')})



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
    if period_type == 'all':

        dat = pd.DataFrame(
            dat.groupby(['Ship To Country Name', 'Order Pick Up Country Name', 'Shipment Mode','Client INCO Term'])['FB Weight',
                                                                                                 'FB Allocated Freight',
                                                                                                 'FB Demurrage',
                                                                                                 'FB Mod Fda'].sum().reset_index())

        dat['freight cost per kilo'] = (dat['FB Allocated Freight'] - (
            dat['FB Demurrage'] + dat['FB Mod Fda'])) / dat['FB Weight']

        dat['id'] = dat['Ship To Country Name'] + dat['Order Pick Up Country Name'] + dat[
            'Shipment Mode'] + dat['Client INCO Term']


        dat = dat.rename(index=str,
                                   columns={'FB Weight': 'FB Weight_'+str(year), 'FB Allocated Freight': 'FB Allocated Freight_'+str(year),
                                            'FB Demurrage': 'FB Demurrage_'+str(year), 'FB Mod Fda': 'FB Mod Fda_'+str(year),
                                            'freight cost per kilo': 'freight cost per kilo_'+str(year)})
    return dat



# calculate savings using some base comparison year, defaults to 2016 and then some comparison year, 2017 in this case
# can modify the way that it subsets so that analysis could be done outside of 2017
def calculate_savings(dat,base_year = 2016,comparison_year = 2017,comparison_period='all'):
    dat_2016 = calc_rates(dat, base_year)

    dat_2017_qtr = calc_rates(dat, comparison_year, comparison_period)

    result = pd.merge(dat_2017_qtr,dat_2016,on='id',how='left')

    result.drop(['Ship To Country Name_y', 'Order Pick Up Country Name_y','Shipment Mode_y','Client INCO Term_y'], axis=1, inplace=True)

    base_year = str(base_year)
    comparison_year = str(comparison_year)
    if comparison_period == 'all':
        comparison_period = comparison_year
    #                                            2016 rate                      2017 total weight
    result[comparison_year+' w '+base_year+' rates'] = result['freight cost per kilo_'+base_year] * result['FB Weight_'+comparison_period] #gives cost to ship current stuff w/ 2016 rates
    #result['2016 w 2017 rates'] = result['freight cost per kilo_17'] * result['FB Weight_16']

    #What it would cost to ship what PFSCM has shipped in 2017 using 2016 rates, as compared to what it actually cost. Positive number is savings
    result['allocated fright delta '+ comparison_year+'w'+base_year+' rates minus actual 2017'] = result[comparison_year+' w '+base_year+' rates'] - (result['FB Allocated Freight_'+comparison_period] -(result['FB Demurrage_'+comparison_period] + result['FB Mod Fda_'+comparison_period]))

    result = result[np.isfinite(result['allocated fright delta '+ comparison_year+'w'+base_year+' rates minus actual 2017'])]

    print
    print 'overall value'
    print ' Note: a positive value means savings since we are comparing what it would have costs to ship 2017 volumnes with 2016 fcpk'
    print result['allocated fright delta ' + comparison_year + 'w' + base_year + ' rates minus actual 2017'].sum()
    print
    print 'brokendown by period'
    print result.groupby([list(result.columns)[0]])['allocated fright delta '+ comparison_year+'w'+base_year+' rates minus actual 2017'].sum()
    print

    return result

test1 = calculate_savings(dat,base_year = 2016,comparison_year = 2017,comparison_period='qtr')


save_loc = 'C:/Users/585000/Desktop/PCFSM/cost_saving/'
test1.to_csv(save_loc+'savings_'+matrix_file,index=False)
