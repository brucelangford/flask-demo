from flask import Flask, render_template, request, redirect
import requests
from bokeh.plotting import figure
from bokeh.embed import components
import pandas as pd
import os


app = Flask(__name__)

app.static_folder = 'static'
app.config.from_object(__name__)
app.vars={'ticker':'AAPL','features':['close']}



@app.route('/graph', methods=['POST'])
def plot_ticker(stock='AAPL',year=2017,month=12):
	
	if request.method=='POST':
		if request.form.get('ticker'):
			app.vars['ticker'] = request.form.get('ticker')

		app.vars['features'] = request.form.getlist('features')
		stock = app.vars['ticker']

		cols = {'open':'Open','high':'High','low':'Low','close':'Close','adj_open':'Adj. Open','adj_high':'Adj. High','adj_low':'Adj. Low','adj_close':'Adj. Close'}

		months = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
		if month==12:
		    month2=1
		    year2=year+1
		else:
		    month2=month+1
		    year2=year

		api_key = '&api_key=' + str(os.environ.get('APIKEY',3)) 
		api_url = 'https://www.quandl.com/api/v1/datasets/WIKI/%s.json?date.gte=%d-%02d-01&date.lt=%d-%02d-01%s' % (stock,year,month,year2,month2,api_key)
		session = requests.Session()

		session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
		raw_data = session.get(api_url)

		try:
			df = pd.DataFrame(data=raw_data.json()['data'], columns=raw_data.json()['column_names'])
		except:
			print(raw_data.json().keys())
			try:
				return raw_data.json()['quandl_error']
			except:
				print('no quandl_error available')
				try:
					return raw_data.json()['error']
				except:
					print('no error available')



		df.Date = pd.to_datetime(df.Date)
		tools = "pan,wheel_zoom,box_zoom,reset"
		plot = figure(tools=tools, title='From Quandl WIKI set: {} prices from {}, {}'.format(stock,months[month],year), 
		             x_axis_label = 'date',
		             x_axis_type='datetime')

		colors = ['red','blue','green','violet','cyan','black','yellow','magenta']

		filt = ( df.Date>=pd.datetime(year,month,1) ) & ( df.Date<pd.datetime(year2 ,month2,1)) 
		for feature, color in zip(app.vars['features'],colors[:len(app.vars['features'])]):
			plot.line(df[filt].Date, df[filt][cols[feature]], legend=feature, color=color)
		# plot.legend = app.vars['features']
		plot.legend.location = 'bottom_right'
		plot.height = 400;
		plot.width = 600;
		# show(plot) 
		script, div = components(plot)
		return render_template('graph.html', script=script, div=div)


@app.route('/')
def index():
	plot_ticker()
	return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')


if __name__ == '__main__':
	app.run(port=33507)
