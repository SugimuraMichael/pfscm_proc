
from mrkpicheck_data_cleaning import replace_SCMS
import pandas as pd

li_name = 'PPM Pad LI June 26 2017'
li = pd.read_csv('C:/Users/585000/Desktop/PCFSM/pad li weekly files/'+li_name+'.csv')

li = replace_SCMS(li)


li.to_csv('C:/Users/585000/Desktop/PCFSM/pad li weekly files/'+li_name+'_2.csv',index= False)


