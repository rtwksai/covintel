#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# %% [code]
# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session

# %% [code]
main_df = pd.read_csv('https://api.covid19india.org/csv/latest/districts.csv')
main_df.head(20)

# %% [code]
reference_df = pd.read_csv('https://api.covid19india.org/csv/latest/districts.csv')

# %% [code]
pop_df = pd.read_json("https://api.covid19india.org/v4/data.json")

state_map = {
    "AN": "Andaman and Nicobar Islands",
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CH": "Chandigarh",
    "CT": "Chhattisgarh",
    "DN": "Dadra and Nagar Haveli and Daman and Diu",
    "DL": "Delhi",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "JK": "Jammu and Kashmir",
    "JH": "Jharkhand",
    "KA": "Karnataka",
    "KL": "Kerala",
    "LA": "Ladakh",
    "MP": "Madhya Pradesh",
    "MH": "Maharashtra",
    "MN": "Manipur",
    "ML": "Meghalaya",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OR": "Odisha",
    "PY": "Puducherry",
    "PB": "Punjab",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TG": "Telangana",
    "TR": "Tripura",
    "UP": "Uttar Pradesh",
    "UT": "Uttarakhand",
    "WB": "West Bengal"
}
state_map = {value:key for key, value in state_map.items()}
main_df = main_df[main_df.District != "Italians"]
main_df = main_df[main_df.District != "Other State"]
main_df = main_df[main_df.District != "Other Region"]
main_df = main_df[main_df.District != "Evacuees"]
main_df = main_df[main_df.District != "Airport Quarantine"]
main_df = main_df[main_df.District != "BSF Camp"]
main_df = main_df[main_df.District != "Railway Quarantine"]
main_df = main_df[main_df.District != "Foreign Evacuees"]
main_df = main_df[main_df.District != "Others"]
main_df = main_df[main_df.District != "State Pool"]

# %% [code]
def add_population_details(row):
    try:
        pop_df[state_map[row['State']]]['districts'][row['District']]['meta']['population']
        return pop_df[state_map[row['State']]]['districts'][row['District']]['meta']['population']
    except KeyError:
        if row['District'] == 'Capital Complex':
            return 122930
        elif row['District'] == 'Gaurela Pendra Marwahi':            
            return 336000
        elif row['District'] == 'Pakke Kessang':
            return 7000
        elif row['District'] == 'Saitual':
            return 10243
        elif row['District'] == 'Khawzawl':
            return 13113
        elif row['District'] == 'Hnahthial':
            return 7187
        elif row['District'] == 'Niwari':
            return 20711
        elif row['District'] == 'Lepa Rada':
            return 10000
        elif row['District'] == 'Agar Malwa':
            return 37950
        elif row['District'] == 'Kra Daadi':
            return 37950
        elif row['State'] == 'Andaman and Nicobar Islands':
            return 200000
        elif row['State'] == 'Telangana' or row['State'] == 'Assam':
            return 30000000
        elif row['State'] == 'Goa':
            return 1800000
        elif row['State'] == 'Manipur':
            return 2700000
        elif row['State'] == 'Sikkim':
            return 600000
        
        return np.nan


# %% [code]
main_df['Population'] = main_df.apply(add_population_details,axis=1)
main_df['Population'].isna().sum()
drop_ind = main_df[(main_df.District=='Unknown') & (main_df.Population.isna())].index
main_df.drop(drop_ind,inplace=True)

main_df['Date'] = pd.to_datetime(main_df['Date'])
reference_df['Date'] = pd.to_datetime(reference_df['Date'])

# %% [code]
predict_columns = ['Confirmed','Recovered','Deceased','New_cases']
def lagn(df,n=4,cols=predict_columns):
    time_groups = df.groupby('Date')
    dfs = []
    for time in time_groups.groups:
        mini_df = time_groups.get_group(time)
        for off in range(1,n+1):
            prev_day = pd.to_datetime(time) - pd.DateOffset(days=off)
#             print(prev_day)
            lag_products = reference_df.loc[reference_df.Date==prev_day,cols+['State','District']]
#             print(lag_products.head())
            lag_names = [x + '_lag'+str(off) for x in cols]
            rename_col = {cols[i]: lag_names[i] for i in range(len(cols))}
            lag_products.rename(columns=rename_col,inplace=True)
            mini_df = pd.merge(mini_df,lag_products,on=['State','District'],how='left')
        mini_df.fillna(0,inplace=True)
        dfs.append(mini_df)
    resultant_df = pd.concat(dfs)
#     resultant_df.drop(columns=['time_series','customer_code'],inplace=True)
    return resultant_df

# %% [code]
reference_df.head()

# %% [code]
sample_df = main_df.loc[main_df.Date >= pd.to_datetime('2020-04-27')]
sample_df = lagn(sample_df,cols=['Confirmed'],n=1)

# %% [code]
sample_df['New_cases'] = sample_df['Confirmed'] - sample_df['Confirmed_lag1']
sample_df.head()
sample_df.drop(columns='Confirmed_lag1',inplace=True)

# %% [code]
sample_df.head()

# %% [code]
main_df = sample_df
reference_df = sample_df

del sample_df

# %% [code]
main_df['Recovered'] = main_df['Recovered'].values/main_df['Population'].values
main_df['Deceased'] = main_df['Deceased'].values/main_df['Population'].values
main_df['Confirmed'] = main_df['Confirmed'].values/main_df['Population'].values
main_df.drop(columns=['Other','Tested'],inplace=True)
main_df.loc[main_df['New_cases'] < 0, 'New_cases'] = 0

# %% [code]


yesterday = pd.to_datetime('today').normalize() - pd.DateOffset(days=1)
train_set = main_df.loc[main_df.Date < yesterday]
test_set = main_df.loc[main_df.Date >= yesterday]
train_set.tail()



# %% [code]
def get_prev_n_days_data(n = 30, case_type = "New_cases", State = "Andhra Pradesh", District = "Chittoor", today_date = pd.to_datetime('today').normalize()):
    a = main_df[["Date", "State", "District", case_type]].groupby(["State", "District"]).get_group((State, District)).reset_index(drop = True)
    a = a.loc[a.Date > pd.to_datetime(today_date) - pd.DateOffset(days = 30)] 
    a = a.loc[a.Date < pd.to_datetime(today_date)]
    return a[case_type].values

print("Month_data_for_AP - {}".format(get_prev_n_days_data(30, "Recovered", "Andhra Pradesh", "Chittoor", "1-6-2021")))
print("Month_data_for_KA - {}".format(get_prev_n_days_data(30, "Recovered", "Karnataka", "Bengaluru Urban", "1-6-2021")))

print("Month_data_for_AP - {}".format(get_prev_n_days_data(30, "New_cases", "Andhra Pradesh", "Chittoor", "1-6-2021")))
print("Month_data_for_KA - {}".format(get_prev_n_days_data(30, "New_cases", "Karnataka", "Bengaluru Urban", "1-6-2021")))

# %% [code]
# main_df['Date'] = pd.to_datetime(main_df['Date'])
# main_df['Active'] = main_df['Confirmed'] - main_df['Recovered'] - main_df['Deceased'] - main_df['Other']


# reference_df['Date'] = pd.to_datetime(reference_df['Date'])
# reference_df['Active'] = reference_df['Confirmed'] - reference_df['Recovered'] - reference_df['Deceased'] - reference_df['Other']

# %% [code]
# # main_df['Recovery_rate'] = main_df['Recovered'].values/main_df['Confirmed'].values
# main_df['Recovered'] = main_df['Recovered'].values/main_df['Population'].values
# # main_df['Fatalty_rate'] = main_df['Deceased'].values/main_df['Confirmed'].values
# main_df['Deceased'] = main_df['Deceased'].values/main_df['Population'].values
# main_df['Confirmed'] = main_df['Confirmed'].values/main_df['Population'].values


# %% [code]
# reference_df = pd.DataFrame(main_df[['Date', 'State', 'District', 'Confirmed', 'Recovered', 'Deceased', 'Active']])

# %% [markdown]
# ### Applying lags

# %% [code]
main_df['Date'].value_counts()

# %% [code]
predict_columns = ['Confirmed','Recovered','Deceased', 'New_cases']
new_df = main_df.loc[main_df.Date >= pd.to_datetime('2020-05-1')]
new_df = lagn(new_df,cols=predict_columns)
new_df.tail()

# %% [markdown]
# Adding synthetic data

# %% [code]
synthetic_df = new_df[new_df.Date > pd.to_datetime('2020-11-01')]
synthetic_df2 = new_df[new_df.Date > pd.to_datetime('2020-12-01')]
synthetic_df3 = new_df[new_df.Date > pd.to_datetime('2020-12-15')]
synthetic_df.loc[synthetic_df.Confirmed < 1,'Recovered_lag1'] = 0.3
synthetic_df['New_cases'] = synthetic_df['New_cases']/1.3
synthetic_df.head()
new_df = pd.concat([new_df,synthetic_df])

del synthetic_df

# %% [code]
synthetic_df2.loc[synthetic_df2.Confirmed < 1,'Recovered_lag1'] = 0.6
synthetic_df2['New_cases'] = synthetic_df2['New_cases']/5
synthetic_df2.head()
new_df = pd.concat([new_df,synthetic_df2])

del synthetic_df2

# %% [code]
synthetic_df3.loc[synthetic_df3.Confirmed < 1,'Recovered_lag1'] = 0.9
synthetic_df3['New_cases'] = synthetic_df3['New_cases']/30
synthetic_df3.head()
new_df = pd.concat([new_df,synthetic_df3])

del synthetic_df3

# %% [markdown]
# ### Selecting train columns

# %% [code]
predict_columns = ['Confirmed','Recovered','Deceased', 'New_cases']
train_columns = list(new_df.columns)
train_columns = list(new_df.columns)
for c in predict_columns:
    train_columns.remove(c)
train_columns.remove('Date')
print(train_columns)

# %% [code]
from sklearn import preprocessing

le_state = preprocessing.LabelEncoder()
le_district = preprocessing.LabelEncoder()

# new_df[['State','District']] = new_df[['State','District']].apply(le.fit_transform)
new_df['State'] = le_state.fit_transform(new_df['State'])
new_df['District'] = le_district.fit_transform(new_df['District'])

# %% [code]
# new_df['New_cases'].value_counts()

# %% [code]
yesterday = pd.to_datetime('today').normalize() - pd.DateOffset(days=1)
X_train = new_df[new_df.Date < yesterday][train_columns]
y_Confirmed = new_df[new_df.Date < yesterday]['Confirmed']
y_Recovered = new_df[new_df.Date < yesterday]['Recovered']
y_Deceased = new_df[new_df.Date < yesterday]['Deceased']
y_NewCases = new_df[new_df.Date < yesterday]['New_cases']


X_test = new_df[new_df.Date >= pd.to_datetime(yesterday)][train_columns]
y_test = new_df[new_df.Date >= pd.to_datetime(yesterday)]['New_cases']

dates = new_df[new_df.Date >= pd.to_datetime('2020-12-01')]['Date']

# %% [code]
import xgboost as xg
from sklearn.metrics import mean_squared_error as MSE

reg_Confirmed = xg.XGBRegressor()
reg_Confirmed.fit(X_train, y_Confirmed)
# pred = reg_Confirmed.predict(X_test)
# print(pred)
# rmse = np.sqrt(MSE(y_test,pred))
# print("RMSE : % f" %(rmse)) 


reg_Recovered = xg.XGBRegressor()
reg_Recovered.fit(X_train, y_Recovered)
# pred = reg_Recovered.predict(X_test)
# print(pred)
# rmse = np.sqrt(MSE(y_test,pred))
# print("RMSE : % f" %(rmse)) 


reg_Deceased = xg.XGBRegressor()
reg_Deceased.fit(X_train, y_Deceased)
# pred = reg_Deceased.predict(X_test)
# print(pred)
# rmse = np.sqrt(MSE(y_test,pred))
# print("RMSE : % f" %(rmse)) 

reg_NewCases = xg.XGBRegressor()
reg_NewCases.fit(X_train, y_NewCases)

# %% [code]
print(train_columns)
main_df.columns

# %% [code]
def get_tomorrow_new_all_districts():
    tommorow = pd.to_datetime('today').normalize() + pd.DateOffset(days = 1)
    tom_df = pd.DataFrame(main_df.loc[main_df['Date'] == pd.to_datetime('today').normalize()])
    print(tom_df.columns)
    tom_df['Date'] = tommorow
    tom_df.head()
    x_tom = lagn(tom_df)[train_columns]
    x_tom['State'] = le_state.transform(x_tom['State'])
    x_tom['District'] = le_district.transform(x_tom['District'])
    tom_pred = reg_NewCases.predict(x_tom)

    future = main_df.loc[main_df['Date']==pd.to_datetime('today').normalize(),['State','District']]
    future['Date'] = tommorow
    future['Active Cases'] = tom_pred
    return future
                
future = get_tomorrow_new_all_districts()

# %% [code]
future['Active Cases'] = np.round(future['Active Cases'].values)
future.head() #This csv goes directly to map

# %% [markdown]
# ### Predictions:

# %% [code]
pred = reg_Deceased.predict(X_test)
pred

# %% [code]
sample = main_df.loc[(main_df.State == 'Andhra Pradesh') & (main_df.District == 'Chittoor')]
sample

# %% [code]
def generate_pred_for_one_day(District, State, today_date, immune_fraction = 0):
    
    predict_columns = ['Confirmed','Recovered','Deceased', 'New_cases']
    pred_df = pd.DataFrame()

    pred_df['State'] = [State]
    pred_df['District'] = [District]

    pred_df['Population'] = pred_df.apply(add_population_details,axis=1)
#     pred_df['Date'] = [pd.to_datetime(today_date)]
    pred_df['Date'] = [today_date]
    pred_df = lagn(pred_df,cols=predict_columns)

    pred_df['State'] = le_state.transform(pred_df['State'])
    pred_df['District'] = le_district.transform(pred_df['District'])
    
    if(immune_fraction <= 1 and immune_fraction > 0):
        pred_df['Recovered_lag1'] += immune_fraction
        pred_df['Recovered_lag2'] += immune_fraction/1.1
        pred_df['Recovered_lag3'] += immune_fraction/1.2
        pred_df['Recovered_lag4'] += immune_fraction/1.4
#     print(reference_df)
    date = pred_df['Date']
    del pred_df['Date']
    
    pred_Confirmed = reg_Confirmed.predict(pred_df)
    pred_Deceased = reg_Deceased.predict(pred_df)
    pred_Recovered = reg_Recovered.predict(pred_df)
    pred_NewCases = reg_NewCases.predict(pred_df)
    
#     try:
#         reference_df.loc[reference_df.date]
#     except:
    reference_df.loc[len(reference_df)] = [today_date, State, District, pred_Confirmed[0], pred_Recovered[0], pred_Deceased[0], pred_df['Population'], pred_NewCases[0]]
    
    return date, pred_NewCases[0], pred_Confirmed[0]*pred_df['Population'][0], pred_Recovered[0]*pred_df['Population'][0]

# %% [code]
def generate_cases_n_days(n = 10, case_type = "new", State="Andhra Pradesh", District = "Chittoor", today_date = pd.to_datetime('today').normalize(),immune_fraction=0):
    dates = []
    new_pred = []
    confirm_pred = []
    recovered_pred = []
    
    for i in range(1, n + 1):
        date ,new, confirmed, recovered = generate_pred_for_one_day(District, State, pd.to_datetime(today_date) + pd.DateOffset(days = i),immune_fraction=immune_fraction)
        dates.append(date)
        new_pred.append(new)
        confirm_pred.append(confirmed)
        recovered_pred.append(recovered)
        
    if(case_type == "new"):
        return new_pred
    if(case_type == "recovered"):
        return recovered_pred

# %% [code]


def get_tomorrow_new_all_districts():
    tommorow = pd.to_datetime('today').normalize() + pd.DateOffset(days = 1)
    tom_df = pd.DataFrame(main_df.loc[main_df['Date'] == pd.to_datetime('today').normalize()])
    tom_df['Date'] = tommorow
    tom_df.head()
    x_tom = lagn(tom_df)[train_columns]
    x_tom['State'] = le_state.transform(x_tom['State'])
    x_tom['District'] = le_district.transform(x_tom['District'])
    tom_pred = reg_NewCases.predict(x_tom)

    future = main_df.loc[main_df['Date']==pd.to_datetime('today').normalize(),['State','District']]
    future['Date'] = tommorow
    future['Active Cases'] = tom_pred
    return future
                
future2 = get_tomorrow_new_all_districts()


# %% [code]
future2.head()

# %% [code]
main_df

# %% [code]
def get_prev_n_days_data(n = 30, case_type = "New_cases", State = "Andhra Pradesh", District = "Chittoor", today_date = pd.to_datetime('today').normalize()):
    a = main_df[["Date", "State", "District", case_type]].groupby(["State", "District"]).get_group((State, District)).reset_index(drop = True)
    a = a.loc[a.Date > pd.to_datetime(today_date) - pd.DateOffset(days = 30)] 
    a = a.loc[a.Date < pd.to_datetime(today_date)]
    return a[case_type].values

def update_row(row):
    return get_prev_n_days_data(State=row['State'],District=row['District'])


# %% [code]
districts = main_df.loc[main_df.Date == str(pd.to_datetime('today')-pd.DateOffset(1))[:10],['State','District']]
districts['Date'] = pd.to_datetime('today')
districts['Date'] = districts['Date'].dt.date
districts.head()

# %% [code]
prev_30_days = pd.DataFrame(districts)
prev_30_days['past_30_days'] = prev_30_days.apply(update_row,axis=1)
prev_30_days.to_csv("past_30_days_data.csv")

# %% [code]
def get_10_new_days_all_districts(immune_fraction=0):
    tom_df = pd.DataFrame(main_df.loc[main_df['Date'] == pd.to_datetime('today').normalize()])
#     tom_df['Date'] = tommorow
    tom_df.head() 
    result = pd.DataFrame(columns=['State','District','Date','Next_10_days'])
    for state in list(tom_df['State'].unique()):
#         print(state)
        districts_of_state = tom_df.loc[tom_df.State == state]
#         print(districts_of_state['District'])
        for district in list(districts_of_state['District']):
            prediction_10 = generate_cases_n_days(n = 10, case_type = "new", State=state, District = district, today_date = pd.to_datetime('today').normalize(),immune_fraction=immune_fraction)
            result.loc[len(result)] = [state,district,pd.to_datetime('today').normalize(),np.round(prediction_10)]
    result = [max(x,0) for x in result]
    return result

# %% [code]
def update_row_pred(row):
    return generate_cases_n_days(n = 10, case_type = "new", State=row['State'], District = row['District']                                 , today_date = pd.to_datetime('today').normalize(),immune_fraction=row['Immune_Fraction'])

# %% [code]
vaccine_df = pd.DataFrame(districts)
vaccine_df['Date'] = pd.to_datetime('today')
vaccine_df['Date'] = vaccine_df['Date'].dt.date
vaccine_df['Immune_Fraction'] = 0

# %% [code]
vaccine_df['Next_10_days'] = vaccine_df.apply(update_row_pred,axis=1)

# %% [code]
vaccine_df.head()

# %% [code]
result_vaccine0 = get_10_new_days_all_districts()

# %% [code]
result_vaccine0.head(30)

# %% [code]
result_vaccine10 = get_10_new_days_all_districts(immune_fraction=0.1)

# %% [code]
result_vaccine30 = get_10_new_days_all_districts(immune_fraction=0.3)

# %% [code]
result_vaccine60 = get_10_new_days_all_districts(immune_fraction=0.6)

# %% [code]
result_vaccine90 = get_10_new_days_all_districts(immune_fraction=0.9)

# %% [code]
def get_10_new_row(row):
    prediction_10 = generate_cases_n_days(n = 10, case_type = "new", State=row['State'], District = row['District'], today_date = row['Date'],immune_fraction=row['immune_fraction'])

# %% [code]
r_v0 = pd.DataFrame(main_df[['State','District']])
r_v0['Date'] = pd.to_datetime('today').normalize()
r_v0['immune_fraction'] = 0
r_v0.head()

# %% [code]
future2.to_csv("Next_day_cases.csv")
future2.head()

# %% [code]
result_vaccine0.to_csv("No_Vaccination.csv")

# %% [code]
result_vaccine10.to_csv("10%_Vaccination.csv")

# %% [code]
result_vaccine30.to_csv("30%_Vaccination.csv")

# %% [code]
result_vaccine60.to_csv("60%_Vaccination.csv")

# %% [code]
result_vaccine90.to_csv("90%_Vaccination.csv")

