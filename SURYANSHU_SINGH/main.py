'''
Render published dashboard link:
https://worldcupwinners-dashinterface.onrender.com/
'''

import numpy as np
import pandas as pd
from dash import Dash, html, dash_table, dcc, callback, Output, Input, MATCH, ALL
import plotly.express as px

#import data from csv file
df = pd.read_csv("worldcup_winners.csv")

app = Dash()
app.layout = [
    html.Div(className='row', children="World Cup Winners Throughout The Years (1930-2022)",
             style={'textAlign': 'center', 'color': 'gold', 'fontSize': 30}),
    html.Hr(),
    dcc.Dropdown(options=['All Data', 'Country', 'Year'], value='All Data', clearable=False, id='data-selector'),
    html.Div(id='secondary-data-selector'), #for 2nd dropdown menu
    html.Hr(),
    html.Div(id='display-data'),
    html.Div(id='choropleth-map')
]

# Controls for second dropdown menu for additional required options
@app.callback(
    Output(component_id='secondary-data-selector', component_property='children'),
    Input(component_id='data-selector', component_property='value')
)
def display_secondary(selected_value):
    if (selected_value == 'All Data'):
        return html.Div('No secondary dropdown needed.', style={'textAlign': 'center', 'color': 'blue', 'fontSize': 15})
    elif (selected_value == 'Country'):
        unique_countries = sorted(df['Winner'].unique())
        #print(f"Countries: {unique_countries}")
        return dcc.Dropdown(
            options=[c for c in unique_countries],
            placeholder='Select a country...',
            id={'type': 'dynamic-dropdown', 'index': 'country'}
        )
    elif (selected_value == 'Year'):
        years = sorted(df['Year'].dropna())
        return dcc.Dropdown(
            options=[y for y in years],
            placeholder='Select a year...',
            id={'type': 'dynamic-dropdown', 'index': 'year'}
        )

# Control the data shown on the dashboard after or before the dropdown interactions
@app.callback(
    Output(component_id='display-data', component_property='children'),
    Output(component_id='choropleth-map', component_property='children'),
    Input(component_id='data-selector', component_property='value'),
    Input(component_id={'type': 'dynamic-dropdown', 'index': ALL}, component_property='value'),
    prevent_initial_call=False
)
def display_data(primary, secondary):
    if (primary == 'All Data' or not secondary or secondary[0] is None): # All Data
        filtered_df = df
    else:
        selected = secondary[0]
        
        if (primary == 'Country'): # Country
            filtered_df = df[df['Winner'] == selected]
        elif (primary == 'Year'): # Year
            filtered_df = df[df['Year'] == selected]
        else:
            filtered_df = df

    data = dash_table.DataTable(data=filtered_df.to_dict('records'), page_size=15)

    wins = df['Winner'].value_counts().reset_index()
    wins.columns = ['Country', 'Wins']

    fig = px.choropleth(
        wins, locations='Country', color='Wins', range_color=[0, 5], hover_name='Country', locationmode='country names', projection='orthographic', width=1000, height=600
    )

    choropleth = dcc.Graph(figure=fig)

    return data, choropleth
'''
# Run the app
if __name__ == '__main__':
    app.run(debug=True)
'''
server = app.server