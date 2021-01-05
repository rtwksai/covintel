#!/usr/bin/env python
# coding: utf-8

# In[2]:


import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from sklearn import preprocessing
import xgboost as xg
from sklearn.metrics import mean_squared_error as MSE
import os


# In[3]:


main_df = pd.read_csv('https://api.covid19india.org/csv/latest/districts.csv')
main_df.tail(20)


# In[4]:


reference_df = pd.read_csv('https://api.covid19india.org/csv/latest/districts.csv')


# In[5]:


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
state_list = list(state_map.keys())

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


# In[6]:


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


# In[7]:


main_df['Population'] = main_df.apply(add_population_details,axis=1)
main_df['Population'].isna().sum()
drop_ind = main_df[(main_df.District=='Unknown') & (main_df.Population.isna())].index
main_df.drop(drop_ind,inplace=True)

main_df['Date'] = pd.to_datetime(main_df['Date'])
reference_df['Date'] = pd.to_datetime(reference_df['Date'])


# In[8]:


predict_columns = ['Confirmed','Recovered','Deceased', 'New_cases']
def lagn(df,n=4,cols=predict_columns):
    time_groups = df.groupby('Date')
    dfs = []
    for time in time_groups.groups:
        mini_df = time_groups.get_group(time)
        for off in range(1,n+1):
            prev_day = pd.to_datetime(time) - pd.DateOffset(days=off)
            lag_products = reference_df.loc[reference_df.Date==prev_day,cols+['State','District']]
            lag_names = [x + '_lag'+str(off) for x in cols]
            rename_col = {cols[i]: lag_names[i] for i in range(len(cols))}
            lag_products.rename(columns=rename_col,inplace=True)
            mini_df = pd.merge(mini_df,lag_products,on=['State','District'],how='left')
        mini_df.fillna(0,inplace=True)
        dfs.append(mini_df)
    resultant_df = pd.concat(dfs)
    return resultant_df


# In[9]:


reference_df.head()


# In[10]:


sample_df = main_df.loc[main_df.Date >= pd.to_datetime('2020-04-27')]
sample_df = lagn(sample_df,cols=['Confirmed'],n=1)


# In[11]:


sample_df['New_cases'] = sample_df['Confirmed'] - sample_df['Confirmed_lag1']
sample_df.head()
sample_df.drop(columns='Confirmed_lag1',inplace=True)


# In[12]:


sample_df.head()


# In[13]:


main_df = sample_df
reference_df = sample_df

del sample_df


# In[14]:


main_df['Recovered'] = main_df['Recovered'].values/main_df['Population'].values
main_df['Deceased'] = main_df['Deceased'].values/main_df['Population'].values
main_df['Confirmed'] = main_df['Confirmed'].values/main_df['Population'].values
main_df.drop(columns=['Other','Tested'],inplace=True)
main_df.loc[main_df['New_cases'] < 0, 'New_cases'] = 0


# In[15]:




yesterday = pd.to_datetime('today').normalize() - pd.DateOffset(days=1)
train_set = main_df.loc[main_df.Date < yesterday]
test_set = main_df.loc[main_df.Date >= yesterday]
train_set.tail()


# ### Applying lags

# In[16]:


main_df['Date'].value_counts()


# In[17]:


predict_columns = ['Confirmed','Recovered','Deceased', 'New_cases']
new_df = main_df.loc[main_df.Date >= pd.to_datetime('2020-05-1')]
new_df = lagn(new_df,cols=predict_columns)
new_df.tail()


# ### Selecting train columns

# In[18]:


predict_columns = ['Confirmed','Recovered','Deceased', 'New_cases']
train_columns = list(new_df.columns)
for c in predict_columns:
    train_columns.remove(c)
train_columns.remove('Date')
print(train_columns)


# In[19]:


le_state = preprocessing.LabelEncoder()
le_district = preprocessing.LabelEncoder()

new_df['State'] = le_state.fit_transform(new_df['State'])
new_df['District'] = le_district.fit_transform(new_df['District'])


# In[20]:


yesterday = '2020-12-01'
X_train = new_df[new_df.Date < pd.to_datetime(yesterday)][train_columns]
y_Confirmed = new_df[new_df.Date < pd.to_datetime(yesterday)]['Confirmed']
y_Recovered = new_df[new_df.Date < pd.to_datetime(yesterday)]['Recovered']
y_Deceased = new_df[new_df.Date < pd.to_datetime(yesterday)]['Deceased']
y_NewCases = new_df[new_df.Date < pd.to_datetime(yesterday)]['New_cases']

X_test = new_df[new_df.Date >= pd.to_datetime(yesterday)][train_columns]
y_test = new_df[new_df.Date >= pd.to_datetime(yesterday)]['New_cases']

y_test = y_test.reset_index()
y_test.drop(columns='index',inplace=True)


dates = new_df[new_df.Date >= pd.to_datetime('2020-12-01')]['Date']


# In[21]:


y_test.head()


# In[22]:



reg_Confirmed = xg.XGBRegressor()
reg_Confirmed.fit(X_train, y_Confirmed)

reg_Recovered = xg.XGBRegressor()
reg_Recovered.fit(X_train, y_Recovered)

reg_Deceased = xg.XGBRegressor()
reg_Deceased.fit(X_train, y_Deceased)

reg_NewCases = xg.XGBRegressor()
reg_NewCases.fit(X_train, y_NewCases)
pred = reg_NewCases.predict(X_test)
rmse = np.sqrt(MSE(y_test,pred))
print("RMSE : % f" %(rmse)) 


# In[23]:


tp = pd.DataFrame(pred)
tp[0].value_counts()


# ### Predictions:

# In[24]:


reference_df.head()


# In[25]:


def generate_pred_for_one_day(District, State, today_date):
    
    predict_columns = ['Confirmed','Recovered','Deceased', 'New_cases']
    pred_df = pd.DataFrame()

    pred_df['State'] = [State]
    pred_df['District'] = [District]

    pred_df['Population'] = pred_df.apply(add_population_details,axis=1)
    pred_df['Date'] = [today_date]
    pred_df = lagn(pred_df,cols=predict_columns)

    pred_df['State'] = le_state.transform(pred_df['State'])
    pred_df['District'] = le_district.transform(pred_df['District'])
    
    date = pred_df['Date']
    del pred_df['Date']
    
    pred_Confirmed = reg_Confirmed.predict(pred_df)
    pred_Deceased = reg_Deceased.predict(pred_df)
    pred_Recovered = reg_Recovered.predict(pred_df)
    pred_NewCases = reg_NewCases.predict(pred_df)
    
    reference_df.loc[len(reference_df)] = [today_date, State, District, pred_Confirmed[0], pred_Recovered[0], pred_Deceased[0], pred_df['Population'], pred_NewCases[0]]
    
    return date, pred_NewCases[0], pred_Confirmed[0]*pred_df['Population'][0], pred_Recovered[0]*pred_df['Population'][0]


def generate_cases_n_days(n = 10, case_type = "new", State="Andhra Pradesh", District = "Chittoor", today_date = pd.to_datetime('today').normalize()):
        
    dates = []
    new_pred = []
    confirm_pred = []
    recovered_pred = []
    
    for i in range(1, n + 1):
        date ,new, confirmed, recovered = generate_pred_for_one_day(District, State, pd.to_datetime(today_date) + pd.DateOffset(days = i))
        dates.append(date)
        new_pred.append(new)
        confirm_pred.append(confirmed)
        recovered_pred.append(recovered)
        
    if(case_type == "new"):
        return new_pred
    if(case_type == "recovered"):
        return recovered_pred


# In[26]:


print("next_10_AP_new")
print(generate_cases_n_days(n = 10, case_type = "new", State="Andhra Pradesh", District = "Chittoor", today_date = pd.to_datetime('today').normalize()))
print("next_10_KA_new")
print(generate_cases_n_days(n = 10, case_type = "new", State="Karnataka", District = "Bengaluru Urban", today_date = pd.to_datetime('today').normalize()))

print("next_10_AP_recov")
print(generate_cases_n_days(n = 10, case_type = "recovered", State="Andhra Pradesh", District = "Chittoor", today_date = pd.to_datetime('today').normalize()))
print("next_10_KA_recov")
print(generate_cases_n_days(n = 10, case_type = "recovered", State="Karnataka", District = "Bengaluru Urban", today_date = pd.to_datetime('today').normalize()))


# In[27]:


def calculate_herd_immunity(cases_threshold, days_threshold, State, District, today_date):
    new_cases = generate_cases_n_days(days_threshold, "new", State, District, today_date)
    print(np.array(new_cases)<cases_threshold)
    count = np.count_nonzero(np.array(new_cases)<cases_threshold)
    print(count)
    return (count/days_threshold)*100


District =  'Chittoor'
State = 'Andhra Pradesh'
today_date = '1-5-2021'
days = 10

print(calculate_herd_immunity(15, 10, State, District, today_date))    


# In[28]:


main_df.head()


# In[29]:


def get_prev_n_days_data(n = 30, case_type = "New_cases", State = "Andhra Pradesh", District = "Chittoor", today_date = pd.to_datetime('today').normalize()):
    a = main_df[["Date", "State", "District", case_type]].groupby(["State", "District"]).get_group((State, District)).reset_index(drop = True)
    a = a.loc[a.Date > pd.to_datetime(today_date) - pd.DateOffset(days = 30)] 
    a = a.loc[a.Date < pd.to_datetime(today_date)]
    return a[case_type].values

print("Month_data_for_AP - {}".format(get_prev_n_days_data(30, "Recovered", "Andhra Pradesh", "Chittoor", "1-6-2021")))
print("Month_data_for_KA - {}".format(get_prev_n_days_data(30, "Recovered", "Karnataka", "Bengaluru Urban", "1-6-2021")))

print("Month_data_for_AP - {}".format(get_prev_n_days_data(30, "New_cases", "Andhra Pradesh", "Chittoor", "1-6-2021")))
print("Month_data_for_KA - {}".format(get_prev_n_days_data(30, "New_cases", "Karnataka", "Bengaluru Urban", "1-6-2021")))


# In[30]:


def get_tomorrow_new_all_districts():
    tommorow = pd.to_datetime('today').normalize() + pd.DateOffset(days = 1)
    tom_df = main_df.loc[main_df['Date'] == pd.to_datetime('today').normalize()]
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


# In[31]:

path = "./data/state_data/"
for state in state_list:
    filename = "prediction_"+state_map[state]+".csv"
    state_df = future.groupby('State').get_group(state)
    state_df.to_csv(os.path.join(path,filename), index=False)