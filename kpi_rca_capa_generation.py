import pandas as pd



'''
This document is based off of taking the comments on rows from the google sheets and creating a new doc
which is essentially the ASN or PE or PO number depending on the KPI, then the comments fields see below for
the structure of the document. Future iteration of this would be to autoamte the pulling from each of the google sheets
that would remove the manual creation of the RCA/CAPA reference file with below structure

Field list:
Identifier
Supplier days delay	PFSCM days delay
Root Cause Analysis (PFSCM days delay explanation)
What is the Corrective Action?
Additional Input Required

File then iterates over this and generates a txt file which can be used as an RCA and CAPA templete for the teams to
work through.
'''

dat = pd.read_csv('C:/Users/585000/Desktop/PCFSM/rca_capa_8_11.csv')

dat = dat.dropna(how='all')

for col in list(dat.columns):
    dat[col] = dat[col].fillna('')
    print col
    #dat[col] = dat[col].str.decode('latin-1')


country_list = []
with open("C:/Users/585000/Desktop/PCFSM/RCA_811_test.txt", "w") as text_file:
    text_file.write("RCA and CAPA Document\n")
    text_file.write(" \n")

    for index, row in dat.iterrows():

        if row['Ship To Country Name'] == '':

            text_file.write(str(row['Identifier'])+":")
            text_file.write(" \n")
            if row['Supplier days delay'] != '':
                text_file.write("\tSupplier Delays: "+str(row['Supplier days delay']))
                text_file.write(" \n")
            if row['PFSCM days delay'] != '':
                text_file.write("\tPFSCM Delays: "+str(row['PFSCM days delay']))
                text_file.write(" \n")

            text_file.write("\tRCA: "+str(row['Root Cause Analysis (PFSCM days delay explanation)']))
            text_file.write(" \n")
            text_file.write("\tCAPA: "+str(row['What is the Corrective Action?']))
            text_file.write(" \n")

            if row['Additional Input Required'] != '':
                text_file.write(" ")
                text_file.write("\tAdditional Input: "+str(row['Additional Input Required']))
                text_file.write(" \n")


        if row['Ship To Country Name'] != '':

            if row['Ship To Country Name'] not in country_list:
                country_list.append(row['Ship To Country Name'])
                current_c = row['Ship To Country Name']

                text_file.write(str(current_c) + ":\n")

                for inner_index, inner_row in dat.iterrows():
                    if inner_row['Ship To Country Name'] == current_c:
                        text_file.write('\t'+str(inner_row['Identifier']) + ":")
                        text_file.write(" \n")

                        if inner_row['Supplier days delay'] != '':
                            text_file.write("\t\tSupplier Delays: " + str(inner_row['Supplier days delay']))
                            text_file.write(" \n")
                        if inner_row['PFSCM days delay'] != '':
                            text_file.write("\t\tPFSCM Delays: " + str(inner_row['PFSCM days delay']))
                            text_file.write(" \n")

                        text_file.write("\t\tRCA: " + str(inner_row['Root Cause Analysis (PFSCM days delay explanation)']))
                        text_file.write(" \n")
                        text_file.write("\t\tCAPA: " + str(inner_row['What is the Corrective Action?']))
                        text_file.write(" \n")
                        if inner_row['Additional Input Required'] != '':
                            text_file.write(" ")
                            text_file.write("\t\tAdditional Input: " + str(inner_row['Additional Input Required']))
                            text_file.write(" \n")
                        text_file.write(" \n")

        text_file.write(" \n")


