import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np
from datetime import datetime

# import os
# os.chdir('./Poke-Battles')

pokemon_df = pd.read_csv('./raw-files/pokemon.csv')
pokemon_df = pokemon_df.melt(id_vars=['#', 'Name', 'Type 1', 'Type 2', 'Generation', 'Legendary'], var_name='Stat', value_name='Value')




app = dash.Dash("Pokemon Stats", external_stylesheets=[dbc.themes.SLATE])

app.layout = dbc.Container([
    dbc.Row([

        dbc.Col([
            html.H3("Select a stat to use as a color"),
            dcc.Dropdown(
                id = 'selected_stat',
                options=[{'label':i, 'value':i} for i in ['Type 1', 'Type 2', 'Generation', 'Legendary']],
                value='Legendary'
            ),
        ], md='auto'),

        dbc.Col([
            dcc.Graph(
                id='SwarmPlot',
            ),
        ], md='auto'),

        # dbc.Col([
        #
        # ], md='2'),

    ]),
], fluid=True)

@app.callback(
    Output('SwarmPlot', 'figure'),
    [Input('selected_stat', 'value')]
)
def update_swarmplot(color_stat):

    return px.strip(pokemon_df, y='Value', color=color_stat, facet_col='Stat', hover_data=['Name', 'Type 1', 'Type 2', 'Generation', 'Legendary'])

if __name__ == '__main__':
    app.run_server()
