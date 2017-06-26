README file for mrkpicheck
Notes: a lot of these could be combined into one file with a long list of functions.

as of 6/21/17

checking_blank_fields.py: 
	function check_for_blanks(dat=PAD_COR,save_name=file name,save_loc=file path,period=time period string, defaults to 2017)
		
    purpose: 
			1) check supplier related fields: Vendor Promised date
			Vendor Inco Fulfilment date, PO Sent to Vendor date, and Order Created Date
				A) Looks for incomplete fields and some basic patterns which may indicate incomplete fields

			2) PO Turnaround KPI Checks: PO Sent date and PQ Actionable Date
				A) if a PO Sent date is in a given period, then check to
				see if the PQ actionable date is blank, if so, flag it.

			3) PE Turnaround KPI checks:  PE Response date (used to set
			a given period) and measured using PE Actionable and PE Sent Date
				A) Check for blanks in PE Actionable and PE Sent dates

		Output: 
			Excel file with 3 tabs. One for each section. Duplicates
			between the supplier checks and the PO turnaround checks are removed due to lots of duplication between them

		notes: 
			1) This file is very "noisy". Since we are looking for incomplete data fields it is difficult to determine what is missing because it has not been recieved, or things that are legitimately missing. long term goal should be to reduce noise.

			2) File determines period by concatinating the previous milestone dates and looking for ones which fall into a given period. period variable sets supplier performance checks, idea being we are looking for ones appearing in 2017. the reporting period variable is whatever month (yyyy-mm) we are in given as a string

checkingduplicates_v2.py:
	function check_incomplete_duplicates(input_dat=PAD_COR,period=['list of dates']):
	
		purpose: 
			looking for potential duplication within the PAD COR dataset. One issue here is that further testing is needed to try and detect duplicates... this file will need to be reworked. 

			subsets to period using strategy similar to checking_blank_fields.py 

			then performs a groupby based on Order number and PE# and gets the unique count of values for each. if the value is greater than 1 it means that there are potential duplicates.
		Output:
			currently just prints out things
		notes:
			Need to test further...


data_cleaning.py:
	function replace_SCMS(PAD_COR_DATASET or line item dataset):

		purpose: 
			replace 'SCMS' with 'PO' in the datasets, returns a dataset where just that has been changed
		Output:
			returns dataset where only SCMS and PO have been swapped
		Notes: 
			This is just a replace all operation

data_set_chekcer_v3.py:
	function compare_padcors(old_dat =PAD_COR, new_dat = PAD_COR, reporting_order_month = [list of date strings])

		purpose: 
			compare two PAD COR datasets and check for changes in changes of POs, ASNs and reporting details for the 3 KPIs. it is looking for rows which appear in one but not the other, or for rows which now have a different number of rows than before. idea is that we need to report to the global fund when there are changes in previously reported periods... ideally this should not be occuring but since it is observed to happen we need to check for it.

		old_dat: 
			previous PAD COR, typically a PAD COR which was submitted to the global fund in the previous month

		new_dat: 
			can be anything, but typically use the most recent PAD COR in order to see the differences.

		reporting_order_month: 
			list of month strings defaults to the first quarter of 2017 ['2017-01','2017-02','2017-03'], but can be whatever you need/choose. 

		output:
			excel file. gets marked by error type, I also include the "parent row" (basically the version of that row that ends in 0) so operations can see the parent to determine what is happening with the "child" row 

			(unsure what those are actually called by the operations teams)

full_file_kpis.py:
	function 1) run_kpis(matrix_file, dat, reporting_yr_month,save_loc,save_name,save_yes_no= 'yes')

		purpose: create a marked dataset that can be used by other functions here to perform PAD COR KPI calculations. previous versions performed the calculations on smaller sections of the dataset... but this can be run once and then calculations can be done quickly on that file. sub .1 second. Initial calculation time is around 1 minute to generate the file though. so there is a tradeoff, but you can just reference the output of this function. 

		matrix_file: 
			string that has the name of the file... just used to display later on so this is an artifact that can be removed

		dat: 
			PAD COR dataset to be marked up

		save_loc, save_name: 
			where to save the file to and what name you would like it to have, strings

		save_yes_no: 
			defaults to yes and just saves the file if you so choose. this is so you can reference it later rather than rerunning


		Output: a dataset which has additional columns for KPI calculations

		Notes: can likely be optimized since this is an intial version of this calculation


	function 2) generate_individual_kpi_numbers(dat, months= ['2017-05'],matrix_file = '')

		purpose: calculate the KPIs for a given period of time and show each units KPI numbers. for example if you want each of the months in Q1 it would be ['2017-01','2017-02','2017-03']. The function will calculate the KPIs for each month and print them out. It will also create an aggregated dataset for the KPIs so that overall figures can be seen/recoreded. One issue is that KPI performance changes overtime as operations teams request/make changes

		dat: 
			marked PAD COR dataset that has been passed through run_kpis()

		months: 
			some list of strings to denote period. for specific months it would have to be in the structure YYYY-MM. however YYYY would also work

		matrix_file: 
			just to display in output so that the date of the file can be seen.... an astethic 

		Output: 
			aggregated dataset that shows at whatever level was fed into the months variable

	function 3) generate_total_kpi(dat, months= ['2017-01','2017-02','2017-03'],matrix_file='')

		purpose: 
			calculate the KPI values for a period of time, it provides the aggregated values. computationally is almost identical to generate_individual_kpi_numbers()

		dat:
			marked PAD COR dataset that has been passed through run_kpis()

		months:
			some list of strings to denote period. for specific months it would have to be in the structure YYYY-MM. however YYYY would also work

		matrix_file: 
			just to display in output so that the date of the file can be seen.... an astethic 

		Output: 
			none

		Notes: 
			this is a calculation that is often asked, and without it it is tiring to calculate so why not just make a function. 

	function 4) generate_just_kpi_period_dataset(dat, months=['2017-01', '2017-02', '2017-03'])

		purpose: 
			subset the main dataset output from run_kpis(), it is useful because it is easier to see the particular data for a month and look into issues that may appear, blank values, negative PO turnaround times, missing FLT vs PLt calculations. So this is to make checking into the data easier

		dat: 
			marked PAD COR dataset that has been passed through run_kpis()

		months: 
			some list of strings to denote period. for specific months it would have to be in the structure YYYY-MM. however YYYY would also work

		Output: 
			dataset marked for rows which fall into which KPIs which can be used to take manual looks into the data. 

lsu_vipd_requests.py

	function 1) vipd_checks_vs_po_create(dat2,DATE_TO_COMPARE,save_loc='',save_name='')

		purpose: 
			experimental report for LSU looking at the export doc reciept dates (also notes as Vendor Inco Fulfilment date in datasets) to see that it is not blank and then checks to see that the Order Create Date to see that if the export doc reciept date is older than 3 days (set as a hard coded value in the function as N)

		dat2: 
			PAD COR dataset
		






