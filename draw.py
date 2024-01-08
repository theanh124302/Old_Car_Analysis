
import numpy as np # linear algebra
import pandas as pd 


import matplotlib.pyplot as plt 
df = pd.read_json('Data/predict.json')
df_new = pd.read_json('Data/predict.json')


df_new['price'] = df_new['price'] * 1.25 +20000000

df['year'] = 2023 - df['year']
df_new['year'] = 0
df = pd.concat([df, df_new])


# Calculate the percentage change relative to the first year
df['percentage_change'] = (df['price'] / df.groupby('car_name')['price'].transform('first') - 1) * 100

# Group by brand and year, calculate mean, and reset index
grouped_df = df.groupby(['brand', 'year'])['percentage_change'].mean().reset_index()

# Get the top 10 most frequent brands
top_brands = df['brand'].value_counts().nlargest(10).index

# Filter the dataframe for the top 10 brands
df_top_brands = grouped_df[grouped_df['brand'].isin(top_brands)]

# Pivot the dataframe to make it suitable for plotting
pivot_df = df_top_brands.pivot(index='year', columns='brand', values='percentage_change')

# Plotting
ax = pivot_df.plot(kind='line', marker='o', figsize=(10, 6))
ax.set_xlabel('Year')
ax.set_ylabel('Percentage Change')
ax.set_title('Percentage Change in Mean Price for Top 10 Brands')
plt.legend(title='Brand')
plt.show()


