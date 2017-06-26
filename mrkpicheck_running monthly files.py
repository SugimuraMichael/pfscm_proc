import pandas as pd
import numpy as np
from mrkpicheck.kpis import run_kpis
from mrkpicheck.checkingduplicates_v2 import check_incomplete_duplicates
from mrkpicheck.data_set_checker_v3 import compare_padcors
from mrkpicheck.checking_blank_fields import check_for_blanks
from mrkpicheck.Checking_blanks_v2 import pe_po
from mrkpicheck.lsu_vipd_request import vipd_checks_vs_po_create
from mrkpicheck.data_cleaning import replace_SCMS

import os
import time
#doesnt change
MC_directory = 'C:/Users/585000/Desktop/PCFSM/2017 KPIs/'

### USE PAD COR not pad cor ppm
matrix_file = 'PAD COR 6_19_17'
dat = pd.read_csv(MC_directory + matrix_file+'.csv')

#old_dat= pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/final submissions/Predictive Analysis Dataset_COR_March 2017_pulled 4-13 (1).csv')
#old_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 5_05_17.csv')
old_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 5_11_17.csv')
new_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 6_19_17.csv')


version='_v12'
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
Monday = 'no'
#PE PO
pe_po_period  = '2017'

save_loc = 'C:/Users/585000/Desktop/PCFSM/monthly reporting files/'+month+'/'+version+'/'
#save names
save_name = "KPIs_"+matrix_file+version+'.csv'
compare_save_name = "change_tracker_"+matrix_file+version+'.xlsx'
supply_save_name = 'kpi_and_supplier_checks_'+matrix_file+version+'.xlsx'
blank_save_name = 'Checking_blanks_'+matrix_file+version+'.xlsx'
checking_vipd_po = matrix_file+version+'_VIFD_report.xlsx'

if not os.path.exists(save_loc):
    os.makedirs(save_loc)

start_time = time.time()

dat = replace_SCMS(dat)

print '############################## KPIS ##############################'
print

run_kpis(matrix_file,dat,reporting_period,save_loc,save_name,save_yes_no = save_yes_no)

print '############################## Duplicates ##############################'

check_incomplete_duplicates(dat, period = supply_period)

print '############################## Old vs New ##############################'

compare_padcors(old_dat,new_dat,save_loc,compare_save_name,compare_reporting_order_month)

print '############################## Supplier Fields for LSU ##############################'

check_for_blanks(dat,comparison_date,supply_save_name,save_loc,period = supply_period,reporting_period=reporting_period)

#print '############################## Potential missing PE POs ##############################'
#redundant, added into the check for blanks function above 5/26
#pe_po(dat,blank_save_name,save_loc,period = pe_po_period)

#def vipd_checks_vs_po_create(dat2,DATE_TO_COMPARE,Monday='yes',save_loc='',save_name=''):
print '############################## VIPD_Checks  ##############################'
vipd_checks_vs_po_create(dat,comparison_date,save_loc,checking_vipd_po)

print("--- %s seconds ---" % (time.time() - start_time))
print '############################## Done ##############################'
