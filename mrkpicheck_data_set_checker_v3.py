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
#directory = 'C:/Users/585000/Desktop/PCFSM/'

from workdays import networkdays
import time
from datetime import datetime
#import datetime
import collections
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
#old_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 5_05_17.csv')
#new_dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/2017 KPIs/PAD COR 5_11_17.csv')



#ASN-39613
#period that old dat applies to

def compare_padcors(old_dat,new_dat,saveloc, save_name, reporting_order_month = ['2017-01','2017-02','2017-03']):
    def union(a, b):
        """ return the union of two lists """
        return list(set(a) | set(b))
    reporting_order_month = reporting_order_month
    otif_tracker = {}
    po_tracker = {}
    pe_tracker = {}

    neo_otif_tracker = {}
    neo_po_tracker = {}
    neo_pe_tracker = {}
    for month in reporting_order_month:

        print '########################## Current month is'+ month +' ########################## '
        #                                                CHANGE THIS
        #VPD_comparison_date = datetime.strptime(DATE_TO_COMPARE, "%m/%d/%Y").date()


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

                    if pe_num not in pe_tracker:
                        old_dat.loc[index, 'KPI 2 PE Turnaround'] = 1

                        ## ADD TO TWO PE RELATED DICTIONARIES
                        pe_tracker[pe_num] = month

            if d2 != 'nan':
                #print d2
                d2 = datetime.strptime(d2, "%m/%d/%Y")
                if d2.strftime("%m, %Y") == month_kpi + ', ' + year_kpi:

                    if po_num not in po_tracker:
                        old_dat.loc[index, 'KPI 3 PO Turnaround'] = 1

                        ## ADD TO TWO RELATED PO DICTIONARIES
                        po_tracker[po_num]= month

            otif_flag = str(row['KPI 1 OTIF'])
            if otif_flag == '1':
                otif_tracker[asn] = month

        ### GATHER NEW DAT
        #d = '1/18/2017'
        #d = datetime.strptime(d, "%m/%d/%Y")
        #d.strftime("%m, %Y") == month_kpi + ', ' + year_kpi


        # build dictionaries to check values

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



                    if pe_num not in neo_pe_tracker:
                        new_dat.loc[index, 'KPI 2 PE Turnaround'] = 1

                        ## ADD TO TWO PE RELATED DICTIONARIES
                        neo_pe_tracker[pe_num] = month

            if d2 != 'nan':
                d2 = datetime.strptime(d2, "%m/%d/%Y")
                if d2.strftime("%m, %Y") == month_kpi + ', ' + year_kpi:

                    if po_num not in neo_po_tracker:
                        new_dat.loc[index, 'KPI 3 PO Turnaround'] = 1

                        ## ADD TO TWO RELATED PO DICTIONARIES
                        neo_po_tracker[po_num] = month


            otif_flag = str(row['KPI 1 OTIF'])
            if otif_flag == '1':

                neo_otif_tracker[asn] = month


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
    print 'building dicts'
    full_otif_list = []

    for asn in neo_otif_tracker:
        if asn not in full_otif_list:
            full_otif_list.append(asn)
    for asn in otif_tracker:
        if asn not in full_otif_list:
            full_otif_list.append(asn)


    full_po_list = []
    for po in neo_po_tracker:
        if po not in full_po_list:
            full_po_list.append(po)
    for po in po_tracker:
        if po not in full_po_list:
            full_po_list.append(po)
    full_pe_list = []
    for pe in neo_pe_tracker:
        if pe not in full_pe_list:
            full_pe_list.append(pe)
    for pe in pe_tracker:
        if pe not in full_pe_list:
            full_pe_list.append(pe)
    # tell you which ones are missing in one but not the other
    #OTIF

    '''
    otif_grouped_old = pd.DataFrame(old_dat.groupby(['Shipment#']).aggregate({
        'Order Last Delivery Recorded Year - Month': lambda x: x.nunique(),
        'Client Promised Delivery Date': lambda x: x.nunique(),
        'Shipment Delivered Date': lambda x: x.nunique()
    }).reset_index())
    otif_grouped_new = pd.DataFrame(new_dat.groupby(['Shipment#']).aggregate({
        'Order Last Delivery Recorded Year - Month': lambda x: x.nunique(),
        'Client Promised Delivery Date': lambda x: x.nunique(),
        'Shipment Delivered Date': lambda x: x.nunique()
    }).reset_index())
    '''

    old_dat['unit'] = ''
    new_dat['unit'] = ''
    old_dat['error_type'] = ''
    new_dat['error_type'] = ''
    old_dat['error_period'] = ''
    new_dat['error_period'] = ''
    old_dat['new_v_old'] = ''
    new_dat['new_v_old'] = ''
    new_dat['comments'] = ''
    new_dat['comments'] = ''

    differences =  pd.DataFrame()
    cols = new_dat.columns.tolist()

    for asn in full_otif_list:
        otif_old_copy = old_dat.copy()
        otif_new_copy= new_dat.copy()
        #print asn
        otif_old_copy = otif_old_copy[otif_old_copy["Shipment#"]==str(asn)]
        otif_new_copy = otif_new_copy[otif_new_copy["Shipment#"]==str(asn)]

        oldm_old = otif_old_copy['Order Last Delivery Recorded Year - Month'].tolist()
        oldm_new = otif_new_copy['Order Last Delivery Recorded Year - Month'].tolist()

        oldm_bool = collections.Counter(oldm_old) == collections.Counter(oldm_new)

        cpd_old = otif_old_copy['Client Promised Delivery Date'].tolist()
        cpd_new = otif_new_copy['Client Promised Delivery Date'].tolist()
        cpd_bool = collections.Counter(cpd_old) == collections.Counter(cpd_new)

        d1_old = otif_old_copy['Shipment Delivered Date'].tolist()
        d1_new = otif_new_copy['Shipment Delivered Date'].tolist()
        d1_bool = collections.Counter(d1_old) == collections.Counter(d1_new)

        if oldm_bool == False or cpd_bool == False or d1_bool == False:
            otif_old_copy['error_type'] = 'OTIF'
            otif_new_copy['error_type'] = 'OTIF'

            if asn in otif_tracker:
                otif_old_copy['error_period'] = otif_tracker[asn]
            if asn not in otif_tracker:
                otif_old_copy['error_period'] = 'N/A'

            if asn in neo_otif_tracker:
                otif_new_copy['error_period'] = neo_otif_tracker[asn]
            if asn not in neo_otif_tracker:
                otif_new_copy['error_period'] = 'N/A'

            otif_old_copy['new_v_old'] = 'old'
            otif_new_copy['new_v_old'] = 'new'

            otif_old_copy['unit'] = asn
            otif_new_copy['unit'] = asn
            differences = differences.append(otif_old_copy)
            differences = differences.append(otif_new_copy)


    for pe in full_pe_list:
        pe_old_copy = old_dat.copy()
        pe_new_copy = new_dat.copy()

        pe_old_copy = pe_old_copy[pe_old_copy["PE#"]==str(pe)]

        pe_new_copy = pe_new_copy[pe_new_copy["PE#"]==str(pe)]

        response_old = set(pe_old_copy['PE Response Date'].tolist())
        response_old = list(response_old)
        response_new = set(pe_new_copy['PE Response Date'].tolist())
        response_new = list(response_new)

        response_bool = collections.Counter(response_old) == collections.Counter(response_new)

        action_old = set(pe_old_copy['PE Actionable Date'].tolist())
        action_old = list(action_old)

        action_new = set(pe_new_copy['PE Actionable Date'].tolist())
        action_new = list(action_new)

        action_bool = collections.Counter(action_old) == collections.Counter(action_new)

        sent_old = set(pe_old_copy['PE Sent Date'].tolist())
        sent_old = list(sent_old)
        sent_new = set(pe_new_copy['PE Sent Date'].tolist())
        sent_new = list(sent_new)
        sent_bool = collections.Counter(sent_old) == collections.Counter(sent_new)

        if response_bool == False or action_bool == False or sent_bool == False:

            pe_old_copy['error_type'] = 'PE'
            pe_new_copy['error_type'] = 'PE'

            if pe in pe_tracker:
                pe_old_copy['error_period'] = pe_tracker[pe]
            if pe not in pe_tracker:
                pe_old_copy['error_period'] = 'N/A'

            if pe in neo_pe_tracker:
                pe_new_copy['error_period'] = neo_pe_tracker[pe]
            if pe not in neo_pe_tracker:
                pe_new_copy['error_period'] = 'N/A'

            pe_old_copy['new_v_old'] = 'old'
            pe_new_copy['new_v_old'] = 'new'

            pe_old_copy['unit'] = pe
            pe_new_copy['unit'] = pe

            if pe_old_copy.empty == True:
                pe_old_copy = pd.DataFrame()
                pe_old_copy = pe_old_copy.reindex(columns=np.append(pe_old_copy.columns.values, cols))

                for i in range(1):
                    pe_old_copy.loc[i, 'new_v_old'] = 'old'
                    pe_old_copy.loc[i, 'unit'] = pe
                    pe_old_copy.loc[i, 'error_period'] = 'N/A'
                    pe_old_copy.loc[i, 'error_type'] = 'PE'

            if pe_new_copy.empty == True:
                pe_new_copy = pd.DataFrame()
                pe_new_copy = pe_new_copy.reindex(columns=np.append(pe_new_copy.columns.values, cols))
                for i in range(1):
                    pe_new_copy.loc[i, 'new_v_old'] = 'new'
                    pe_new_copy.loc[i, 'unit'] = pe
                    pe_new_copy.loc[i, 'error_period'] = 'N/A'
                    pe_new_copy.loc[i, 'error_type'] = 'PE'

            differences = differences.append(pe_old_copy)
            differences = differences.append(pe_new_copy)


    for po in full_po_list:
        po_old_copy = old_dat.copy()
        po_new_copy = new_dat.copy()


        '''
        st =  "abcdefghij"
        st = st[:-1]
        '''
        parent = 0
        if po[-1:] != '0':
            po_parent = po[:-1]+'0'

            po_old_copy_parent = old_dat.copy()
            po_new_copy_parent = new_dat.copy()

            po_old_copy_parent = po_old_copy_parent[po_old_copy_parent['Order#'] == str(po_parent)]
            po_new_copy_parent = po_new_copy_parent[po_new_copy_parent['Order#'] == str(po_parent)]

            po_old_copy_parent['error_type'] = 'Parent PO'
            po_new_copy_parent['error_type'] = 'Parent PO'

            po_old_copy_parent['error_period'] = 'N/A'
            po_new_copy_parent['error_period'] = 'N/A'

            po_old_copy_parent['new_v_old'] = 'old'
            po_new_copy_parent['new_v_old'] = 'new'

            po_old_copy_parent['unit'] = po
            po_new_copy_parent['unit'] = po

            parent = 1

        po_old_copy = po_old_copy[po_old_copy["Order#"] == str(po)]
        po_new_copy = po_new_copy[po_new_copy["Order#"] == str(po)]



        pq_action_old = set(po_old_copy['PQ Actionable Date'].tolist())
        pq_action_old = list(pq_action_old)
        pq_action_new = set(po_new_copy['PQ Actionable Date'].tolist())
        pq_action_new = list(pq_action_new)


        pq_action_bool = collections.Counter(pq_action_old) == collections.Counter(pq_action_new)


        sent_old = set(po_old_copy['PO Sent to Vendor Date'].tolist())
        sent_old = list(sent_old)
        sent_new = set(po_new_copy['PO Sent to Vendor Date'].tolist())
        sent_new = list(sent_new)
        sent_bool = collections.Counter(sent_old) == collections.Counter(sent_new)


        if pq_action_bool == False or sent_bool == False:
            po_old_copy['error_type'] = 'PO'
            po_new_copy['error_type'] = 'PO'
            if po in po_tracker:
                po_old_copy['error_period'] = po_tracker[po]
            if po not in po_tracker:
                po_old_copy['error_period'] = 'N/A'
            if po in neo_po_tracker:
                po_new_copy['error_period'] = neo_po_tracker[po]
            if po not in neo_po_tracker:
                po_new_copy['error_period'] = 'N/A'

            po_old_copy['new_v_old'] = 'old'
            po_new_copy['new_v_old'] = 'new'
            po_old_copy['unit'] = po
            po_new_copy['unit'] = po

            if po_old_copy.empty == True:
                po_old_copy = pd.DataFrame()
                po_old_copy = po_old_copy.reindex(columns=np.append(po_old_copy.columns.values, cols))
                for i in range(1):
                    po_old_copy.loc[i,'new_v_old'] = 'old'
                    po_old_copy.loc[i,'unit'] = po
                    po_old_copy.loc[i,'error_period'] = 'N/A'
                    po_old_copy.loc[i, 'error_type'] = 'PO'

            if po_new_copy.empty == True:
                po_new_copy = pd.DataFrame()
                po_new_copy = po_new_copy.reindex(columns=np.append(po_new_copy.columns.values, cols))
                for i in range(1):
                    po_new_copy.loc[i,'new_v_old'] = 'new'
                    po_new_copy.loc[i,'unit'] = po
                    po_new_copy.loc[i,'error_period'] = 'N/A'
                    po_new_copy.loc[i, 'error_type'] = 'PO'

            if parent == 1:
                parent = pd.DataFrame()

                parent = parent.append(po_old_copy_parent)
                parent = parent.append(po_new_copy_parent)

                parent['PO Sent to Vendor Date'] = parent['PO Sent to Vendor Date'].fillna('')
                parent['PQ Actionable Date'] = parent['PQ Actionable Date'].fillna('')

                poso_ct = parent['PO Sent to Vendor Date'].nunique()
                pq_act_ct = parent['PQ Actionable Date'].nunique()

                if poso_ct == 1 and pq_act_ct == 1:
                    po_new_copy_parent = po_new_copy_parent.drop_duplicates(subset = ['Order#'])
                    differences = differences.append(po_new_copy_parent)

                if poso_ct != 1 or poso_ct != 1:
                    differences = differences.append(po_old_copy_parent)
                    differences = differences.append(po_new_copy_parent)

            differences = differences.append(po_old_copy)
            differences = differences.append(po_new_copy)

    differences = differences[cols]
    OTIF = differences[differences['error_type']=='OTIF']

    OTIF_cols = ['unit',
               'error_period',
                 'new_v_old',
                 'error_type',
                   'Grant#',
                   'Project Code',
                   'PE#',
                   'PQ#','Order#','Shipment#','Order Point of Contact','PQ Buyer'
                 ,'Sub Vendor Name','PQ Product Group','Current Shipment Milestone','Shipment Delivered Date'
                 ,'Current Planned Delivery Date','Delivery Recorded Date','Delivery Recorded Year - Month',
                 'Client Promised Delivery Date','Order Last Delivery Recorded Year - Month','COTD Category'
                 ]

    OTIF = OTIF[OTIF_cols]
    PO = differences[differences['error_type'].str.contains('PO')]

    PO_cols = ['unit',
               'error_period',
               'new_v_old',
               'error_type',
                'Grant#',
               'PE#',
               'PQ#',
               'Order#',
               'Shipment#',
               'Order Type',
               'Order Short Closed',
               'Order Point of Contact',
               'PQ Buyer',
               'PQ Product Group',
               'Managed By',
               'PR Received Date',
               'PE Create Date',
               'PE Actionable Date',
               'PE Sent Date',
               'PE Response Date',
               'PE Proceed To PQ Date',
               'PQ Create Date',
               'PQ Actionable Date',
               'PQ Proceed To PO/SO Date',
               'Order Created Date',
               'PO Sent to Vendor Date',
               'PO Vendor Confirmed Date',
               'Vendor Promised Date',
               'comments']
    PO = PO[PO_cols]

    pe_col_list = ['unit',
               'error_period',
                   'new_v_old',
                   'error_type',
                   'Grant#',
                   'Project Code',
                   'PE#',
                   'PQ#',
                   'Contract Type',
                   'PQ Buyer',
                   'PQ Product Group',
                   'PR Received Date',
                   'PR Last Submitted Date',
                   'PE Create Date',
                   'PE Actionable Date',
                   'PE Expiry Date',
                   'PE Estimate Ready Date',
                   'PE Sent Date',
                   'PE Response Date',
                   'PE Proceed To PQ Date',
                   'comments']

    PE = differences[differences['error_type']=='PE']
    PE = PE[pe_col_list]
    #saveloc, save_name,

    writer = pd.ExcelWriter(saveloc+save_name)


    readme = pd.read_csv('C:/Users/585000/Desktop/PCFSM/monthly reporting files/readme_checking_datasets.csv')
    readme.to_excel(writer, 'Readme', index=False)

    PE.to_excel(writer, 'PE Changes', index = False)
    PO.to_excel(writer, 'PO Changes', index = False)
    OTIF.to_excel(writer, 'OTIF Changes', index = False)
    writer.save()

    #return differences

        ####
        ####
        # go through each line, get the values, remove duplicates, and compared CPPD, D1, and Order last delivery month year
        # if there is a discrepency, flag it and throw it onto the new dataset
        ###
        #maybe can reuse old checking methods to flag?, would have to re add all those dictionaries

#test = compare_padcors(old_dat,new_dat)

#test.to_csv('C:/Users/585000/Desktop/PCFSM/data_report_v4.csv',index = False)