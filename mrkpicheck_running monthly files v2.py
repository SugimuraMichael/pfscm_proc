########################################################################################################################

'''
8/10 readability changes, updated imports, commented out unused functions

Thiis file is used to run a series of function which were created to automate much of the regular analysis that PMU
conducts.

you need to change settings, set the data files to point it to, and the save location fot the files


'''
#def run_kpis(matrix_file, dat, reporting_yr_month,save_loc,save_name,save_yes_no= 'yes'):

import pandas as pd
import mrkpicheck.full_file_kpis as full_file

from mrkpicheck.data_set_checker_v3 import compare_padcors
from mrkpicheck.checking_blank_fields import check_for_blanks
from mrkpicheck.data_cleaning import replace_SCMS
from mrkpicheck.outlier_checks import do_the_thing

import numpy as np

#from mrkpicheck.kpis import run_kpis
#from mrkpicheck.checkingduplicates_v2 import check_incomplete_duplicates
#from mrkpicheck.Checking_blanks_v2 import pe_po
#from mrkpicheck.lsu_vipd_request import vipd_checks_vs_po_create

import os.path
import os
import time
#doesnt change
MC_directory = 'C:/Users/585000/Desktop/PCFSM/2017 KPIs/'

### USE PAD COR not pad cor ppm
matrix_file = 'PAD COR 8_9_17'
#matrix_file = 'PAD COR 7_13_17_test_environment'
dat = pd.read_csv(MC_directory + matrix_file+'.csv')

#old_dat= pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/final submissions/Predictive Analysis Dataset_COR_March 2017_pulled 4-13 (1).csv')
#old_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 5_05_17.csv')

#
#old_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 5_11_17.csv')
old_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 7_14_17.csv')
new_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 8_9_17.csv')
#if old dataset was one submitted to GF after may 2017 then need to replace SCMS with PO in new one
old_dat = replace_SCMS(old_dat)
new_dat = replace_SCMS(new_dat)

version='8_9'
month = 'July'

#OPTIONS
save_yes_no = 'yes'
#KPIs
reporting_period = '2017-07'
#checking supply
comparison_date = '06/06/2017'
supply_period = '2017'
#comparing pad cors
compare_reporting_order_month = ['2017-01','2017-02','2017-03','2017-04','2017-05','2017-06']
Monday = 'yes'
#PE PO
pe_po_period  = '2017'

save_loc = 'C:/Users/585000/Desktop/PCFSM/monthly reporting files/'+month+'/'+version+'/'
#save names
save_name = "KPIs_2_V2_"+matrix_file+version+'.csv'
compare_save_name = "change_tracker_"+matrix_file+version+'.xlsx'
supply_save_name = 'kpi_and_supplier_checks_'+matrix_file+version+'.xlsx'
blank_save_name = 'Checking_blanks_'+matrix_file+version+'.xlsx'
checking_vipd_po = matrix_file+version+'_VIFD_report.xlsx'
outlier_file = 'Outliers_'+matrix_file+version+'.xlsx'


if not os.path.exists(save_loc):
    os.makedirs(save_loc)

if os.path.isfile(save_loc+save_name) == False:
    #all this does is replace scms with po...
    dat2 = replace_SCMS(dat)

    dat2 = full_file.run_kpis(matrix_file, dat, reporting_period, save_loc, save_name, save_yes_no=save_yes_no,TGF = 'Yes')


if os.path.isfile(save_loc+save_name) == True:

    print 'hello world'
    dat2 = pd.read_csv(save_loc+save_name)

start_timez = time.time()


print '############################## KPIS ##############################'
print

#generate_individuals can handle any number of periods,
#cats = full_file.generate_individual_kpi_numbers(dat2, months= ['2017-01','2017-02','2017-03','2017-04','2017-05'],matrix_file = matrix_file)
#runtime .092 seconds for 1 month
#currently just setting it to do one month set by reporting month


kpi_dat = full_file.generate_individual_kpi_numbers(dat2, months= [reporting_period],matrix_file = matrix_file)

#for a full period, people ask frequently
kpi_dat.to_csv(save_loc+matrix_file+'_kpi_outputs_aggregated.csv',index=False)

print
print "Generating KPIs for one specific month (Months = reporting_period)"
full_file.generate_total_kpi(dat2, months= [reporting_period],matrix_file=matrix_file)

print
print "Generating KPIs for longer period of time Change months as needed"
full_file.generate_total_kpi(dat2, months= ['2017-01','2017-02','2017-03','2017-04','2017-05','2017-06'],matrix_file=matrix_file)


just_kpis = full_file.generate_just_kpi_period_dataset(dat2, months=[reporting_period])
#adding new file to mark outliers for kpi 1-5
print
print 'generate outlier files, this is based off of a dataframe of just KPI rows'
do_the_thing(just_kpis,save_loc=save_loc,save_name=outlier_file)

just_kpis.to_csv(save_loc+matrix_file+'_just_kpi_rows.csv',index=False)

#print '############################## Duplicates ##############################'

#check_incomplete_duplicates(dat, period = supply_period)

print '############################## Old vs New ##############################'

compare_padcors(old_dat,new_dat,save_loc,compare_save_name,compare_reporting_order_month)

print '############################## Supplier Fields for LSU ##############################'

check_for_blanks(dat,comparison_date,supply_save_name,save_loc,period = supply_period,reporting_period=reporting_period)

#print '############################## VIPD_Checks  ##############################'
#vipd_checks_vs_po_create(dat,comparison_date,save_loc,checking_vipd_po)

print("total time --- %s seconds ---" % (time.time() - start_timez))
print '############################## Done ##############################'


