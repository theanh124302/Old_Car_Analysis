import copy
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from skrub import (
    SimilarityEncoder,
    MinHashEncoder,
    GapEncoder,
     TableVectorizer
)
import joblib
import json

# Save pipeline



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
        return 'NORMAL'
    else:
        return 'LOWEND'

df['brand_segment'] = df['brand'].apply(car_band)

df['series'] = df['series'].apply(lambda x: df['series'].value_counts().index[0] if x == '-' else x)
df['series'].fillna(df['series'].value_counts().index[0], inplace=True)
df['transmission'] = df['transmission'].apply(lambda x: df['transmission'].value_counts().index[0] if x == '-' else x)
df['transmission'].fillna(df['transmission'].value_counts().index[0], inplace=True)
df['assemble_place'] = df['assemble_place'].map({'Lắp ráp trong nước': 0, 'Nhập khẩu': 1})

df.dropna(subset=['price'], inplace=True)
df.reset_index(drop=True, inplace=True)

# X_without_car = df.drop(['price','url','car_name'], axis=1)
X_with_car = df.drop(['price','url'], axis=1)
y = df['price']


copy_X = copy.deepcopy(X_with_car)
copy_y = copy.deepcopy(y)
X_train, X_test, y_train, y_test = train_test_split(copy_X, copy_y, test_size=0.2, random_state=42)

pipeline = make_pipeline(TableVectorizer(high_cardinality_transformer=GapEncoder(n_components=30)), HistGradientBoostingRegressor(max_bins=255,max_depth=20,max_iter = 300,max_leaf_nodes=31,min_samples_leaf=20))
pipeline.fit(X_train,y_train)


joblib.dump(pipeline, 'model.joblib')
loaded_pipeline = joblib.load('model.joblib')

y_pred = loaded_pipeline.predict(X_test)

# Calculate R-squared
r_squared = r2_score(y_test, y_pred)
print(r_squared)