import streamlit as st
import numpy as np
import xarray as xr
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import StringIO
from sklearn.metrics import r2_score, mean_squared_error


# import data
@st.cache_data(
    hash_funcs={StringIO: StringIO.getvalue},
)
def load_data():
    data = pd.read_csv("forecast.csv")
    data["Time"] = pd.to_datetime(data["Time"])
    images = np.load("delft_novjan_128.npz")["arr_0"]

    y, x = np.ogrid[:128, :128]
    radius = 64
    mask = (x - 63.5) ** 2 + (y - 63.5) ** 2 <= radius**2

    # Step 4: Use the mask to extract the circular region from the original array
    masked_array = np.ma.array(
        images, mask=np.broadcast_to(~mask, images.shape)
    )

    return data, masked_array


data, images = load_data()


st.write(
    "Choose a date between 3rd November 2021 and 9th January 2022 to see the \
    solar forecasts based on sensor data, imagery, and their multi-modal combination"
)

# Set the minimum and maximum selectable dates
min_date = datetime(2021, 11, 3)
max_date = datetime(2022, 1, 9)

# Set the default date to the minimum date to ensure it is within the desired range
default_date = min_date

# Date selector for selecting the desired date within the range
selected_date = st.date_input(
    "Select a date:",
    min_value=min_date,
    max_value=max_date,
    value=default_date,
)

# Get the corresponding dataset based on the user's selection
selected_data_key = selected_date  # .strftime("%Y-%m-%d")
selected_data = data[data["Time"].dt.date == selected_data_key]
images_day = images[selected_data.index]
selected_data.reset_index(inplace=True)
images_xr = xr.DataArray(
    images_day,
    dims=("Time", " ", " "),
    coords={"Time": selected_data["Time"].dt.strftime("%H:%M")},
)

r2_meteo = r2_score(selected_data["Meteo"], selected_data["True"])
r2_img = r2_score(selected_data["Imagery"], selected_data["True"])
r2_mm = r2_score(selected_data["MM"], selected_data["True"])

rmse_meteo = np.sqrt(
    mean_squared_error(selected_data["Meteo"], selected_data["True"])
)
rmse_img = np.sqrt(
    mean_squared_error(selected_data["Imagery"], selected_data["True"])
)
rmse_mm = np.sqrt(
    mean_squared_error(selected_data["MM"], selected_data["True"])
)

# Create a line plot using Plotly's go.Scatter
fig = go.Figure()
# fig = make_subplots(rows=2, cols=1)
fig.add_trace(
    go.Scatter(
        x=selected_data["Time"],
        y=selected_data["True"],
        mode="lines",
        name="Ground Truth",
    ),
)
fig.add_trace(
    go.Scatter(
        x=selected_data["Time"],
        y=selected_data["MM"],
        mode="lines",
        name="Multi-Modal, R2 = {}".format(
            str(round(r2_mm, 3)),
            # str(round(rmse_mm, 3))
        ),
    ),
)
fig.add_trace(
    go.Scatter(
        x=selected_data["Time"],
        y=selected_data["Meteo"],
        mode="lines",
        name="Sensor Data, R2 = {}".format(
            str(round(r2_meteo, 3)),
            # str(round(rmse_meteo, 3))
        ),
    ),
)
fig.add_trace(
    go.Scatter(
        x=selected_data["Time"],
        y=selected_data["Imagery"],
        mode="lines",
        name="Sky Imagery, R2 = {}".format(
            str(round(r2_img, 3)),
            # str(round(rmse_img, 3))
        ),
    ),
)
fig.update_xaxes(rangeslider_visible=True)

# Customize the layout of the line plot
fig.update_layout(
    title=f"Solar Irradiance (W/m2) on {selected_data_key}",
    xaxis_title="Time",
    yaxis_title="Solar Irradiance (W/m2)",
    template="plotly_dark",
)

# Display the Plotly line plot
st.plotly_chart(fig, use_container_width=True)

# Load and display the corresponding image based on the user's selection
# st.write("Sky Imagery")

fig2 = px.imshow(
    images_xr,
    x=None,
    y=None,
    animation_frame="Time",
    aspect="equal",
    range_color=[0, 255],
    color_continuous_scale="blues_r",
)

# fig2.update_coloraxes(colorbar_title_text="Solar Irradiance (W/m2)")

# fig2.update_traces(
#     dict(showscale=False, coloraxis=None, colorscale="gray"),
#     # selector={"type": "heatmap"},
# )

# fig2.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
fig2.update_layout(coloraxis_showscale=False)
fig2.update_xaxes(
    showticklabels=False, ticks="", showgrid=False, zeroline=False
)
fig2.update_yaxes(
    showticklabels=False, ticks="", showgrid=False, zeroline=False
)

st.plotly_chart(fig2, use_container_width=True)
