
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

import os
import time

#doesnt change
MC_directory = 'C:/Users/585000/Desktop/PCFSM/2017 KPIs/'

################################## SECTION THAT REQUIRES ADJUSTING ##################################
### USE PAD COR not pad cor ppm
matrix_file = 'PAD COR 8_15_17'

#Reporting period is most important to adjust... by default it is a single month. but function it feeds into
# can take multiple months at a time as a list of strings
reporting_period = '2017-07' #used in most basic kpi reporting where only 1 month of data is generated


#by default this will generally be equal to matrix_file... but can also use the compare function to look for
# differences between two PAD CORs not just for reporting purposes... can help track when changes occured within
# the system and has been periodically useful
newer_PAD_COR = matrix_file
older_PAD_COR = 'PAD COR 7_14_17' #set to be the previous reporting period dataset. in this case the submission for
                                    # june pulled on July 14 2017

dat = pd.read_csv(MC_directory + matrix_file+'.csv') #load basic dataset, PAD COR as a csv

old_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/'+older_PAD_COR+'.csv')
new_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/'+newer_PAD_COR+'.csv')

version='8_15_v2' #this sets the folder that you will save to.
                  # This script gives permission to write new folders if they do not exist
month = 'July' #Sets a parent folder. I have been saving all the runs I do for a particular month together
                # Example path PFSCM-> Monthly Reporting -> month='July'->version = XXXXX

comparison_date = '08/10/2017' #used in checking for blanks

#Used to determine whether or not code should be saved
save_yes_no = 'yes'
#KPIs
#checking supply... this is subsetting to things which occur in 2017...
# to adjust ['2017','2018'] will work... but whether that choice is made will have to be addressed by PMU
supply_period = ['2017']

#comparing pad cors.
# THIS needs to be updated monthly, so include previous months. At a certain point we can just make a function for this
# Also using this to generate aggregated total
compare_reporting_order_month = ['2017-01','2017-02','2017-03','2017-04','2017-05','2017-06']
#PE PO
save_loc = 'C:/Users/585000/Desktop/PCFSM/monthly reporting files/'+month+'/'+version+'/'

################################## Basic House Keeping ##################################

#save names
# as of now these are fairly stagnant,
save_name = "KPIs_2_V2_"+matrix_file+'.csv'
compare_save_name = "change_tracker_"+matrix_file+'.xlsx'
supply_save_name = 'kpi_and_supplier_checks_'+matrix_file+'.xlsx'
blank_save_name = 'Checking_blanks_'+matrix_file+'.xlsx'
checking_vipd_po = matrix_file+'_'+'_VIFD_report.xlsx'
outlier_file = 'Outliers_'+matrix_file+'_'+'.xlsx'

#make the directory we wills save to
if not os.path.exists(save_loc):
    os.makedirs(save_loc)

#generate a dataset that has columns for KPI calculations added to it
#this section will also generate a dataset outputed in the format for submission to TGF
# format is essentially a standard dataset with 4 extra columns.
# function full_file.run_kpis has this embededed in it. Could pull it out, but I figured it would be alright to leave
# at least for the time being.
if os.path.isfile(save_loc+save_name) == False:
    #all this does is replace scms with po...
    dat2 = replace_SCMS(dat)
    dat2 = full_file.run_kpis(matrix_file, dat, reporting_period, save_loc, save_name, save_yes_no=save_yes_no,TGF = 'Yes')

#if file has already been run, the longest thing for basic reporting is creating the marked dataset
# approximately 1min on current computer.
if os.path.isfile(save_loc+save_name) == True:

    print 'hello world'
    dat2 = pd.read_csv(save_loc+save_name)

#calling functions to replace SCMS with PO for comparison datasets
old_dat = replace_SCMS(old_dat)
new_dat = replace_SCMS(new_dat)

#timer
start_timez = time.time()

print '############################## KPIS ##############################'
print

print "Time to calculate KPIs for a specific reporting month"
                                             # USAGE NOTES READ

# First function will calculate and display the KPI totals for a given period, based off of the reporting.
# this function actually just aggregates the kpi values for a given period "months" option. By feeding it just
# the reporting_period variable placed in a list, it means it will aggregate the values for a single month.
# later a list of months is fed in to give a larger aggregated kpi output

full_file.generate_total_kpi(dat2, months= [reporting_period],matrix_file=matrix_file)

print
print "Generating dataset of aggregated KPI Months, default is to have output surpressed, but save file"
print
                                                # USAGE NOTES READ

#setting the defaul period to be same as above, but whereas the following function aggregates the results, this
# function just aims to create a dataset which can be used to look at how KPIs trend across months.
# FUTURE addition would be a quarter aggregator...? I guess...

#NOTES:
# compare_reporting_order_month+[reporting_period]
# yields ['2017-01', '2017-02', '2017-03', '2017-04', '2017-05', '2017-06', '2017-07']
#surpress option supresses KPI output, makes file output cleaner

kpi_dat = full_file.generate_individual_kpi_numbers(dat2, months= compare_reporting_order_month+[reporting_period]
                                                    ,matrix_file = matrix_file,surpress="yes")

#for a full period, people ask frequently
kpi_dat.to_csv(save_loc+matrix_file+'_kpi_outputs_aggregated.csv',index=False)



print
print "Generating KPIs for longer period of time Change months as needed"

                                                # USAGE NOTES READ

#using the list of months in compare_reporting_order_month as a base which should be everything but the most
# recent reporting month... we can just add the reporting period to it and generate a dataset of all the months.
# in this case. It means when people ask, "what was KPI performance for Q2 of 2017" you can just enter the appropriate
# months and have it calculate a total for you

#NOTES:
# compare_reporting_order_month+[reporting_period]
# yields ['2017-01', '2017-02', '2017-03', '2017-04', '2017-05', '2017-06', '2017-07']

#This will calculate aggregated KPIs, Change to calculate for a period such as a quarter. This would be represented
# with ['2017-01', '2017-02', '2017-03'] for Q1 of 2017
# instead of the current months= compare_reporting_order_month+[reporting_period]

full_file.generate_total_kpi(dat2, months= compare_reporting_order_month+[reporting_period],matrix_file=matrix_file)


print 'See save folder to see aggregated totals for given period'

                                                # USAGE NOTES READ

#setting the defaul period to be same as above, but whereas the previous function aggregates the results, this
# function just aims to create a dataset which can be used to look at how KPIs trend across months.
# FUTURE addition would be a quarter aggregator...? I guess...

just_kpis = full_file.generate_just_kpi_period_dataset(dat2, months= [reporting_period])
just_kpis.to_csv(save_loc+matrix_file+'_just_kpi_rows.csv',index=False) #save dataset

print
print 'generate outlier files, this is based off of a dataframe of just KPI rows'

                                                # USAGE NOTES READ

#this generates outlier files in an appropriate format for the KPIs, output can be uploaded to google sheets
# recommend uploading versus copy pasting because of how google sheets interprets cells missing values to the right
# as requiring merging.

# outlier file is aimed at flagging ANYTHING that does not meet the KPI criteria, so looking here will also show
# rows which are in KPI 4 but lack a value in the lead time matrix,
# Rows which do not have planned or actual costs. These are flagged if the flt_vs_plt calculated field is blank
#  this would be caused by missing planned or actual freight lead time, if planned lead time is missing, then it
#  requires it be added to the FLT matrix

do_the_thing(just_kpis,save_loc=save_loc,save_name=outlier_file) #terribly named, but it generates outliers for kpis


print '############################## Old vs New ##############################'

                                                # USAGE NOTES READ

#Comparison of PAD CORs, reccomend running after the 10th of the month "hardclose" date. The function compares
# 2 PAD COR datasets and looks for differences in previous months to determine rows which have been changed, added, etc
# the output is a list of PEs, POs, ASNs (otif) that need to be looked at to determine why they changed in past data
#   NOTE: Otif is fairly stable and it is not common to see changes in past data

#
compare_padcors(old_dat,new_dat,save_loc,compare_save_name,compare_reporting_order_month)

print '############################## Supplier Fields for LSU ##############################'

                                                # USAGE NOTES READ

#This function looks for blanks in vendor related dates, PO turnaround, and PE turnaround and tries to flag rows
# which could potentially be missing data. Signal to noise ratio on this is VERY HIGH and bears improvement overtime
# caveat is that rows which appear under vendor performance tab are not flagged again under the PO Turnaround tab
# reason is there is typically a good amount of overlap.
check_for_blanks(dat,comparison_date,supply_save_name,save_loc,period = supply_period,reporting_period=reporting_period)


print("total time --- %s seconds ---" % (time.time() - start_timez))
print '############################## Done ##############################'






