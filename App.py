from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib

load_model = joblib.load("model.joblib")
app = Flask(__name__)


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
def car_band(x):
    if x in ['Rolls', 'Bentley', 'Lincoln', 'LandRover', 'Porsche', 'Maserati', 'Lexus', 'Jeep', 'Cadillac']:
        return 'LUXURY'
    elif x in ['Other', 'Volvo', 'Mercedes', 'Infiniti', 'Jaguar', 'Mini', 'BMW', 'Audi']:
        return 'PREMIUM'
    elif x in ['Subaru', 'Volkswagen', 'Peugeot', 'Toyota', 'Ford', 'VinFast', 'Mazda', 'Hyundai', 'Honda','MG','Mitsubishi']:
        return 'NORMAL'
    else:
        return 'LOWEND'

new_car_df = pd.read_json("Data/new_car_data.json")
new_car_df.drop_duplicates(subset=['car_name'], inplace=True)
new_car_df['price'] = new_car_df['price'].astype(str).apply(process_price)*1.1+20000000

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    df = pd.DataFrame(data, index=[0])
    df['brand_segment'] = df['brand'].apply(car_band)
    try:
        prediction = load_model.predict(df)
    except Exception as e:
        prediction = "???"
    merged_df = pd.merge(df, new_car_df[
        ['car_name', 'price']],
                         on='car_name', how='left', suffixes=('', '_new'))
    print(merged_df)
    predict_price = int(prediction[0])
    if not pd.isna(merged_df['price'].iloc[0]):
        depreciation = predict_price/merged_df['price'].iloc[0]
        percent = int(depreciation*100)
        if predict_price > 1000000000:
            result = {
                "prediction": str(predict_price // 1000000000) + " tỷ " + str(
                    (predict_price % 1000000000) // 1000000) + " triệu \n Giá trị " + str(percent) + "% so với xe mới."
            }
        else:
            result = {
                "prediction": str(predict_price// 1000000) + " triệu \n Giá trị " + str(percent) + "% so với xe mới."
            }
        print(depreciation)
    else:
        if predict_price > 1000000000:
            result = {
                "prediction": str(predict_price // 1000000000) + " tỷ " + str(
                    (predict_price % 1000000000) // 1000000) + " triệu "
            }
        else:
            result = {
                "prediction": str(predict_price// 1000000) + " triệu "
            }
    print(result)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
