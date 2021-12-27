#!/bin/env python
import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import argparse
import plotly.express as px
import os
import datetime as dt
from utils.dashboard_util import *
from utils.query_utils import *

# REQUIRED for dashboard to work on atg-dash VM
from dashboard import app

server = app.server
stats_file = "try.csv"
# stats_file = "TEST/results_sme_nano_vl_4_cpu_go_gm_nano_binaries_sve_bet0.1_2021.10.11_120121.csv"
# Load csv into DataFrame
df = pd.read_csv(stats_file)
# Global Variables
STATS = df["Stat"].unique().tolist()
# Here Benchmarks implies Tests
BENCHMARKS = df["Tests"].unique().tolist()


# Layout

layout = html.Div(
    [
        html.Div(
            [
                html.H4("Stats", style={"color": "#2d598e", "textAlign": "center"}),
                dcc.Dropdown(
                    id="stats_dropdown",
                    multi=True,
                    options=[{"label": i, "value": i} for i in STATS],
                    value=[],
                    searchable=True,
                    placeholder='Please Select..',
                    className='select_box',
                    clearable=True
                ),
            ],
            style={"width": "40%", "display": "inline-block"},
        ),
        html.Div(
            [
                html.H4(
                    "Benchmarks", style={"color": "#2d598e", "textAlign": "center"}
                ),
                dcc.Dropdown(
                    id="benchmarks_dropdown",
                    multi=True,
                    options=[{"label": i, "value": i} for i in BENCHMARKS],
                    value=[],
                    placeholder='Please Select..',
                    searchable=True,
                    clearable=True,
                    className='select_box'
                ),
            ],
            style={"width": "40%", "display": "inline-block"},
        ),
        html.Br(),
        html.Br(),
        html.Div(id="graphs_container", children=[]),
        
    ]
)
# Return a List of dcc graph objects
@app.callback(
    dash.dependencies.Output("graphs_container", "children"),
    [
        dash.dependencies.Input("stats_dropdown", "value"),
        dash.dependencies.Input("benchmarks_dropdown", "value"),
    ],
)
def return_list_of_graphs(stats_selected, benchmarks_selected):
    df = pd.read_csv(stats_file)
    dcc_graph_items = []

    # Filter Stats
    if not stats_selected:
        stats_selected = STATS
    df = df[df["Stat"].isin(stats_selected)]

    # Filter benchmarks
    if not benchmarks_selected:
        benchmarks_selected = BENCHMARKS
    df = df[df["Tests"].isin(benchmarks_selected)]

    for stat in stats_selected:
        selected_stat = stat
        df_loop = df[df["Stat"] == selected_stat]
        cols_legend = df_loop.columns[2:]
        df_loop.dropna(subset=cols_legend, inplace=True, axis=0, how="all")

        # If df_loop is empty, use unfiltered df
        if df_loop.empty:
            df_loop = df

        fig = px.bar(
            df_loop,
            x="Tests",
            y=cols_legend,
            barmode="group",
            height=500,
            labels={
                "value": "Difference%",
                "variable": "Configurations",
                "Tests": "Benchmarks",
            },
            title="Stat : " + selected_stat,
        )

        # Put into a div for easier customization
        dcc_graph_object = html.Div(
            id="div_id_" + stat,
            children=[dcc.Graph(id=stat, figure=fig)],
            style={"border": "2px blue solid"},
        )

        # Append to out list of these graph objects
        dcc_graph_items.append(dcc_graph_object)

    return dcc_graph_items

app.layout = layout
if __name__ == "__main__":
    port = int(8880)
    print_html_path(port=port)
    app.run_server(debug=False, port=port, host="0.0.0.0")
