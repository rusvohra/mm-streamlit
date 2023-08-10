from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import DateField
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import xarray as xr
import json
import plotly

app = Flask(__name__)

# import data
def load_data():
    data = pd.read_csv("forecast.csv")
    data["Time"] = pd.to_datetime(data["Time"])
    images = np.load("delft_novjan_128.npz")["arr_0"]

    y, x = np.ogrid[:128, :128]
    radius = 64
    mask = (x - 63.5) ** 2 + (y - 63.5) ** 2 <= radius**2

    masked_array = np.ma.array(
        images, mask=np.broadcast_to(~mask, images.shape)
    )

    return data, masked_array

class DateForm(FlaskForm):
    date = DateField('Select a Date')

@app.route('/', methods=['GET', 'POST'])
def index():
    # form = DateForm()
    # selected_date = None

    # if form.validate_on_submit():
    #     selected_date = form.date.data

    form = DateForm()
    selected_date = None
    plot_div = None

    if form.validate_on_submit():
        selected_date = form.date.data

        # Call your Plotly plotting function with the selected_date
        plot_div = create_plot(selected_date)

    return render_template('index_cal.html', form=form, selected_date=selected_date, plot_div=plot_div)

def create_plot(data, images, selected_date):
    # Use the selected_date to create your plot using Plotly
    # For example, create a simple scatter plot:
    selected_data_key = selected_date  # .strftime("%Y-%m-%d")
    selected_data = data[data["Time"].dt.date == selected_data_key]
    images_day = images[selected_data.index]
    selected_data.reset_index(inplace=True)
    images_xr = xr.DataArray(
        images_day,
        dims=("Time", " ", " "),
        coords={"Time": selected_data["Time"].dt.strftime("%H:%M")},
    )
    layout = go.Layout(title='Your Plot Title', xaxis=dict(title='Date'), yaxis=dict(title='Value'))
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=selected_data["Time"],
            y=selected_data["True"],
            mode="lines",
            name="Ground Truth",
        ),
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="Vegetables in Europe"

    # Convert Plotly figure to HTML div
    plot_div = pio.to_html(fig, include_plotlyjs=False, full_html=False)
    return plot_div

if __name__ == '__main__':
    data, images = load_data()
    app.run(debug=True)
