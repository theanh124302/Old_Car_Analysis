import joblib
import pandas as pd
import json

df = pd.read_csv('Data/data.csv')

def process_price(price):
    try:
        if price.find('Tỷ') != -1:
            ty= price.split('Tỷ')[0]
            trieu = price.split('Tỷ')[1]
            trieu = trieu.split('Triệu')[0]
            return float(ty)*1000000000 + float(trieu)*1000000
        elif price.find('Triệu') != -1:
            trieu = price.split('Triệu')[0]
            trieu = trieu.replace(' ','')
            return float(trieu)*1000000
        else:
            return 0
    except:
        return 0
df['price'] = df['price'].astype(str).apply(process_price)

def process_year_colum(year):
    if year.isdigit():
        return float(year)
    else:
        return 0
df['year'] = df['year'].astype(str).apply(process_year_colum)

df.drop_duplicates(subset=['url'], inplace=True)

df.dropna(subset=['car_name'], inplace=True)

df.drop(df[df['driven kms'] < 1000].index, inplace=True)
df.dropna(inplace=True)

df['brand'] = df['car_name'].str.split().str[0]

df['year'] = df['year'].apply(lambda x: df['year'].value_counts().index[0] if x < 1990 else x)

df['price'] = df['price'].apply(lambda x: df[df['year'] == x]['price'].mean() if x == 0 else x)

df['num_of_door'] = df['num_of_door'].apply(lambda x: df['num_of_door'].value_counts().index[0] if x > 6 else x)

threshold = 100
car_count = df['brand'].value_counts()
small_brands = car_count[car_count < threshold].index.tolist()
df['brand'] = df['brand'].apply(lambda x: 'Other' if x in small_brands else x)
df['brand'].fillna('Other', inplace=True)
brand_counts = df['brand'].value_counts()
total_brands = len(df['brand'])
brand_percentages = (brand_counts / total_brands) * 100

def car_band(x):
    if x in ['Rolls', 'Bentley', 'Lincoln', 'LandRover', 'Porsche', 'Maserati', 'Lexus', 'Jeep', 'Cadillac']:
        return 'LUXURY'
    elif x in ['Other', 'Volvo', 'Mercedes', 'Infiniti', 'Jaguar', 'Mini', 'BMW', 'Audi']:
        return 'PREMIUM'
    elif x in ['Subaru', 'Volkswagen', 'Peugeot', 'Toyota', 'Ford', 'VinFast', 'Mazda', 'Hyundai', 'Honda','MG','Mitsubishi']:
        return 'VOLUME'
    else:
        return 'LOWEND'

df['brand_segment'] = df['brand'].apply(car_band)

df['series'] = df['series'].apply(lambda x: df['series'].value_counts().index[0] if x == '-' else x)
df['series'].fillna(df['series'].value_counts().index[0], inplace=True)
df['transmission'] = df['transmission'].apply(lambda x: df['transmission'].value_counts().index[0] if x == '-' else x)
df['transmission'].fillna(df['transmission'].value_counts().index[0], inplace=True)
df['assemble_place'] = df['assemble_place'].map({'Lắp ráp trong nước': 0, 'Nhập khẩu': 1})
df = df.drop_duplicates(subset=['car_name'])
df = df[df['year'] >= 2018]
# Load the model from the file
model_loaded = joblib.load('model.joblib')
new_data = pd.DataFrame()
unique_car_name = df['car_name'].unique()
years_to_predict = [2018,2019,2020,2021,2022]
for car_name in unique_car_name:
    for year in years_to_predict:
        record = {
            "car_name": car_name,
            "year": year,
        }
        data = pd.DataFrame(record, index=[0])
        new_data = pd.concat([new_data, data], ignore_index=True)

new_data.loc[:, 'driven kms'] = (2023 - new_data['year'])*11000
new_data['brand'] = new_data['car_name'].str.split().str[0]
new_data['brand_segment'] = new_data['brand'].apply(car_band)
new_data['assemble_place'] = None
new_data['series'] = None
new_data['num_of_door'] = None
new_data['num_of_seat'] = None
new_data['engine_type'] = None
new_data['transmission'] = None

merged_df = pd.merge(new_data, df[['car_name', 'assemble_place', 'series', 'num_of_door', 'num_of_seat', 'engine_type', 'transmission']], on='car_name', how='left', suffixes=('', '_old'))
columns_to_fill = ['assemble_place', 'series', 'num_of_door', 'num_of_seat', 'engine_type', 'transmission']
for column in columns_to_fill:
     new_data[column] = new_data[column].combine_first(merged_df[column + '_old'])
new_data['price'] = model_loaded.predict(new_data).flatten()
list_of_dicts = new_data.to_dict(orient='records')
json_data = new_data.to_json(orient='records')
with open("Data/predict.json", 'w', encoding='utf-8') as json_file:
        json.dump(list_of_dicts, json_file,ensure_ascii=False ,    indent = 4)