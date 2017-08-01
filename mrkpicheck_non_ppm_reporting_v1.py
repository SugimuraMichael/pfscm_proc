########################################################################################################################

'''
Thiis file is used to run a series of function which were created to automate much of the regular analysis that PMU
conducts.

you need to change settings, set the data files to point it to, and the save location fot the files


'''
#def run_kpis(matrix_file, dat, reporting_yr_month,save_loc,save_name,save_yes_no= 'yes'):

import pandas as pd
import numpy as np
from mrkpicheck.kpis import run_kpis
from mrkpicheck.checkingduplicates_v2 import check_incomplete_duplicates
from mrkpicheck.data_set_checker_v3 import compare_padcors
from mrkpicheck.checking_blank_fields import check_for_blanks
#from mrkpicheck.Checking_blanks_v2 import pe_po
from mrkpicheck.lsu_vipd_request import vipd_checks_vs_po_create
from mrkpicheck.data_cleaning import replace_SCMS
import mrkpicheck.full_file_kpis as full_file



import os.path
import os
import time
#doesnt change
MC_directory = 'C:/Users/585000/Desktop/PCFSM/2017 KPIs/'

### USE PAD COR not pad cor ppm
matrix_file = 'program_id PADCOR merge_3'
#matrix_file = 'PAD COR 7_13_17_test_environment'
dat = pd.read_csv(MC_directory + matrix_file+'.csv')

#old_dat= pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/final submissions/Predictive Analysis Dataset_COR_March 2017_pulled 4-13 (1).csv')
#old_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 5_05_17.csv')

#
#old_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 5_11_17.csv')
old_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/Predictive Analysis Dataset - COR May 2017 Analysis_pulled 06-14 (1).csv')
new_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 7_14_17.csv')
#if old dataset was one submitted to GF after may 2017 then need to replace SCMS with PO in new one
old_dat = replace_SCMS(old_dat)
new_dat = replace_SCMS(new_dat)

version='proj_id_v3'
month = 'test_non_ppm'

#OPTIONS
save_yes_no = 'yes'
#KPIs
reporting_period = '2017-06'
#checking supply
comparison_date = '06/06/2017'
supply_period = '2017'
#comparing pad cors
compare_reporting_order_month = ['2017-01','2017-02','2017-03','2017-04','2017-05']
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


if not os.path.exists(save_loc):
    os.makedirs(save_loc)

if os.path.isfile(save_loc+save_name) == False:
    #all this does is replace scms with po...
    dat2 = replace_SCMS(dat)

    c = full_file.run_kpis(matrix_file, dat, reporting_period, save_loc, save_name, save_yes_no=save_yes_no,TGF = 'no')


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

full_list_for_non_ppm_test = ['2016-01','2016-02','2016-03','2016-04','2016-05','2016-06','2016-07','2016-08','2016-09',
 '2016-10','2016-11','2016-12','2017-01','2017-02','2017-03','2017-04','2017-05','2017-06']

kpi_dat = full_file.generate_individual_kpi_numbers(dat2, months= full_list_for_non_ppm_test,matrix_file = matrix_file)

#for a full period, people ask frequently
kpi_dat.to_csv(save_loc+matrix_file+'_kpi_outputs_aggregated.csv',index=False)

supplier_list = ['Janssen','Gilead','Malaria Consortium','MOH of Dom Republic']

for supplier in supplier_list:
    dat3 = dat2.copy()
    dat3 =dat3[dat3['Managed By']==supplier]
    kpi_dat = full_file.generate_individual_kpi_numbers(dat3, months=full_list_for_non_ppm_test,
                                                        matrix_file=matrix_file)
    kpi_dat.to_csv(save_loc + matrix_file +"_" +supplier+'_kpi_outputs_aggregated.csv', index=False)

full_file.generate_total_kpi(dat2, months= full_list_for_non_ppm_test,matrix_file=matrix_file)


full_file.generate_total_kpi(dat2, months= ['2017-01','2017-02','2017-03','2017-04','2017-05'],matrix_file=matrix_file)


just_kpis = full_file.generate_just_kpi_period_dataset(dat2, months=[reporting_period])

just_kpis.to_csv(save_loc+matrix_file+'_just_kpi_rows.csv',index=False)
