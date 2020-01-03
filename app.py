from flask import Flask, render_template, request, redirect
import requests
from bokeh.plotting import figure
from bokeh.embed import components
import pandas as pd


app = Flask(__name__)

app.static_folder = 'static'

@app.route('/graph')
def plot_ticker(stock='AAPL',year=2017,month=12):
    months = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
    api_url = 'https://www.quandl.com/api/v1/datasets/WIKI/%s.json' % stock
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
    raw_data = session.get(api_url)
    df = pd.DataFrame(data=raw_data.json()['data'], columns=raw_data.json()['column_names'])
    df.Date = pd.to_datetime(df.Date)
    tools = "pan,wheel_zoom,box_zoom,reset"
    plot = figure(tools=tools, title='From Quandl WIKI set: {} Close price from {}, {}'.format(stock,months[month],year), 
                 x_axis_label = 'date',
                 x_axis_type='datetime')
    if month==12:
        month2=1
        year2=year+1
    else:
        month2=month+1
        year2=year
    filt = ( df.Date>=pd.datetime(year,month,1) ) & ( df.Date<pd.datetime(year2 ,month2,1)) 
    plot.line(df[filt].Date, df[filt].Close)
    # show(plot) 
    script, div = components(plot)
    return render_template('graph.html', script=script, div=div)


@app.route('/')
def index():
  return render_template('index.html')

@app.route('/about')
def about():
  return render_template('about.html')

if __name__ == '__main__':
  app.run(port=33507)
