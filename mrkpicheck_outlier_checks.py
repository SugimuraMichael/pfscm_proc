import pandas as pd

import sys

reload(sys)
sys.setdefaultencoding('latin-1')

'''
write outlier files to a sheet because reasons. also boredom on a tuesday

intake a processed kpi file/dataframe, the one that has been subsetted to just the kpirows

just_kpis = full_file.generate_just_kpi_period_dataset(dat, months=[reporting_period])

reason being it will be super fast to iterate over the 7 kpis in a file of around a few hundred lines
'''

#rename to be less terrible at your leisure
def format_for_teams(dat2,kpi_num,outlier_col,reporting_cols=[]):
    dat = dat2.copy()
    main = ['Waiver Required?',
 'Grant#',
 'Project Code',
 'PE#',
 'PQ#',
 'Order#',
 'Shipment#',
 'Order Type',
 'Contract Type',
 'Client Type',
 'Order Short Closed',
 'Order Point of Contact',
 'PQ Buyer',
 'Sub Vendor Code',
 'Sub Vendor Name',
 'PQ Product Group',
 'Managed By',
 'Managed By - Project',
 'Managed By - Group',
 'DIRDRP/RDC',
 'Fulfill Via',
 'Vendor INCO Term',
 'Vendor INCO Location',
 'Client INCO Term',
 'Client INCO Location',
 'Shipment Mode',
 'Freight Forwarder',
 'Shipment Total Item Quantity',
 'Shipment Total Item Weight',
 'Shipment Total Item Volume',
 'Order Pick Up Country Code',
 'Order Pick Up Country Name',
 'Order Pick Up Country Latitude',
 'Order Pick Up Country Longitude',
 'Ship To Country Code',
 'Ship To Country Name',
 'Ship To Country Latitude',
 'Ship To Country Longitude',
 'PR Received Date',
 'PR Last Submitted Date',
 'PE Create Date',
 'PE Actionable Date',
 'PE Expiry Date',
 'PE Estimate Ready Date',
 'PE Sent Date',
 'PE Response Date',
 'PE Proceed To PQ Date',
 'PE Requested Delivery Date',
 'PQ Create Date',
 'PQ Actionable Date',
 'PQ First Submitted Date',
 'PQ First Approved Date',
 'PQ First Sent to Client Date',
 'PQ Last Sent Date',
 'PQ First Response Date',
 'PQ Last Client Response Date',
 'PQ Proceed To PO/SO Date',
 'Order Created Date',
 'PO Sent to Vendor Date',
 'PO Vendor Confirmed Date',
 'Vendor Promised Date',
 'Vendor INCO Fulfillment Date',
 'ASN/DN Created Date',
 'Shipment Last Approved Date',
 'Import Waiver Requested Date',
 'Import Waiver Received Date',
 'Shipment Documents Sent to F&L Date',
 'F&L Accepted Shipment Date',
 'Shipment Picked Up Date',
 'Shipment Shipped Date',
 'Shipment Arrived at Port Date',
 'Shipment Entered Customs Date',
 'Shipment Cleared Customs Date',
 'Current Shipment Milestone',
 'Shipment Delivered Date',
 'Current Planned Delivery Date',
 'PQ Item Req Delivery Date - Latest',
 'Delivery Recorded Date',
 'Delivery Recorded Year - Month',
 'Delivery Recorded Month',
 'Delivery Recorded Qtr',
 'Delivery Recorded Year',
 'Client Promised Delivery Date',
 'Order Last Delivery Recorded Date',
 'Order Fully Delivered?',
 'Order Last Delivery Recorded Year - Month',
 'Order Last Delivery Recorded Month',
 'Order Last Delivery Recorded Qtr',
 'Order Last Delivery Recorded Year',
 'VOTD Days Late',
 'VOTD Category',
 'COTD Days Late',
 'COTD Category',
 'Shipment Total AD Days',
 'Shipment Total UD Days',
 'Shipment Value',
 'PQ Value',
 'Order Value',
 'Pharma',
 'Emergency',
 'Confirmation of Receipt Date',
 'Complaints About Delivery']
    summary = ['Notes','PR/GF days delay',
 'Supplier days delay',
 'PFSCM days delay',
 "Root Cause Analysis (PFSCM days delay explanation)",
 'What is the Corrective Action?'
 ]
    '''
    'PE_outliers'
'PO_outliers'
    '''
    outlier = [outlier_col]

    col_list = main+reporting_cols+outlier+summary
    #def format_for_teams(dat,kpi_num,outlier_col):
    dat['Notes'] = dat[outlier_col]
    dat = dat[((dat[kpi_num] == 'Yes') & (dat[outlier_col] != 'within'))][col_list] #\
    dat = dat.drop(outlier_col, 1)

    if outlier_col == 'PE_outliers':
        dat = dat.drop_duplicates(['PE#','pe_turnaround'])

    if outlier_col == 'PO_outliers':
        dat = dat.drop_duplicates(['Order#','po_turnaround'])

    return dat


def do_the_thing(dat2,save_loc, save_name):
    dat = dat2.copy()
    #just gonna slice and dice a bunch
    #OTIF

    dat['Otif_outliers'] = 'within'
    dat['PE_outliers'] = 'within'
    dat['PO_outliers'] = 'within'
    dat['kpi4_outliers'] = 'within'
    dat['kpi5_outliers'] = 'within'
    dat['kpi6_outliers'] = 'within'
    dat['kpi7_outliers'] = 'within'
    '''
    PR/GF days delay	Supplier days delay	PFSCM days delay	"Root Cause Analysis
(PFSCM days delay explanation)"	What is the Corrective Action?
    '''
    dat['Notes'] = ''
    dat['PR/GF days delay'] = ''
    dat['Supplier days delay'] = ''
    dat['PFSCM days delay'] = ''
    dat["Root Cause Analysis (PFSCM days delay explanation)"] = ''
    dat['What is the Corrective Action?'] = ''


    for index, row in dat.iterrows():

        #evaluate for KPI 1 4 and 5
        if row['KPI 1_4_5'] == "Yes":
            if row['COTD Category'] != '14 Days or Less':
                dat.loc[index,'Otif_outliers'] = 'greater than 14 days late'

            if pd.isnull(row['flt_vs_plt']) == True:
                dat.loc[index,'kpi4_outliers'] = 'Missing N/A'
                dat.loc[index,'kpi5_outliers'] = 'Missing N/A'

            if pd.isnull(row['flt_vs_plt']) != True:

                #kpi 4
                if row['flt_vs_plt'] >.12 or row['flt_vs_plt'] < -.12:
                    flt_minus_plt = row['flt_-_plt']
                    if flt_minus_plt > 14 or flt_minus_plt < -14:
                        dat.loc[index, 'kpi4_outliers'] = 'greater than 14 days off planned lead time'

                #kpi5
                if row['flt_vs_plt'] >0:
                    dat.loc[index, 'kpi5_outliers'] = 'Actual freight leadtime > planned'

                    #else:
                    #    dat.loc[index, 'kpi4_outliers'] = 'late, but within 14 days off planned lead time'


        if row['KPI 2'] == "Yes":
            if pd.isnull(row['pe_turnaround']) == True:
                dat.loc[index,'PE_outliers'] = 'Missing N/A'

            if pd.isnull(row['pe_turnaround']) != True:
                if float(row['pe_turnaround']) > 3:
                    dat.loc[index, 'PE_outliers'] = 'turnaround time over 3 calendar days'

        if row['KPI 3'] == "Yes":
            if pd.isnull(row['po_turnaround']) == True:
                dat.loc[index, 'PO_outliers'] = 'Missing N/A'

            if pd.isnull(row['po_turnaround']) != True:

                if row['po_turnaround'] > 7:
                    dat.loc[index, 'PO_outliers'] = 'turnaround time over 7 calendar days'


    writer = pd.ExcelWriter(save_loc + save_name)


    format_for_teams(dat,kpi_num='KPI 1_4_5',outlier_col='Otif_outliers',reporting_cols=['COTD Category']).to_excel(writer, 'OTIF Outliers', index=False)
    format_for_teams(dat,kpi_num='KPI 2',outlier_col='PE_outliers',reporting_cols=['pe_turnaround']).to_excel(writer, 'PE Outliers', index=False)
    format_for_teams(dat,kpi_num='KPI 3',outlier_col='PO_outliers',reporting_cols=['po_turnaround']).to_excel(writer, 'PO Outliers', index=False)
    format_for_teams(dat,kpi_num='KPI 1_4_5',outlier_col='kpi4_outliers',reporting_cols=['Full Lead Time (not including production)','Actual Freight Leadtime',
                                                                                         'flt_vs_plt','flt_-_plt']).to_excel(writer, 'FLT Outliers', index=False)
    format_for_teams(dat,kpi_num='KPI 1_4_5',outlier_col='kpi5_outliers',reporting_cols=['Full Lead Time (not including production)','Actual Freight Leadtime',
                                                                                         'flt_vs_plt','flt_-_plt']).to_excel(writer, 'Within FLT Outliers', index=False)
    #format_for_teams(dat,kpi_num='KPI 1_4_5',outlier_col='kpi6_outliers').to_excel(writer, 'Within Freight Cost Outliers', index=False)
    #format_for_teams(dat,kpi_num='KPI 1_4_5',outlier_col='kpi7_outliers').to_excel(writer, 'Within Freight Cost Outliers', index=False)





    writer.save()

    return dat

