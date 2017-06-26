'''
Check 2 pad cor datasets to check if monthly KPI related things have changed

relevant fields are
D1, CPPD #order last recorded delivery changes? need to figure out how to check

PE Turn around
    PE response date
    PE actionable date

PO
    PE sent to vendor date
    PQ actionable

Vendor confirmed date != NA
    must have VFP and VPDD

'''
directory = 'C:/Users/585000/Desktop/PCFSM/'

from workdays import networkdays
import time
from datetime import datetime
#import datetime
import pandas as pd
import numpy as np

#from modified folder
#old is what we use as "truth" bc we are looking to see what has changed

#Jan
#old_dat= pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/final submissions/Predictive Analysis Dataset_COR_January 2017_pulled 2-14.csv')
#Predictive Analysis Dataset_COR_February 2017_pulled 3-16 (1).csv
#Febuary
#old_dat= pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/final submissions/Predictive Analysis Dataset_COR_February 2017_pulled 3-16 (1).csv')
#March
#old_dat= pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/final submissions/Predictive Analysis Dataset_COR_March 2017_pulled 4-13 (1).csv')

#old_dat= pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 4_12_17.csv')
#new is the newest dataset we are vetting
old_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 5_05_17.csv')
new_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 5_11_17.csv')



#ASN-39613
#period that old dat applies to

def compare_padcors(old_dat,new_dat,reporting_order_month = ['2017-01','2017-02','2017-03']):
    reporting_order_month = reporting_order_month

    for month in reporting_order_month:
        DATE_TO_COMPARE = '05/05/2017'
        #                                                CHANGE THIS
        VPD_comparison_date = datetime.strptime(DATE_TO_COMPARE, "%m/%d/%Y").date()


        month_kpi = month[-2:]
        year_kpi = month[:4]

        #old dat
        old_dat['Ta0'] = 0
        for index, row in old_dat.iterrows():
            a = str(row['Project Code'])
            a = a[-3:]
            if a == 'TA0':
                old_dat.loc[index, 'Ta0'] = 1

        old_dat = old_dat[old_dat['Ta0'] == 0]
        old_dat.drop(['Ta0'], axis=1, inplace=True)

        old_dat = old_dat[old_dat['Client Type'] != 'NGF']
        old_dat = old_dat[old_dat['Managed By - Project']!= 'SCMS']
        old_dat = old_dat[old_dat['Order Short Closed'] != "Yes"]
        #new dat
        new_dat['Ta0'] = 0
        for index, row in new_dat.iterrows():
            a = str(row['Project Code'])
            a = a[-3:]
            if a == 'TA0':
                new_dat.loc[index, 'Ta0'] = 1
        new_dat = new_dat[new_dat['Ta0'] == 0]
        new_dat.drop(['Ta0'], axis=1, inplace=True)
        new_dat = new_dat[new_dat['Client Type'] != 'NGF']
        new_dat = new_dat[new_dat['Managed By - Project']!= 'SCMS']
        new_dat = new_dat[new_dat['Order Short Closed'] != "Yes"]

        old_dat['Order Last Delivery Recorded Year - Month'].isnull().sum()
        old_dat['Order Last Delivery Recorded Year - Month']=old_dat['Order Last Delivery Recorded Year - Month'].fillna("NANNN")
        old_dat['KPI 1 OTIF'] = np.where(old_dat['Order Last Delivery Recorded Year - Month'].str.contains(month),1,0)


        new_dat['Order Last Delivery Recorded Year - Month'].isnull().sum()
        new_dat['Order Last Delivery Recorded Year - Month']=new_dat['Order Last Delivery Recorded Year - Month'].fillna("NANNN")
        new_dat['KPI 1 OTIF'] = np.where(new_dat['Order Last Delivery Recorded Year - Month'].str.contains(month),1,0)

        print
        print 'currently looking at ' + month
        print "OTIF old vs new " + str(old_dat['KPI 1 OTIF'].sum()) +" : " + str(new_dat['KPI 1 OTIF'].sum())
        print
        print "OTIF old breakdown: "
        print old_dat['COTD Category'][old_dat['KPI 1 OTIF']==1].value_counts()
        print
        print "OTIF new breakdown: "
        print new_dat['COTD Category'][new_dat['KPI 1 OTIF']==1].value_counts()

        old_dat['KPI 2 PE Turnaround'] = 0
        old_dat['KPI 3 PO Turnaround'] = 0
        new_dat['KPI 2 PE Turnaround'] = 0
        new_dat['KPI 3 PO Turnaround'] = 0

        # build dictionaries to check values
        otif_cpdd_dict = {}
        otif_d1_dict = {}
        po_dict_sent_to_vendor = {}
        po_dict_pq_actionable = {}
        pe_dict_response = {}
        pe_dict_pe_actionable = {}

        print 'old'
        for index, row in old_dat.iterrows():
            d = str(row['PE Response Date'])
            d2 = str(row['PO Sent to Vendor Date'])
            in_pe = int(row['KPI 2 PE Turnaround'])

            pe_num = str(row['PE#'])
            in_po = int(row['KPI 3 PO Turnaround'])
            po_num = str(row['Order#'])
            asn = str(row['Shipment#'])
            if d != 'nan':
                #print d
                d = datetime.strptime(d, "%m/%d/%Y")
                if d.strftime("%m, %Y") == month_kpi + ', ' + year_kpi:

                    if pe_num not in pe_dict_response:
                        old_dat.loc[index, 'KPI 2 PE Turnaround'] = 1

                        ## ADD TO TWO PE RELATED DICTIONARIES
                        pe_dict_response[pe_num] = row['PE Response Date']
                        pe_dict_pe_actionable[pe_num] = row['PE Actionable Date']

            if d2 != 'nan':
                #print d2
                d2 = datetime.strptime(d2, "%m/%d/%Y")
                if d2.strftime("%m, %Y") == month_kpi + ', ' + year_kpi:

                    if po_num not in po_dict_sent_to_vendor:
                        old_dat.loc[index, 'KPI 3 PO Turnaround'] = 1

                        ## ADD TO TWO RELATED PO DICTIONARIES
                        po_dict_sent_to_vendor[po_num] = row['PO Sent to Vendor Date']
                        po_dict_pq_actionable[po_num] = row['PQ Actionable Date']

            otif_flag = str(row['KPI 1 OTIF'])
            if otif_flag == '1':

                otif_cpdd_dict[asn] = row['Client Promised Delivery Date']
                otif_d1_dict[asn] =row['Shipment Delivered Date']


        ### GATHER NEW DAT
        #d = '1/18/2017'
        #d = datetime.strptime(d, "%m/%d/%Y")
        #d.strftime("%m, %Y") == month_kpi + ', ' + year_kpi


        # build dictionaries to check values
        neo_otif_cpdd_dict = {}
        neo_otif_d1_dict = {}

        neo_po_dict_sent_to_vendor = {}
        neo_po_dict_pq_actionable = {}
        neo_pe_dict_response = {}
        neo_pe_dict_pe_actionable = {}
        print 'new'

        for index, row in new_dat.iterrows():
            d = str(row['PE Response Date'])
            d2 = str(row['PO Sent to Vendor Date'])
            in_pe = int(row['KPI 2 PE Turnaround'])

            pe_num = str(row['PE#'])
            in_po = int(row['KPI 3 PO Turnaround'])
            po_num = str(row['Order#'])
            asn = str(row['Shipment#'])
            if d != 'nan':
                d = datetime.strptime(d, "%m/%d/%Y")
                if d.strftime("%m, %Y") == month_kpi + ', ' + year_kpi:
                    # build dictionaries to check values



                    if pe_num not in neo_pe_dict_response:
                        new_dat.loc[index, 'KPI 2 PE Turnaround'] = 1

                        ## ADD TO TWO PE RELATED DICTIONARIES
                        neo_pe_dict_response[pe_num] = row['PE Response Date']
                        neo_pe_dict_pe_actionable[pe_num] = row['PE Actionable Date']

            if d2 != 'nan':
                d2 = datetime.strptime(d2, "%m/%d/%Y")
                if d2.strftime("%m, %Y") == month_kpi + ', ' + year_kpi:

                    if po_num not in neo_po_dict_sent_to_vendor:
                        new_dat.loc[index, 'KPI 3 PO Turnaround'] = 1

                        ## ADD TO TWO RELATED PO DICTIONARIES
                        neo_po_dict_sent_to_vendor[po_num] = row['PO Sent to Vendor Date']
                        neo_po_dict_pq_actionable[po_num] = row['PQ Actionable Date']

            otif_flag = str(row['KPI 1 OTIF'])
            if otif_flag == '1':

                neo_otif_cpdd_dict[asn] = row['Client Promised Delivery Date']
                neo_otif_d1_dict[asn] =row['Shipment Delivered Date']

        print
        print "PE old vs new " + str(old_dat['KPI 2 PE Turnaround'].sum()) +" : " + str(new_dat['KPI 2 PE Turnaround'].sum())
        print "PO old vs new " + str(old_dat['KPI 3 PO Turnaround'].sum()) +" : " + str(new_dat['KPI 3 PO Turnaround'].sum())


        # pull out examples to check
        #otif_new = pd.DataFrame(new_dat)
        #otif_old = pd.DataFrame(old_dat)

        #PO_new = pd.DataFrame(new_dat)
        #PO_old = pd.DataFrame(old_dat)

        #PO_new = PO_new[PO_new['KPI 3 PO Turnaround'] == 1]
        #PO_old = PO_old[PO_old['KPI 3 PO Turnaround'] == 1]

        #PO_old = pd.DataFrame(PO_old[['Order#','PO Sent to Vendor Date']])
        #combined_po = pd.merge(PO_new,PO_old,how='left',on='Order#',indicator=True)

        #combined_po.to_csv(directory+'PO differences 3_15 to feb dataset.csv')



        #should be the same POs in both

        full_otif_list = []
        for asn in neo_otif_cpdd_dict:
            if asn not in full_otif_list:
                full_otif_list.append(asn)
        for asn in otif_cpdd_dict:
            if asn not in full_otif_list:
                full_otif_list.append(asn)

        full_po_list = []
        for po in neo_po_dict_sent_to_vendor:
            if po not in full_po_list:
                full_po_list.append(po)
        for po in po_dict_sent_to_vendor:
            if po not in full_po_list:
                full_po_list.append(po)

        full_pe_list = []

        for pe in neo_pe_dict_response:
            if pe not in full_pe_list:
                full_pe_list.append(pe)
        for pe in pe_dict_response:
            if pe not in full_pe_list:
                full_pe_list.append(pe)

        differences =  pd.DataFrame()
        # tell you which ones are missing in one but not the other
        print
        print 'Missing in either new or old dataset'


        #cpDD
        print 'Missing Client promised delivery date:'
        missing_otif = []
        for po in full_otif_list:
            if po not in neo_otif_cpdd_dict:
                print 'PO missing in new dataset: '+str(po) +" in old has Client promised delivery date of "+str(otif_cpdd_dict[po])
                missing_otif.append(po)
            if po not in otif_cpdd_dict:
                print 'PO missing in old dataset: '+str(po) +" in new has Client promised delivery date of "+str(neo_otif_cpdd_dict[po])
                missing_otif.append(po)

        print 'Missing D1 Date:'
        missing_d1 = []
        for po in full_otif_list:
            if po not in neo_otif_d1_dict:
                print 'PO missing in new dataset: '+str(po) +" in old has D1 Date of "+str(otif_d1_dict[po])
                missing_d1.append(po)
            if po not in otif_d1_dict:
                print 'PO missing in old dataset: '+str(po) +" in new has D1 Date of "+str(neo_otif_d1_dict[po])
                missing_d1.append(po)
        print
        print 'Missing PE response:'
        #neo_pe_dict_pe_actionable
        #                pe_dict_pe_actionable
        missing_pe = []
        for pe in full_pe_list:
            if pe not in neo_pe_dict_response:
                print 'PE missing in new dataset: '+str(pe) +" in old has PE response date of "+str(pe_dict_response[pe])
                missing_pe.append(pe)

            if pe not in pe_dict_response:
                print 'PE missing in old dataset: '+str(pe) +" in new has PE response date of "+str(neo_pe_dict_response[pe])
                missing_pe.append(pe)


        print
        print 'Missing PE Actionable: '
        missing_pe_actionable = []
        for pe in full_pe_list:
            if pe not in neo_pe_dict_pe_actionable:
                print 'PE missing in new dataset: '+str(pe) +" in old has PE Actionable date of "+str(pe_dict_pe_actionable[pe])
                missing_pe_actionable.append(pe)

            if pe not in pe_dict_pe_actionable:
                print 'PE missing in old dataset: '+str(pe) +" in new has PE Actionable date of "+str(neo_pe_dict_pe_actionable[pe])
                missing_pe_actionable.append(pe)

        print
        print 'Missing Po sent to vendor:'
        missing_po = []
        for po in full_po_list:
            if po not in neo_po_dict_sent_to_vendor:
                print 'PO missing in new dataset: '+str(po) +" in old has Po sent to vendor date of "+str(po_dict_sent_to_vendor[po])
                missing_po.append(po)
            if po not in po_dict_sent_to_vendor:
                print 'PO missing in old dataset: '+str(po) +" in new has Po sent to vendor date of "+str(neo_po_dict_sent_to_vendor[po])
                missing_po.append(po)
        print
        print 'Missing Po PQ actionable:'

        missing_po_pq_action = []
        for po in full_po_list:
            if po not in neo_po_dict_pq_actionable:
                print 'PO missing in new dataset: '+str(po) +" in old has PQ actionable date of "+str(po_dict_pq_actionable[po])
                missing_po_pq_action.append(po)
            if po not in po_dict_pq_actionable:
                print 'PO missing in old dataset: '+str(po) +" in new has PQ actionable date of "+str(neo_po_dict_pq_actionable[po])
                missing_po_pq_action.append(po)

        ##############################################################

        print
        print "Changes: "
        print 'Client promised delivery date:'
        for asn in full_otif_list:
            new = ''
            old = ''
            #print asn
            if asn in neo_otif_cpdd_dict:
                new = str(neo_otif_cpdd_dict[asn])
            if asn in otif_cpdd_dict:
                old = str(otif_cpdd_dict[asn])
            #if asn == 'ASN-53321':
            #    print 'oh hey'
            #    print new, old
            #print new, old
            if new != old:
                if asn not in missing_otif:
                    print 'New dataset ' +str(asn)+' = '+ new + " and old dataset "+str(asn)+" = " + old

        print 'D1 date: '
        for asn in full_otif_list:
            new = ''
            old = ''
            if asn in neo_otif_d1_dict:
                new = str(neo_otif_d1_dict[asn])
            if asn in otif_d1_dict:
                old = str(otif_d1_dict[asn])
            #print new, old
            if new != old:
                if asn not in missing_d1:
                    print 'New dataset ' +str(asn)+' = '+ new + " and old dataset "+str(asn)+" = " + old


        print 'PE Response:'
        for pe in full_pe_list:
            new = ''
            old = ''

            if pe in neo_pe_dict_response:
                new = str(neo_pe_dict_response[pe])
            if pe in pe_dict_response:
                old = str(pe_dict_response[pe])
            #print new, old
            if new != old:
                if pe not in missing_pe:
                    print 'New dataset ' +str(pe)+' = '+ new + " and old dataset "+str(pe)+" = " + old
        print
        print 'PE Actionable:'
        for pe in full_pe_list:
            new = ''
            old = ''

            if pe in neo_pe_dict_pe_actionable:
                new = str(neo_pe_dict_pe_actionable[pe])
            if pe in pe_dict_pe_actionable:
                old = str(pe_dict_pe_actionable[pe])
            #print new, old
            if new != old:
                if pe not in missing_pe_actionable:
                    print 'New dataset ' +str(pe)+' = '+ new + " and old dataset "+str(pe)+" = " + old

        print
        print 'Po sent to vendor:'
        for po in full_po_list:
            new = ''
            old = ''
            if po in neo_po_dict_sent_to_vendor:
                new = str(neo_po_dict_sent_to_vendor[po])
            if po in po_dict_sent_to_vendor:
                old = str(po_dict_sent_to_vendor[po])
            #print new, old
            if new != old:
                if po not in missing_po:
                    print 'New dataset ' +str(po)+' = '+ new + " and old dataset "+str(po)+" = " + old

                #print 'PO missing in old dataset: '+str(po) +" in new has value of "+str(neo_po_dict_sent_to_vendor[po])

        print
        print 'Po PQ actionable:'

        for po in full_po_list:
            new = ''
            old = ''
            if po in neo_po_dict_pq_actionable:
                new = str(neo_po_dict_pq_actionable[po])
            if po in po_dict_pq_actionable:
                old = str(po_dict_pq_actionable[po])
            #print new, old
            if new != old:
                if po not in missing_po_pq_action:
                    print 'New dataset ' +str(po)+' = '+ new + " and old dataset "+str(po)+" = " + old


        print 'Supplier Information'
        '''
        need to check to see if the supplier information is present in the new dataset. and then see if it changed
        as compared to the old dataset... FUN
        '''





        print 'END'


