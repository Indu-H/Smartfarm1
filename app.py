from flask import Flask, render_template, request, redirect, session
import requests

app = Flask(__name__)
app.secret_key = 'secret123'

# Flood-prone Karnataka districts
ALLOWED_DISTRICTS = [
    "udupi", "dakshina kannada", "uttara kannada", "kodagu", "belagavi", "raichur"
]

# Mapping districts to valid city names for weather API
DISTRICT_TO_CITY = {
    "udupi": "udupi",
    "dakshina kannada": "mangalore",
    "uttara kannada": "karwar",
    "kodagu": "madikeri",
    "belagavi": "belgaum",
    "raichur": "raichur"
}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    if request.form['username'] == 'farmer' and request.form['password'] == 'smart123':
        session['user'] = request.form['username']
        return redirect('/form')
    return "Invalid login. Try again."

@app.route('/form')
def form():
    if 'user' in session:
        return render_template('form.html', districts=[d.title() for d in ALLOWED_DISTRICTS])
    return redirect('/')

@app.route('/result', methods=['POST'])
def result():
    city = request.form['location'].strip().lower()
    crop = request.form['crop']

    if city not in ALLOWED_DISTRICTS:
        return f"❌ Sorry, SmartFarm only supports these districts:<br><br>{', '.join([d.title() for d in ALLOWED_DISTRICTS])}"

    api_city = DISTRICT_TO_CITY.get(city)
    weather = get_weather(api_city)
    if weather:
        temp, humidity, rainfall = weather
        message = get_recommendation(temp, humidity, rainfall, crop)
        return render_template('result.html',
                               city=city.title(), crop=crop,
                               temp=temp, humidity=humidity, rainfall=rainfall,
                               message=message)
    else:
        return "❌ Failed to fetch weather data. Please check the city name or try again."

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

def get_weather(city):
    api_key = "826db80774dea7662cc033abbf5b85b9"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},in&appid={api_key}&units=metric"
    try:
        data = requests.get(url).json()
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        rainfall = data.get('rain', {}).get('1h', 0)
        return temp, humidity, rainfall
    except:
        return None

def get_recommendation(temp, humidity, rainfall, crop):
    if rainfall > 70:
        return "⚠️ Too much rainfall. Risk of waterlogging. Not suitable for planting."
    elif rainfall < 10:
        return "⚠️ Very low rainfall. Irrigation is required."
    elif temp < 18:
        return "🌤️ Temperature too low. Suitable only for cold-weather crops."
    elif temp > 38:
        return "🔥 Too hot. High risk of heat stress in crops."
    elif humidity < 30:
        return "🌵 Low humidity. Not suitable for moisture-loving crops."

    crop = crop.lower()
    if crop == "rice":
        if rainfall < 30:
            return "⚠️ Rainfall too low for rice. Try water-conserving crops."
        else:
            return "✅ Conditions are suitable for rice cultivation."
    elif crop == "wheat":
        if temp > 32:
            return "⚠️ Too hot for wheat. Risk of low yield."
        else:
            return "✅ Conditions are suitable for wheat."
    elif crop == "ragi":
        if temp < 22 or temp > 30:
            return "⚠️ Temperature not ideal for ragi. Best range is 22°C to 30°C."
        elif humidity < 40:
            return "⚠️ Humidity too low for ragi."
        else:
            return "✅ Conditions are suitable for ragi cultivation."

    return "✅ General conditions are good for planting."

if __name__ == '__main__':
    app.run(debug=True)
