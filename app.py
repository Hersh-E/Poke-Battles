import dash
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

from Chart_Functions.chord_diagram import poke_chord_diagram

# import os
# os.chdir('./Poke-Battles')

pokemon_df = pd.read_csv('./raw-files/pokemon.csv')
# pokemon_df = pokemon_df.melt(id_vars=['#', 'Name', 'Type 1', 'Type 2', 'Generation', 'Legendary'], var_name='Stat', value_name='Value')
pokemon_df.loc[pokemon_df['Type 2'].isna(), 'Type 2'] = 'None'



combats_df = pd.read_csv('./raw-files/combats.csv')
combats_df2 = combats_df.copy()
combats_df2.columns = ['Second_pokemon','First_pokemon','Winner']
combats_df = combats_df.append(combats_df2).drop_duplicates()
combats_df = pd.merge(combats_df,pokemon_df[['#', 'Type 1', 'Generation']],left_on='First_pokemon',right_on='#', how='left')
combats_df['First_Type'] = combats_df['Type 1']
combats_df['First_Gen'] = combats_df['Generation']
combats_df.drop(['#', 'Type 1', 'Generation'],axis=1,inplace=True)
combats_df = pd.merge(combats_df,pokemon_df[['#', 'Type 1', 'Generation']],left_on='Second_pokemon',right_on='#', how='left')
combats_df['Second_Type'] = combats_df['Type 1']
combats_df['Second_Gen'] = combats_df['Generation']
combats_df.drop(['#', 'Type 1', 'Generation'],axis=1,inplace=True)
combats_df['wins'] = combats_df['First_pokemon']==combats_df['Winner']
combats_df.loc[combats_df['wins']==True]


app = dash.Dash("Pokemon Stats", external_stylesheets=[dbc.themes.SLATE])

server = app.server

control1 = dbc.Card([
    dbc.FormGroup([
        dbc.Label("Select a stat to compare the generations"),
        dcc.Dropdown(
            id = 'selected_stat',
            options=[{'label':i, 'value':i} for i in ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']],
            value='HP',
        ),
    ]),
], body=True)

control2 = dbc.Card([
    dbc.FormGroup([
        dbc.Label("Select generations to compare battles"),
        dbc.Checklist(
            id = 'selected_gens',
            options=[{'label':'Generation ' + str(i), 'value':i} for i in [1, 2, 3, 4, 5, 6]],
            value=[1,2],
        ),
        dbc.Label("** select a chord or slice to see win percentages"),
    ]),
], body=True)

app.layout = dbc.Container([
    dbc.Row([

        dbc.Col([
            control1,
        ], md='3'),

        dbc.Col([
            dcc.Graph(
                id='SwarmPlot',
                style={"margin": "15px"},
            ),
        ], md='9'),

    ], align='center'),
    dbc.Row([

        dbc.Col([
            control2,
        ], md='3'),

        dbc.Col([
            dcc.Graph(
                id='chord_diagram',
                style={"margin": "15px"},
            ),
        ], md='9'),

    ], align='center'),
], fluid=True)

@app.callback(
    Output('SwarmPlot', 'figure'),
    [Input('selected_stat', 'value')]
)
def update_violinplot(stat):

    fig = px.violin(pokemon_df, y=stat, color='Generation', box=True, points='all', hover_data=['Name', 'Type 1', 'Type 2', 'Generation', 'Legendary'])
    fig.update_layout(
        autosize=False,
        width=900,
        height=500,
        dragmode=False)
    return fig


@app.callback(
    Output('chord_diagram', 'figure'),
    [Input('selected_gens', 'value')]
)
def update_chordplot(gens):
    graphable = combats_df.loc[(combats_df['First_Gen'].isin(gens)) & (combats_df['Second_Gen'].isin(gens))]

    combat_outcomes = graphable.groupby(['First_Type', 'Second_Type'],as_index=False).agg({'wins':'sum','First_pokemon':'count'})
    combat_outcomes.columns = ['First_Type', 'Second_Type','wins','matches']
    combat_outcomes['win_pct'] = combat_outcomes['wins']/combat_outcomes['matches']

    graphable = pd.pivot_table(combat_outcomes, values='win_pct', index=['First_Type'], columns=['Second_Type'], fill_value=0)

    fig = poke_chord_diagram(graphable)

    fig.update_layout(
        autosize=False,
        width=600,
        height=600,
        dragmode=False)

    return fig


if __name__ == '__main__':
    # app.run_server(debug=True, processes=1, threaded=True, host='127.0.01',port=8050, use_reloader=False)
    app.run_server
