from flask import Flask, render_template
import numpy as np
import xarray as xr
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from sklearn.metrics import r2_score
from scipy.stats import pearsonr

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

@app.route("/")
def index():
    data, images = load_data()

    # ... (rest of your code)

    return render_template("index.html", selected_date=selected_date, plot_filename=plot_filename)

if __name__ == "__main__":
    app.run(debug=True)
