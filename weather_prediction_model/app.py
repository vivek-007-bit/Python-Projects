
import pandas as pd
import numpy as np
import gradio as gr
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import mean_squared_error
from datetime import datetime, timedelta
import pytz



#Read Historical Data
def read_historical_data(filename):
    df = pd.read_csv(filename)
    df = df.dropna()
    df = df.drop_duplicates()
    return df



#Prepare Classification Data
def prepare_data(data):
    le = LabelEncoder()

    data['WindGustDir'] = le.fit_transform(data['WindGustDir'])
    data['RainTomorrow'] = le.fit_transform(data['RainTomorrow'])

    X = data[[
        'MinTemp',
        'MaxTemp',
        'WindGustDir',
        'WindGustSpeed',
        'Humidity',
        'Pressure',
        'Temp'
    ]]

    y = data['RainTomorrow']

    return X, y, le



#Train Rain Prediction Model
def train_rain_model(X, y):

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("Mean Squared Error:", mean_squared_error(y_test, y_pred))

    return model



#Prepare Regression Data
def prepare_regression_data(data, feature):

    X = []
    y = []

    for i in range(len(data) - 1):
        X.append(data[feature].iloc[i])
        y.append(data[feature].iloc[i + 1])

    X = np.array(X).reshape(-1, 1)
    y = np.array(y)

    return X, y



# Train Regression Model
def train_regression_model(X, y):

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    model.fit(X, y)

    return model



#Predict Future Values
def predict_future(model, current_value):

    predictions = [current_value]

    for _ in range(5):

        next_value = model.predict(
            np.array([[predictions[-1]]])
        )

        predictions.append(next_value[0])

    return predictions[1:]



#Load Dataset
historical_data = read_historical_data("weather.csv")


#Train Rain Prediction Model
X, y, le = prepare_data(historical_data)

rain_model = train_rain_model(X, y)



#Train Regression Models
X_temp, y_temp = prepare_regression_data(
    historical_data,
    "Temp"
)

X_hum, y_hum = prepare_regression_data(
    historical_data,
    "Humidity"
)

temp_model = train_regression_model(
    X_temp,
    y_temp
)

hum_model = train_regression_model(
    X_hum,
    y_hum
)



#Compass Direction Mapping
compass_points = [
    ('N', 0, 11.25),
    ('NNE', 11.25, 33.75),
    ('NE', 33.75, 56.25),
    ('ENE', 56.25, 78.75),
    ('E', 78.75, 101.25),
    ('ESE', 101.25, 123.75),
    ('SE', 123.75, 146.25),
    ('SSE', 146.25, 168.75),
    ('S', 168.75, 191.25),
    ('SSW', 191.25, 213.75),
    ('SW', 213.75, 236.25),
    ('WSW', 236.25, 258.75),
    ('W', 258.75, 281.25),
    ('WNW', 281.25, 303.75),
    ('NW', 303.75, 326.25),
    ('NNW', 326.25, 348.75),
    ('N', 348.75, 360)
]



#Main Weather Prediction Function
def weather_view(
    city,
    country,
    current_temp,
    feels_like,
    temp_min,
    temp_max,
    humidity,
    pressure,
    wind_speed,
    wind_direction_deg,
    description
):

    
    #Convert wind direction degree to compass direction
    wind_deg = wind_direction_deg % 360

    compass_direction = next(
        point
        for point, start, end in compass_points
        if start <= wind_deg < end
    )

    #Encode compass direction
    if compass_direction in le.classes_:
        compass_direction_encoded = le.transform(
            [compass_direction]
        )[0]
    else:
        compass_direction_encoded = 0


    #Create input dataframe
    current_data = {
        'MinTemp': temp_min,
        'MaxTemp': temp_max,
        'WindGustDir': compass_direction_encoded,
        'WindGustSpeed': wind_speed,
        'Humidity': humidity,
        'Pressure': pressure,
        'Temp': current_temp
    }


    current_df = pd.DataFrame([current_data])

    #Predict Rain
    rain_prediction = rain_model.predict(
        current_df
    )[0]


    #Predict future temperature and humidity
    future_temp = predict_future(
        temp_model,
        temp_min
    )

    future_humidity = predict_future(
        hum_model,
        humidity
    )


    #Generate future timestamps
    timezone = pytz.timezone("Asia/Kolkata")

    now = datetime.now(timezone)

    next_hour = now + timedelta(hours=1)

    next_hour = next_hour.replace(
        minute=0,
        second=0,
        microsecond=0
    )

    future_times = [
        (next_hour + timedelta(hours=i)).strftime("%H:00")
        for i in range(5)
    ]


    #Final Output
    result = f"""
            City: {city}, {country}

            Current Temperature: {current_temp} °C
            Feels Like: {feels_like} °C
            Minimum Temperature: {temp_min} °C
            Maximum Temperature: {temp_max} °C

            Humidity: {humidity} %
            Pressure: {pressure} hPa

            Wind Speed: {wind_speed} m/s
            Weather Description: {description}

            Rain Prediction: {"Yes" if rain_prediction else "No"}

            Future Temperature Prediction:
            """

    for time, temp in zip(future_times, future_temp):
        result += f"\n{time}: {round(temp, 1)} °C"

    result += "\n\nFuture Humidity Prediction:\n"

    for time, hum in zip(future_times, future_humidity):
        result += f"\n{time}: {round(hum, 1)} %"

    return result



#Gradio UI
interface = gr.Interface(
    fn=weather_view,

    inputs=[

        gr.Textbox(
            label="City Name",
            placeholder="Enter city"
        ),

        gr.Textbox(
            label="Country",
            placeholder="Enter country"
        ),

        gr.Number(
            label="Current Temperature (°C)"
        ),

        gr.Number(
            label="Feels Like Temperature (°C)"
        ),

        gr.Number(
            label="Minimum Temperature (°C)"
        ),

        gr.Number(
            label="Maximum Temperature (°C)"
        ),

        gr.Number(
            label="Humidity (%)"
        ),

        gr.Number(
            label="Pressure (hPa)"
        ),

        gr.Number(
            label="Wind Speed (m/s)"
        ),

        gr.Number(
            label="Wind Direction (Degrees)"
        ),

        gr.Textbox(
            label="Weather Description",
            placeholder="e.g Clear Sky"
        )

    ],

    outputs=gr.Textbox(
        label="Prediction Result",
        lines=60
    ),

    title="Weather Prediction App",

    description=(
        "Enter weather details manually "
        "to predict rain probability "
        "and future weather conditions."
    )
)


if __name__ == "__main__":
    interface.launch()
