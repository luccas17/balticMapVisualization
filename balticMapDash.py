import dash
from dash.dependencies import Input, Output, State
import pandas as pd
from plotly.graph_objects import *
from dash import html, dcc

data = pd.read_csv("https://luccas17.github.io/vegaliteBalticMap/data/odin2_2023-09-21_140419_comma.csv")

data["Date"] = pd.to_datetime(data["Month"], format="%m")


filteredData = data

groupedData = data.groupby(["Station name"], as_index=False).mean()
groupedData["Date"] = pd.to_datetime(groupedData["Month"], format="%m")

boxplot_temp_layout = {
    "height": 300, 
    "margin": {"r":20,"t":0,"l":20,"b":20},
    'xaxis': {
        'tickformat': '%b'
    }
}
boxplot_press_layout = {
    "height": 300, 
    "margin": {"r":20,"t":0,"l":20,"b":100},
    'xaxis': {
        'tickformat': '%b'
    }
}

def create_boxplot(boxplot_data, y_field):
    return Box(
        y = boxplot_data[y_field],
        x = boxplot_data["Date"],
        text = boxplot_data["Station name"]
    )

app = dash.Dash(__name__)

baltic_map_trace = Scattergeo(
    lon=groupedData["Longitude"],
    lat=groupedData["Latitude"],
    text=groupedData["Station name"],
    marker={
        "size": 7
    }
)

baltic_map = FigureWidget([baltic_map_trace])

# Documentation for layouts: https://plotly.com/python/reference/layout/geo/ & https://plotly.com/python/reference/layout/
baltic_map_layout = {
"geo": {
    "scope": "europe", 
    "domain": {
    "x": [0, 1], 
    "y": [0, 1]
    }, 
    "lataxis": {"range": [53.0, 63.0]}, 
    "lonaxis": {"range": [5.0, 25.0]}, 
    "showland": True, 
    "landcolor": "rgb(229, 229, 229)",
    "projection": {"type": "mercator"}, 
    "resolution": 50, 
    "countrycolor": "rgb(255, 0, 255)", 
    "coastlinecolor": "rgb(0, 255, 255)", 
    "showcoastlines": True,
    "showcountries": False
}, 
"legend": {"traceorder": "reversed"},
"margin": {
    "l": 0,
    "r": 0,
    "b": 50,
    "t": 50,
    "pad": 4,
    "autoexpand": False
},
"height": 400,
}

baltic_map.update_layout(baltic_map_layout)

boxplot_temp_trace = create_boxplot(data, "Temperature")

boxplot_temp = FigureWidget([boxplot_temp_trace])

boxplot_temp.update_layout(boxplot_temp_layout)

# Update the pressure boxplot 
boxplot_press_trace = create_boxplot(data, "Pressure")

boxplot_press = FigureWidget([boxplot_press_trace])

boxplot_press.update_layout(boxplot_press_layout)

# Update the histogram boxplot 
histogram_temp_trace = Histogram(
    x=data["Temperature"]
)

histogram_temp = FigureWidget([histogram_temp_trace])

app.layout = html.Div([  
    html.H1(children='Baltic Data', style={'textAlign':'center'}),
    html.Button('Reset plots', id='reset', n_clicks=0),
    # First Row: Baltic map and histogram side by side
    html.Div([
        html.Div([
            dcc.Graph(id='balticMap', figure=baltic_map),
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='histogram', figure=histogram_temp),
        ], style={'width': '50%', 'display': 'inline-block'}),
    ]),
    
    # Second Row: Two boxplots below each other
    html.Div([
        html.Div([
            dcc.Graph(id='boxplotTemperature', figure=boxplot_temp),
        ], style={'width': '100%'}),
        
        html.Div([
            dcc.Graph(id='boxplotPressure', figure=boxplot_press),
        ], style={'width': '100%'}),
    ]),
    dcc.Store(id='current-data'),
    dcc.Store(id='last-updated-data'),
    dcc.Store(id='last-updated', data="string")
])

@app.callback(
    Output('boxplotTemperature', 'figure', allow_duplicate=True),
    Output('boxplotPressure', 'figure', allow_duplicate=True),
    Output('histogram', 'figure', allow_duplicate=True),
    Output('balticMap', 'figure', allow_duplicate=True),
    Output('current-data', 'data', allow_duplicate=True),
    Output('last-updated', 'data', allow_duplicate=True),
    Output('last-updated-data', 'data', allow_duplicate=True),
    Input('reset', 'n_clicks'),
    prevent_initial_call=True
)
def reset_data(btn):
    # Update the baltic map graph
    groupedData = data.groupby(["Station name"], as_index=False).mean()
    baltic_map_trace = Scattergeo(
        lon=groupedData["Longitude"],
        lat=groupedData["Latitude"],
        text=groupedData["Station name"],
        marker={
            "size": 7
        }
    )
    baltic_map = FigureWidget([baltic_map_trace])
    baltic_map.update_layout(baltic_map_layout)
    
    # Update the pressure boxplot 
    boxplot_temp_trace = create_boxplot(data, "Temperature")
    boxplot_temp = FigureWidget([boxplot_temp_trace])
    boxplot_temp.update_layout(boxplot_temp_layout)

    # Update the pressure boxplot 
    boxplot_press_trace = create_boxplot(data, "Pressure")
    boxplot_press = FigureWidget([boxplot_press_trace])
    boxplot_press.update_layout(boxplot_press_layout)

    # Update the histogram boxplot 
    histogram_temp_trace = Histogram(
        x=data["Temperature"]
    )

    histogram_temp = FigureWidget([histogram_temp_trace])

    return boxplot_temp, boxplot_press, histogram_temp, baltic_map, data.to_json(), "none", data.to_json()

@app.callback(
    Output('boxplotTemperature', 'figure', allow_duplicate=True),
    Output('boxplotPressure', 'figure', allow_duplicate=True),
    Output('histogram', 'figure', allow_duplicate=True),
    Output('current-data', 'data', allow_duplicate=True),
    Output('last-updated', 'data', allow_duplicate=True),
    Output('last-updated-data', 'data', allow_duplicate=True),
    State('current-data', 'data'),
    State('last-updated', 'data'),
    State('last-updated-data', 'data'),
    Input('balticMap', 'selectedData'),
    prevent_initial_call=True
)
def balticMap_update_graphs(current_data, last_updated, last_updated_data, selectedDataBalticMap):
    # Get the filtered data based on the selected points
    if current_data is None:
        filteredData = data
    elif last_updated != "balticMap":
        filteredData = pd.read_json(current_data)
    else:
        filteredData = pd.read_json(last_updated_data)
    last_updated_data = filteredData
    if selectedDataBalticMap is not  None:
        groupedData = filteredData.groupby(["Station name"], as_index=False).mean()
        selectedPoints = selectedDataBalticMap["points"]
        selectedStations = list(groupedData.loc[[p["pointNumber"] for p in selectedPoints]]["Station name"])
        filteredData = filteredData[filteredData["Station name"].isin(selectedStations)] 
        filteredData["Date"] = pd.to_datetime(data["Month"], format="%m")
    
    # Update the temperature boxplot 
    boxplot_temp_trace = create_boxplot(filteredData, "Temperature")
    boxplot_temp = FigureWidget([boxplot_temp_trace])
    boxplot_temp.update_layout(boxplot_temp_layout)

    # Update the pressure boxplot 
    boxplot_press_trace = create_boxplot(filteredData, "Pressure")
    boxplot_press = FigureWidget([boxplot_press_trace])
    boxplot_press.update_layout(boxplot_press_layout)

    # Update the histogram boxplot 
    histogram_temp_trace = Histogram(
        x=filteredData["Temperature"]
    )
    histogram_temp = FigureWidget([histogram_temp_trace])

    return boxplot_temp, boxplot_press, histogram_temp, filteredData.to_json(), "balticMap", last_updated_data.to_json()

@app.callback(
    Output('boxplotTemperature', 'figure', allow_duplicate=True),
    Output('boxplotPressure', 'figure', allow_duplicate=True),
    Output('balticMap', 'figure', allow_duplicate=True),
    Output('current-data', 'data', allow_duplicate=True),
    Output('last-updated', 'data', allow_duplicate=True),
    Output('last-updated-data', 'data', allow_duplicate=True),
    State('current-data', 'data'),
    State('last-updated', 'data'),
    State('last-updated-data', 'data'),
    Input('histogram', 'selectedData'),
    prevent_initial_call=True
)
def histogram_update_graphs(current_data, last_updated, last_updated_data, selectedDataHistogram):
    if current_data is None:
        filteredData = data
    elif last_updated != "histogram":
        filteredData = pd.read_json(current_data)
    else:
        filteredData = pd.read_json(last_updated_data)
    last_updated_data = filteredData
    # Get the filtered data based on the selected points
    if selectedDataHistogram == {"points": []}:
        return dash.no_update, dash.no_update, dash.no_update, filteredData.to_json(), last_updated, last_updated_data.to_json()
    elif selectedDataHistogram is not None:
        selectedPoints = selectedDataHistogram["points"]
        filteredDataCorrectIndex = filteredData.reset_index(drop=True)
        selectedData = filteredDataCorrectIndex.loc[[points for p in selectedPoints for points in p["pointNumbers"]]]
        filteredData = selectedData
        filteredData["Date"] = pd.to_datetime(data["Month"], format="%m")

    # Update the temperature boxplot 
    boxplot_temp_trace = create_boxplot(filteredData, "Temperature")
    boxplot_temp = FigureWidget([boxplot_temp_trace])
    boxplot_temp.update_layout(boxplot_temp_layout)

    # Update the pressure boxplot 
    boxplot_press_trace = create_boxplot(filteredData, "Pressure")
    boxplot_press = FigureWidget([boxplot_press_trace])
    boxplot_press.update_layout(boxplot_press_layout)
    
    # Update the baltic map graph
    groupedData = filteredData.groupby(["Station name"], as_index=False).mean()
    baltic_map_trace = Scattergeo(
        lon=groupedData["Longitude"],
        lat=groupedData["Latitude"],
        text=groupedData["Station name"],
        marker={
            "size": 7
        }
    )
    baltic_map = FigureWidget([baltic_map_trace])
    baltic_map.update_layout(baltic_map_layout)

    return boxplot_temp, boxplot_press, baltic_map, filteredData.to_json(), "histogram", last_updated_data.to_json()

if __name__ == '__main__':
    app.run(debug=True)