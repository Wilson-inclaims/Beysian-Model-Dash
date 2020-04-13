# -*- coding: utf-8 -*-

# Author: Yiming Yu


from datetime import datetime

import urllib.parse
import warnings

# import plotly.graph_objects as go
from plotly import graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
from dash.dependencies import Input, Output, State
import colorlover as cl

import pandas as pd
import numpy as np

# TODO: KMeans hot shown in function
# from sklearn.preprocessing import StandardScaler, FunctionTransformer, MinMaxScaler
# TODO: add MinMax Scaler into modeling in a later version to improve the performance

from utils.util import *

# pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")
global start_time, end_time, request_count
start_time = 0.0
end_time = 0.0
request_count = 0
# external CSS stylesheets
external_stylesheets = [

    {'href': 'https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/cerulean/bootstrap.min.css',
     'rel': 'stylesheet',
     'integrity': 'sha384-T5jhQKMh96HMkXwqVMSjF3CmLcL1nT9//tCqu9By5XSdj7CwR0r+F3LTzUdfkkQf',
     'crossorigin': 'anonymous'
     },

    {
        'href': 'https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-wvfXpqpZZVQGK6TAh5PVlGOfQNHSoD2xbE+QkPxCAFlNEevoEH3Sl0sibVcOQVnN',
        'crossorigin': 'anonymous'
    }
]

# external JavaScript files
external_scripts = [
    {'src': 'https://bootswatch.com/_vendor/jquery/dist/jquery.min.js'},
    {'src': 'https://bootswatch.com/_vendor/popper.js/dist/umd/popper.min.js'},
    {'src': 'https://bootswatch.com/_vendor/bootstrap/dist/js/bootstrap.min.js'},
    {'src': 'https://bootswatch.com/_assets/js/custom.js'},
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# app = dash.Dash(__name__)


# app.css.config.serve_locally = True
# app.scripts.config.serve_locally = True
app.config.suppress_callback_exceptions = True

app.title = "Bayesian Regression"

color_scale = 'YlOrRd'
font_family = """-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji" """


content_left_4cols = dbc.Col(

    dbc.Card(children=[

        # first tab

        dbc.Form(children=[
            # component used for uploading the file with the data
            # TODO add style for each FormGroup into style.css

            html.H6(['Upload Data ',
                     html.I(
                         id="upload_file_info",
                         className="fa fa-info-circle",

                     )],
                    ),

            dbc.Tooltip(
                "Supported Data Format:      "
                "csv, xlsx, json, txt",
                target="upload_file_info",
            ),

            html.Br(),

            dbc.FormGroup([
                # dbc.Col(dbc.Label("Upload Dataset:"), width=4),
                dbc.Col(
                    dcc.Upload(id="uploaded_file",last_modified=123,
                               children=html.Div([
                                   html.P("Drag and Drop or ",
                                          style={"display": "inline"}),
                                   html.A("Select File",
                                          style={"display": "inline",
                                                 "text-decoration": "underline",
                                                 "cursor": "pointer"}),
                               ]),
                               style={"border": "1px dashed #D9D9D9",
                                      "border-radius": "5px",
                                      "text-align": "center",
                                      "height": "50px",
                                      "line-height": "50px",
                                      },
                               multiple=False), width=12),

            ], row=True),

            html.Br(),

            # *********************************************************************************
            # accordion,
            # *********************************************************************************

            html.Div(id='eda_sector', style={'display': 'none'},
                     children=[

                         html.H6(['Exploratory Data Analysis ',
                                  html.I(
                                      id="config_type_eda_info",
                                      className="fa fa-info-circle",

                                  )],
                                 ),

                         dbc.Tooltip(
                             "Assigning data types for each feature to be used in data exploration, a Target "
                             "must be assigned and should be the index column of the data and the label column",
                             target="config_type_eda_info",
                         ),

                         html.Br(),

                         html.Div(
                             dt.DataTable(
                                 id='raw_data_column_type_setting',
                                 editable=True,
                                 fixed_rows={'headers': True, 'data': 0},

                                 dropdown={

                                     'Type': {
                                         'options': [
                                             {'label': i, 'value': i}
                                             for i in ['Numeric', 'Categorical', 'Target']
                                         ], 'clearable': False

                                     }
                                 },

                                 style_table={
                                     # "padding": '30px',
                                     'width': '100%',
                                     'maxHeight': '300px',
                                     "overflow-y": "auto",
                                     "overflow-x": "auto",
                                     # 'margin-left':'10px'

                                 },
                                 style_cell={"text-align": "center",
                                             "font-family": font_family,
                                             'width': '100px',
                                             "font-size": "90%",
                                             'textOverflow': 'ellipsis',
                                             #                                                     'minWidth': '10px',
                                             #                                                     'maxWidth': '40px'
                                             },

                                 style_header={"text-align": "center",
                                               "font-family": font_family,
                                               "font-weight": "500",
                                               "font-size": "90%",
                                               'width': '100px',
                                               # "color": "white",
                                               "background-color": "#e9ecef",
                                               # "text-transform": "uppercase",
                                               }

                             ), className='dash-table-with-dropdown', ),

                         html.Br(),

                         dbc.Button("Run/Re-run EDA",
                                    id="start_eda",
                                    n_clicks=0,
                                    n_clicks_timestamp=123,
                                    block=True),

                     ]),

            # ****************************************************************************

            html.Div(id='attr_and_model_config', style={'display': 'none'},

                     children=[

                         html.Hr(),

                         html.H6(['Attribute Selection for Modeling ',
                                  html.I(id="config_attr_info",
                                         className="fa fa-info-circle")
                                  ]),

                         dbc.Tooltip(
                             "Assigning data types and weights (default=1) used in the clustering model",
                             target="config_attr_info",
                         ),

                         html.Br(),
                         # dcc.Checklist(id="select_all_rows",
                         #               options=[{'label': 'Select All', 'value': 1}],
                         #               value),
                         html.Div(
                             dt.DataTable(
                                 id='test_ctrl_selection_model_feature_tbl',

                                 editable=True,
                                 fixed_rows={'headers': True, 'data': 0},
                                 row_selectable="multi",
                                 selected_rows=[],
                                 dropdown={
                                     'Type': {
                                         'options': [
                                             {'label': i, 'value': i}
                                             for i in ['Numeric', 'Categorical', 'Target']
                                         ], 'clearable': False

                                     },
                                     'Prior': {
                                         'options': [
                                             {'label': i, 'value': i}
                                             for i in ["Normal", "Student T", "Skew Normal","Categorical"]
                                         ],
                                         'clearable': True,
                                         'value': 'Normal',
                                },

},

                                 style_table={
                                     # "padding": '30px',
                                     'width': '100%',
                                     'maxHeight': '300px',
                                     "overflow-y": "auto",
                                     # "overflow-x": "auto",

                                 },
                                 style_cell={"text-align": "center",
                                             "font-family": font_family,
                                             'width': '100px',
                                             "font-size": "90%",
                                             'textOverflow': 'ellipsis',
                                             #                                                     'minWidth': '10px',
                                             #                                                     'maxWidth': '40px'
                                             },

                                 style_header={"text-align": "center",
                                               "font-family": font_family,
                                               "font-weight": "500",
                                               "font-size": "90%",
                                               'width': '100px',
                                               # "color": "white",
                                               "background-color": "#e9ecef",
                                               # "text-transform": "uppercase",
                                               }

                             ), className='dash-table-with-dropdown'),

                         # html.Br(),

                         #                                       dbc.Button("Confirm & Continue",
                         #                                                  id="continue_to_cluster_analysis_tab",
                         #                                                  n_clicks=0,
                         #                                                  block=True

                         #                                                 ),

                         # html.Br(),
                         # ****************************************************************************


                         html.Div(id='modeling_tab',

                                  children=[
                                      html.Br(),

                                      html.H6(['Model Configuration ',
                                               html.I(id="config_model_info",
                                                      className="fa fa-info-circle")
                                               ],
                                              # style={"display": "none"}
                                              ),

                                      dbc.Tooltip(
                                          "Modify data preprocessing and modeling algorithm settings",
                                          target="config_model_info",
                                          style={"display": "none"}
                                      ),

                                      html.Br(),

                                      dbc.FormGroup(children=[
                                          dbc.Col(dbc.Label(["Train/Test Split: (under development)",
                                                             html.I(
                                                                 id="random_sampling_info",
                                                                 className="fa fa-question-circle",
                                                                 n_clicks=0
                                                             )
                                                             ]), width=5),
                                          dbc.Tooltip("training/testing set split",
                                                      target="random_sampling_info",
                                                      ),
                                          dbc.Col(dbc.RadioItems(id="cluster_random_sampling",
                                                                 value=0,
                                                                 options=[
                                                                     {"label": "True", "value": 1},
                                                                     {"label": "False", "value": 0}],

                                                                 inline=True
                                                                 ), width=7)
                                      ],
                                          row=True,
                                          style={"display": "none"}),
                                      # numeric input used for entering the size of the subsample

                                      html.Div(id="cluster_random_sampling_setting",
                                               style={"display": "none"}),

                                      # html.Br(),

                                      # radio buttons used for selecting the clustering algorithm
                                      dbc.FormGroup([
                                          dbc.Col(html.Label("Model Scaling:"), width=5),
                                          dbc.Col(dbc.RadioItems(id="scaling_option",
                                                                 value=3,
                                                                 options=[{"label": "Standard Scaling",
                                                                           "value": 1},
                                                                          {"label": "MinMax Scaling",
                                                                           "value": 2},
                                                                          {"label": "None",
                                                                           "value": 3}],
                                                                 # TODO: change the value name from number to string
                                                                 inline=False
                                                                 ), width=7),

                                      ],
                                          row=True,
                                          # style={"display": "inline-block"}
                                      ),

                                      html.Hr(),

                                      dbc.Button('Run/Re-run Regression',
                                                 id="start_modeling",
                                                 n_clicks=0,
                                                 n_clicks_timestamp=123,
                                                 block=True),

                                  ])

                     ])

        ],
            style={"margin": "30px"}
        ),

    ],
        style={
            # "display": "inline-block",
            # "vertical-align": "top",
            # "width": "30vw",
            "height": "870px",
            # "height": "100%",
            "overflow": "auto"
            # "margin": "0vw 0vw 2vw 0vw"
        }, className='card-scrollbar'
    ), width=4)

content_right_tabs1 = dbc.Tabs(id='output_tabs', children=[
    # tab 1 subtab 1
    dbc.Tab(tab_id='uploaded_data_tab',
            label="Uploaded Data",
            tab_style={"width": "33.33%"},
            label_style={'text-align': 'center', "font-weight": "500", },

            children=[
                html.Br(),
                html.Div(id="display_table", style={'width': '100%'}),
                # html.Label("Showing the first 10 rows of the data set:"),
            ], style={'margin': '30px'}
            ),

    # tab 1 subtab 2
    dbc.Tab(tab_id='eda_output',
            label="Exploratory Data Analysis",
            tab_style={"width": "33.33%"},
            label_style={'text-align': 'center', "font-weight": "500", },
            children=[
                
                
               html.Div(id='eda_children',
                        children=[
                            html.Br(),
                            html.Br(),
                            dbc.RadioItems(
                                options=[
                                    {"label": "Descriptive Statistics", "value": 1},
                                    {"label": "Correlation Matrix", "value": 2},
                                    {"label": "Histogram", "value": 3},
                                    {"label": "Scatter Plot", "value": 4},
                                ],
                                value=1,
                                id="eda_shown_contents",
                                inline=True,
                                style={'margin-left': '30px'}
                            ),

                            html.Hr(style={'margin-right': '30px', 'margin-left': '30px'}),

                            dcc.Loading([

                                html.Div(id='descriptive_stats',
                                         children=[

                                             html.H6('Descriptive Statistics of Numeric Features:'),
                                             html.Div(id="stats_data_table"),
                                             html.Br(),
                                             html.H6('Descriptive Statistics of Categorical Features:'),
                                             html.Div(id="cat_stats_data_table")],
                                         style={'margin': '30px'}),

                                html.Div(id='corr_matrix',  # label="Correlation Matrix"
                                         children=[

                                             dbc.Row([

                                                 dbc.Col(

                                                     dcc.Loading(html.Div(id="correlation_plot"), type='cube'),
                                                     width=9,
                                                     align="center"),

                                                 dbc.Col([

                                                     dbc.Label("Select Features:"),
                                                     dbc.FormText('Maximum 10 features for display', color='primary'),
                                                     html.Br(),
                                                     dcc.Dropdown(id="correlation_features",
                                                                  multi=True,
                                                                  searchable=True,
                                                                  clearable=True,
                                                                  placeholder="Select Features",
                                                                 style={'maxHeight':'500px','overflow':'auto'}),

                                                 ], width=3, align="start"),

                                             ])

                                         ],
                                         style={'margin': '30px'}),

                                html.Div(id='eda_histogram',  # label="Histograms"
                                         children=[

                                             dbc.Row([

                                                 dbc.Col(
                                                     dcc.Loading(html.Div(id="histogram_plot"), type="cube"),
                                                     width=9,
                                                     align="center"),

                                                 dbc.Col([

                                                     dbc.Label("Select a numeric feature:"),
                                                     dcc.Dropdown(id="histogram_features_num",
                                                                  multi=False,
                                                                  clearable=False),
                                                     html.Br(),
                                                     dbc.Label("# of Bins:"),
                                                     dbc.Input(id="histogram_bin",
                                                               value=5,
                                                               min=1,
                                                               type='number'

                                                               ),

                                                     html.Br(),
                                                     dbc.Label("Group by (categorical feature):"),
                                                     dcc.Dropdown(id="histogram_features_groupby",
                                                                  value="None",
                                                                  multi=False,
                                                                  clearable=False),

                                                 ], width=3, align="start"),

                                             ])
                                         ],
                                         style={'margin': '30px'}),

                                html.Div(id='eda_scatter',  # label="Scatter Plot",
                                         children=[

                                             # TODO: Add the third dropdown for group by color
                                             dbc.Row([
                                                 dbc.Col(
                                                     dcc.Loading(
                                                         html.Div(id="scatter_plot"),
                                                         type='cube'),
                                                     width=9,
                                                     align="center"),

                                                 dbc.Col([
                                                     # dropdown used for selecting the feature to plot on the X axis

                                                     dbc.Label("X-Axis:"),  # width=2),
                                                     dcc.Dropdown(id="scatter-x-axis",
                                                                  multi=False,
                                                                  clearable=False,
                                                                  placeholder="Select a Feature",

                                                                  ),
                                                     html.Br(),
                                                     # dropdown used for selecting the feature to plot on the Y axis
                                                     dbc.Label("Y-Axis:"),
                                                     dcc.Dropdown(id="scatter-y-axis",
                                                                  multi=False,
                                                                  clearable=False,
                                                                  placeholder="Select a Feature",
                                                                  ),
                                                     #                                                  html.Br(),
                                                     #                                                 # dropdown used for selecting the feature to plot on the Y axis
                                                     #                                               dbc.Label("Z-Axis:"),
                                                     #                                                                dcc.Dropdown(id="scatter-z-axis",
                                                     #                                                                             multi=False,
                                                     #                                                                             clearable=False,
                                                     #                                                                             placeholder="Select a Feature",
                                                     #                                                                            ),

                                                 ], width=3, align="start"),

                                             ])

                                         ],
                                         style={'margin': '30px'}),

                            ], type='cube')
                        ])

            ],

            ),

    dbc.Tab(tab_id='model_viz_tab',

            label="Model Summary & Download Result",
            tab_style={"width": "33.33%"},
            label_style={'text-align': 'center', "font-weight": "500", },
            children=[

                html.Div(id='result_summery_viz_children',children=[

                    html.Br(),


                    html.Div(id="results_summary_contents",
                             children=[
                                 dbc.Row(
                                     dbc.Col([
                                         dbc.Alert("Notice some variables' names might be modified for compatibility"),

                                         html.Div(id='model_setting_summary'),

                                         dbc.Card([
                                             dbc.CardHeader('Regression Estimators & Markov Chain Monte Carlo Summary'),
                                             dbc.CardBody([
                                                 dbc.Alert("Warning: Categorical variables will convert to "
                                                           "dummy variables.",
                                                           color="info"),
                                                 #dcc.Loading(html.Div(id="regression_visualization"
                                                                      # render html.Img from bayesian_regression
                                                                      #),
                                                             #type='cube'
                                                             #),
                                                 html.Div(id="regression_visualization"),
                                                 html.Div(
                                                        id = "progressbar_div",
                                                        children = [
                                                            dcc.Interval(id="progress-interval", n_intervals=0, interval=9000),
                                                            dbc.Progress(id="progress",style = {"height":"30px", "margin-bottom": "15px"}),
                                                        ]
                                                    ),
                                                 
                                                 dbc.Button("Detailed Posterior Distribution",
                                                            id='open_posterior_dist',
                                                            color='info',
                                                            n_clicks=0
                                                            ),
                                                 dbc.Modal([
                                                     dbc.ModalHeader("Detailed Posterior Distribution"),
                                                     html.Div(id="posterior_visualization"),
                                                     dbc.ModalFooter(
                                                         dbc.Button("Close", id="close_posterior_dist")
                                                     )],
                                                     id="modal_posterior_dist",
                                                     size="lg"
                                                 )
                                             ])
                                         ],
                                             color="light"),
                                         ],
                                         width=12
                                     )
                                 ),
                                 dbc.Row(
                                     dbc.Col(
                                         dbc.Card([
                                             dbc.CardHeader('Regression Coefficients'),
                                             dbc.CardBody([
                                                 html.Div(
                                                     id = "coff_table_div",
                                                     children = [
                                                         dt.DataTable(id="coefficient_table"),
                                                         ]
                                                 ),
                                                 html.Div(
                                                        id = "progressbar_table",
                                                        children = [
                                                            dcc.Interval(id="progress-table-interval", n_intervals=0, interval=9000),
                                                            dbc.Progress(id="progress-table",style = {"height":"30px",  "margin-bottom": "15px"}),
                                                        ]
                                                    ),
                                                 html.A(id="output_data_link",
                                                        target="_blank",
                                                        children=[
                                                            dbc.Button(children=
                                                                       [html.I(className="fa fa-download"),
                                                                        " Download Result"],
                                                                       # col-sm-1 fa-2x
                                                                       id="download_result_button",
                                                                       style={"vertical-align": "middle",
                                                                              "cursor": "pointer"},
                                                                       ),
                                                        ],
                                                        # className="row"
                                                        style={"display": "inline-block",
                                              "width": "15%"}
                                                        ),
                                                 html.Div(id='download_results_children',
                                                          children=[
                                                              html.Br(style={'height': '50px'}),
                                                              dt.DataTable(
                                                                  id="display_cluster_table",
                                                                  fixed_rows={'headers': True, 'data': 0},
                                                                  # editable=False,
                                         # filter_action="native",
                                         #                          sort_action="native",
                                         #                          sort_mode="multi",
                                                                  style_table={
                                             'width': '100%',
                                             'maxHeight': '430px',
                                             "overflow-y": "auto",
                                             # "overflow-x": "auto",
                                             'margin-top': '10px',
                                             'margin-bottom': '20px',
                                         },
                                                                  style_cell={"text-align": "center",
                                                     "font-family": font_family,
                                                     'width': '100px',
                                                     'textOverflow': 'ellipsis',
                                                     "font-size": "90%",
                                                     },
                                                                  style_header={"text-align": "center",
                                                       "font-family": font_family,
                                                       "font-weight": "500",
                                                       "font-size": "90%",
                                                       "width": "100px",
                                                       "background-color": "#e9ecef",
                                                       # "text-transform": "uppercase",
                                                       }
                                                              ),
                                                          ],
                                                          style={'margin': '30px',
                                                                 'display': 'none'})
                                             ])
                                         ],
                                             color="light"),
                                         width=12
                                     )
                                 ),
                             ]),
                ],
                         style={'margin': '30px'})

            ]),
],
                               style={'width': '100%',
                                      'height': '100%'}
                               )

# second tab


app.layout = html.Div(children=[

    # header
    html.Nav(
        className="navbar navbar-expand-lg navbar-dark bg-navyblue",
        children=[
            html.A(
                html.H3('Bayesian Regression',
                        style={'color': 'white'}),
            ),
        ],
    ),

    dbc.Row([content_left_4cols,

             dbc.Col(id='content_right_8',children=[

                 dbc.Card(children=[

                     html.Div(id="initial_instructor",
                              children=[

                                  html.Label(children=["Please upload a file to start"],
                                             style={"display": "block",
                                                    "font-size": "120%",
                                                    "color": "#BDBDBD",
                                                    "margin-top": "22.5vw",
                                                    "text-align": "center"}),
                              ],
                              ),

                     html.Div(id="data_output", children=[content_right_tabs1], style={'display': 'none'}),

                 ],
                     style={'width': '100%',
                            "height": "870px"
                            }
                 )

             ], width=8,

             )
             ], style={'margin-left': '0.3rem', 'margin-right': '0.3rem', 'margin-top': '1rem'}

            ),

    # hidden divs used for storing the data shared across callbacks
    html.Div(id="uploaded_data", style={"display": "none"}),
    dt.DataTable(id='final_model_data', style_table={'display': 'none'}),
    html.Div(id="clustered_data", style={"display": "none"}),
    html.Div(id="plot_data", style={"display": "none"}),
    html.Div(id="target_feature", style={"display": "none"}),
    html.Div(id="dependent_variable_list", style={"display": "none"}),
    html.Div(id='prior_distribution_list', style={'display': 'none'})
])



@app.callback([Output("initial_instructor", "style"),
               Output("data_output", "style"),
               Output('eda_sector', 'style')],
              [Input("uploaded_data", "children")])
def load_file(uploaded_data):
    if not uploaded_data:
        return [{}, {'display': 'none'}, {'display': 'none'}]
    else:
        return [{'display': 'none'}, {}, {}]


# @app.callback(Output('control_tabs', 'active_tab'),               

#               [Input("continue_to_cluster_analysis_tab", "n_clicks")])
# def load_file(n_clicks):
#     if n_clicks>0:
#         return 'modeling_tab'


@app.callback([Output('eda_children', 'style'),
               Output('result_summery_viz_children','style')],
              [Input("uploaded_file", "last_modified"),
              Input('start_eda','n_clicks'),
              Input('start_modeling','n_clicks')
              ])
def update_visualization(last_modified,eda_clicks,modeling_clicks):#,

    
    
    ctx = dash.callback_context


    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    
    print('button_id {}'.format(str(button_id)))
    if modeling_clicks>0:
        model_results_style={'margin':'30px'}
    else:
        model_results_style={'display':'none'}
        
        
    if eda_clicks>0:
        eda_style={}
    else:
        eda_style={'display':'none'}
    
  
    if button_id=='uploaded_file':
        return  [{'display':'none'},{'display':'none'}]
    else:
        return [eda_style, model_results_style]


@app.callback([Output("descriptive_stats", "style"),
               Output("corr_matrix", "style"),
               Output("eda_histogram", "style"),
               Output("eda_scatter", "style")
               ],
              [Input("eda_shown_contents", "value")])
def eda_content_display(value):
    if value == 1:
        return [{'margin': '30px'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}]
    elif value == 2:
        return [{'display': 'none'}, {'margin': '30px'}, {'display': 'none'}, {'display': 'none'}]
    elif value == 3:
        return [{'display': 'none'}, {'display': 'none'}, {'margin': '30px'}, {'display': 'none'}]
    else:
        return [{'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'margin': '30px'}]


@app.callback(Output("uploaded_data", "children"),
              [Input("uploaded_file", "contents")],
              [State("uploaded_file", "filename")])
def load_file(contents, file_name):
    if contents is not None:
        df_json = parse_contents(contents, file_name)  # .to_json(date_format='iso', orient='split')
        print(df_json)
        return df_json


@app.callback(Output("cluster_random_sampling_setting", "children"),
              [Input("cluster_random_sampling", "value")])
def random_sampling_setting(value):
    if value == 1:
        sampling_setting = dbc.FormGroup([
            dbc.Col(dbc.InputGroup([dbc.InputGroupAddon("Percentage:",
                                                        addon_type="prepend"),
                                    dbc.Input(id="cluster_sample_size",
                                              type="number",
                                              min=1,
                                              max=100,
                                              value=100,
                                              step=1
                                              )
                                    ], size="sm"), width=6),
        ], row=True)

    elif value == 0:
        sampling_setting = dbc.Col(dbc.Input(id="cluster_sample_size",
                                             type="number",
                                             value=100),
                                   style={"display": "none"})

    return html.Div([
        sampling_setting,

    ])



@app.callback(Output('output_tabs', 'active_tab'),
              [Input("start_eda", "n_clicks_timestamp"),
               Input("start_modeling", "n_clicks_timestamp")])
def rerun_eda_display(eda_timestamp, modeling_timestamp):
    if max(eda_timestamp, modeling_timestamp) > 123:
        if eda_timestamp > modeling_timestamp:

            return 'eda_output'
        else:
            return 'model_viz_tab'
    else:
        return 'uploaded_data_tab'
    

@app.callback([Output("stats_data_table", "children"),
               Output("cat_stats_data_table", "children"),
               Output('descriptive_stats', 'disabled'),
               Output('correlation_features', 'options'),
               Output('correlation_features', 'value'),
               Output('histogram_features_num', 'options'),
               Output('histogram_features_num', 'value'),
               Output('histogram_features_groupby', 'options'),
               Output('histogram_features_groupby', 'value'),
               Output("scatter-x-axis", "options"),
               Output("scatter-y-axis", "options"),
               Output("scatter-x-axis", "value"),
               Output("scatter-y-axis", "value"),
               Output('attr_and_model_config', 'style')
               ],
              [Input("start_eda", "n_clicks")],
              [State('raw_data_column_type_setting', 'data'),
               State("uploaded_data", "children")])
def run_eda(n_clicks, eda_feature_config_rows, all_data):
    if n_clicks > 0 and all_data:
        df = pd.read_json(all_data)

        eda_config_df = pd.DataFrame(eda_feature_config_rows)
        print(eda_config_df)
        selected_features_num = eda_config_df[eda_config_df.Type == 'Numeric']['Feature'].tolist()
        selected_features_cat = eda_config_df[eda_config_df.Type == 'Categorical']['Feature'].tolist()
        # create the table containing the descriptive statistics

        if selected_features_num:
            stats = df[selected_features_num].describe().transpose()
            stats = stats.astype(float).round(4)
            stats["feature"] = stats.index
            names = ["feature"]
            names.extend(list(stats.columns[stats.columns != "feature"]))
            stats = stats[names]
            stats.reset_index(drop=True, inplace=True)
        else:
            stats = pd.DataFrame()

        if selected_features_cat:
            cat_df_list = []
            for i in selected_features_cat:  # contanate here later!!!!!!!
                df_cat_stats = df[i].value_counts(dropna=True, sort=True).rename_axis('unique_values').reset_index(
                    name='counts')
                df_cat_stats['Feature'] = i
                cat_df_list = cat_df_list + [df_cat_stats]

            his_groupby_features_options = [{"value": "None", "label": "None"}]
            his_groupby_features_options_value = his_groupby_features_options[0]['label']
            his_groupby_features_options.extend([{"value": i, "label": i} for i in selected_features_cat])
            cat_df_com = pd.concat(cat_df_list)
            cat_df_com = cat_df_com[['Feature', 'unique_values', 'counts']]
            cat_df_com.columns = ['Feature', 'Value', 'Count']

        else:
            his_groupby_features_options = [{"value": "None", "label": "None"}]
            his_groupby_features_options_value = 'None'
            cat_df_com = pd.DataFrame()

        # num_stat_children = dbc.Table.from_dataframe(stats, striped=True, bordered=True, hover=True,size='sm')

        num_stat_children = dt.DataTable(
            data=stats.to_dict(orient="records"),
            columns=[{"id": x, "name": x} for x in list(stats.columns)],
            style_as_list_view=False,
            fixed_rows={'headers': True, 'data': 0},
            # sort_action="native",
            # sort_mode="multi",
            style_table={
                "maxHeight": "280px",
                "width": "100%",
                "overflow-y": "auto",
                # "overflow-x": "auto",
            },
            style_cell={"text-align": "center",
                        "font-family": font_family,
                        'width': '100px',
                        'textOverflow': 'ellipsis',
                        "font-size": "90%",
                        },
            style_header={"background-color": "#e9ecef",
                          "text-align": "center",
                          'width': '100px',
                          # "text-transform": "uppercase",
                          "font-family": font_family,
                          "font-weight": "500",
                          "font-size": "90%"
                          })

        cat_stat_children = dt.DataTable(
            data=cat_df_com.to_dict(orient="records"),
            columns=[{"id": x, "name": x} for x in list(cat_df_com.columns)],
            style_as_list_view=False,
            fixed_rows={'headers': True, 'data': 0},
            # sort_action="native",
            # sort_mode="multi",

            style_table={
                "maxHeight": "280px",
                "width": "100%",
                "overflow-y": "auto",
                # "overflow-x": "auto",
            },
            style_cell={"text-align": "center",
                        "font-family": font_family,
                        'width': '100px',
                        'textOverflow': 'ellipsis',
                        "font-size": "90%",
                        },
            style_header={"background-color": "#e9ecef",
                          "text-align": "center",
                          'width': '100px',
                          # "text-transform": "uppercase",
                          "font-family": font_family,
                          "font-weight": "500",
                          "font-size": "90%"}
        )

        corr_matrix_features_options = [{"value": i, "label": i} for i in
                                        selected_features_num]  # convert cat into dummy and add here!!!!

        # print("corr features")
        # print(corr_matrix_features_options)

        if selected_features_cat is None:
            return [num_stat_children, cat_stat_children, False,
                    corr_matrix_features_options, selected_features_num,
                    corr_matrix_features_options, his_groupby_features_options_value,
                    his_groupby_features_options,"None",
                    corr_matrix_features_options, corr_matrix_features_options,
                    selected_features_num[0], selected_features_num[-1], {}]
        elif selected_features_num is None:
            return [num_stat_children, cat_stat_children, False,
                    corr_matrix_features_options, selected_features_num,
                    corr_matrix_features_options, None,
                    his_groupby_features_options,"None",
                    corr_matrix_features_options, corr_matrix_features_options,
                    selected_features_num[0], selected_features_num[-1], {}]
        else:
            return [num_stat_children, cat_stat_children, False,
                    corr_matrix_features_options, selected_features_num,
                    corr_matrix_features_options, selected_features_num[0],
                    his_groupby_features_options,"None",
                    corr_matrix_features_options, corr_matrix_features_options,
                    selected_features_num[0], selected_features_num[-1], {}]
    else:
        return [[], [], True, [], [], [], [], [],"None", [], [], [], [], {'display': 'none'}]


@app.callback(Output("correlation_plot", "children"),
              [  # Input("processed_data", "children"),
                  Input("correlation_features", "value")],
              [State("uploaded_data", "children")])
def update_correlation_matrix(correlation_features, all_data):
    if all_data and correlation_features:
        df = pd.read_json(all_data)[correlation_features]

        if len(correlation_features) <= 10:
            sigma = df[correlation_features].corr()

        else:
            sigma = df.iloc[:, :10].corr()

        y = list(sigma.index)
        x = list(sigma.columns)
        z = np.nan_to_num(sigma.values)

        annotations = []
        for i in range(z.shape[0]):
            for j in range(z.shape[1]):
                annotations.append(dict(x=x[i], y=y[j], text=str(np.round(z[i, j], 2)), showarrow=False))

        layout = dict(annotations=annotations,
                      plot_bgcolor="white",
                      paper_bgcolor="white",
                      xaxis=dict(tickangle=30),
                      yaxis=dict(tickangle=0),

                      font=dict(size=12),  #
                      height=700,
                      width=800,
                      showlegend=False,
                      margin=dict(t=100, l=150, r=100, b=150, pad=5))  #

        traces = [go.Heatmap(z=z, x=x, y=y, zmin=-1, zmax=1, colorscale=color_scale)]

        figure = go.Figure(data=traces, layout=layout).to_dict()

        correlation_plot = dcc.Graph(figure=figure,
                                     config={'displayModeBar': False}
                                     )

        return correlation_plot

    else:

        return []


@app.callback(Output("histogram_plot", "children"),
              [Input("histogram_features_num", "value"),
               Input("histogram_features_groupby", "value"),
               Input('histogram_bin', 'value')],
              [State("uploaded_data", "children")])
def update_histogram(histogram_features, histogram_features_groupby, nbins, all_data):
    if all_data and histogram_features:

        layout = dict(
            title={
                'text': str(histogram_features),
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},

            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=600,
            width=700,
            bargap=0.1,
            font=dict(size=12),
            # margin=dict(t=100, l=100, r=100, b=100, pad=50),
            xaxis=dict(zeroline=False,
                       showgrid=True,
                       mirror=True,
                       linecolor="#d9d9d9",
                       tickangle=0),
            yaxis=dict(zeroline=False,
                       showgrid=True,
                       mirror=True,
                       linecolor="#d9d9d9",
                       tickangle=0),

        )

        if histogram_features_groupby != "None":
            # histogram_features.extend(histogram_features_groupby) # extend the features to include categorical variable
            useful_features = [histogram_features, histogram_features_groupby]
            df = pd.read_json(all_data)[useful_features]
            figure = go.Figure(layout=layout)
            # create a color list for displaying histogram with groupby
            color_list = cl.scales["9"]["div"]['PuOr']
            # repeat the color list
            color_list = color_list * int(len(df[histogram_features_groupby].unique())/len(color_list)+1)
           
            color_count = 0
            for i in df[histogram_features_groupby].unique():
                df_temp = df[df[histogram_features_groupby] == i]
                figure.add_trace(go.Histogram(
                    x=df_temp[histogram_features],
                    histnorm='',
                    name=str(i),
                    nbinsx=nbins,
                   # opacity=0.75,
                    marker_color=color_list[color_count],
                    # marker={"colorscale":"RdBu"}

                ))
                color_count += 1

            figure.update_layout(xaxis_title_text="Value",
                                 yaxis_title_text="Count",
                                 title={
                                     'text': str(histogram_features) + ' by ' + str(histogram_features_groupby),
                                     'y': 0.9,
                                     'x': 0.5,
                                     'xanchor': 'center',
                                     'yanchor': 'top'},

                                 # barmode='overlay',
                                 showlegend=True,
                                 font=dict(size=12),
                                 bargap=0.1,
                                 #                                  bargroupgap=0.1
                                 )

        else:
            df = pd.read_json(all_data)[[histogram_features]]

            traces = [go.Histogram(x=df[histogram_features],
                                   nbinsx=nbins,
                                   marker_color='#F99B0C'
                                   )]

            figure = go.Figure(data=traces, layout=layout)  # .to_dict()

        histogram_plot = [
            dcc.Graph(figure=figure,
                      config={'displayModeBar': False},
                      style={"height": "600px",
                             "width": "700px"}),
        ]

        return histogram_plot

    else:

        return []


@app.callback(Output("scatter_plot", "children"),
              [  # Input("processed_data", "children"),
                  Input("scatter-x-axis", "value"),
                  Input("scatter-y-axis", "value")],
              [State("uploaded_data", "children")])
def update_scatter_plot(x_axis, y_axis, all_data):
    if all_data and x_axis and y_axis:
        df = pd.read_json(all_data)[[x_axis] + [y_axis]]

        layout = dict(paper_bgcolor="white",
                      plot_bgcolor="white",
                      showlegend=False,
                      font=dict(size=12),
                      margin=dict(t=100, l=100, r=100, b=100, pad=10),
                      height=700,
                      width=800,
                      # font=dict(family="Open Sans", size=9),
                      xaxis=dict(zeroline=False,
                                 showgrid=False,
                                 mirror=True,
                                 linecolor="#d9d9d9",
                                 tickangle=0,
                                 title_text=str(x_axis)
                                 ),
                      yaxis=dict(zeroline=False,
                                 showgrid=False,
                                 mirror=True,
                                 linecolor="#d9d9d9",
                                 tickangle=0,
                                 title_text=str(y_axis)
                                 )
                      )

        traces = [go.Scatter(x=list(df[x_axis]),
                             y=list(df[y_axis]),
                             mode="markers",
                             hoverinfo="text",
                             # text=["ID: " + str(x) for x in list(df["index"])],
                             marker=dict(
                                 color='#F99B0C',
                                         # colorscale=color_scale,
                                         size=9,
                                         line=dict(width=1)))
                  ]
        figure = go.Figure(data=traces, layout=layout).to_dict()

        scatter_plot = dcc.Graph(figure=figure, config={'displayModeBar': False},
                                 style={"height": "700px", "width": "800px"}
                                 )

    else:

        scatter_plot = []

    return scatter_plot


@app.callback([
    Output("display_table", "children"),
    Output("raw_data_column_type_setting", "data"),
    Output("raw_data_column_type_setting", "columns"),
    # Output("test_ctrl_selection_model_feature_tbl", "selected_rows")
],
    [Input("uploaded_data", "children")])
def display_initial_table(all_data):
    if all_data:
        tbl_columns = [{'id': 'Feature', 'name': 'Feature', 'editable': False},
                       {'id': 'Type', 'name': 'Type | editable', 'presentation': 'dropdown'}]

        df_all = pd.read_json(all_data)
        print("Df_all",df_all)
        index_options = [{"value": i, "label": i} for i in df_all.columns]
        features_options = [{"value": i, "label": i} for i in df_all.columns]
        # process the missing values
        #         df[df == "-"] = np.nan
        #         df[df == "?"] = np.nan
        #         df[df == "."] = np.nan
        #         df[df == " "] = np.nan
        # df=df.dropna().reset_index(drop=True) # can change this part to a more customized manner later

        #         # include the indices in the first columns
        #         # TODO add user customized index options
        #         # TODO This one may need further modification to deal with some special cases
        #         # save the raw data in the hidden div
        #         raw_data = df.to_json(orient="split")

        #         # transform the categorical variables into dummy variables
        #         df = pd.get_dummies(df, dummy_na=False, drop_first=True)

        # create the list of features to be shown in the dropdown menu

        display_table = html.Div(
            [html.P('Data Set Size - # rows: {} | # columns: {}'.format(str(len(df_all)), str(len(df_all.columns)))),

             dbc.FormText('* Note: Only showing first 15 rows for reference', color='primary',
                          style={'margin-bottom': '10px'}),

             dt.DataTable(columns=[{"name": i, "id": i} for i in df_all.columns],
                          data=df_all.head(15).to_dict('records'),
                          editable=False,
                          style_as_list_view=False,
                          fixed_rows={'headers': True, 'data': 0},
                          style_table={
                              "maxHeight": "670px",
                              "width": "100%",
                              "overflow-y": "auto",
                              "overflow-x": "auto",
                          },
                          style_cell={"text-align": "center",
                                      "font-family": font_family,

                                      'width': '100px',
                                      "font-size": "90%",
                                      'textOverflow': 'ellipsis',
                                      },
                          style_header={"background-color": "#e9ecef",
                                        "text-align": "center",
                                        # "color": "white",
                                        'width': '100px',
                                        # "text-transform": "uppercase",
                                        "font-family": font_family,
                                        "font-weight": "500",
                                        "font-size": "90%",

                                        }
                          ),

             ], style={'margin-top': '50px',
                       'margin-left': '20px',
                       'margin-right': '20px'})

        test_ctrl_selection_model_feature_tbl = create_modeling_feature_tbl_from_uploaded_file(df=df_all)

        tbl_columns2 = [{'id': 'Feature', 'name': 'Feature', 'editable': False},
                        {'id': 'Type', 'name': 'Type', 'presentation': 'dropdown'}
                        ]

        return [display_table,
                test_ctrl_selection_model_feature_tbl.iloc[:, :2].to_dict('rows'), tbl_columns2,
                #                 test_ctrl_selection_model_feature_tbl.to_dict('rows'),
                #                 tbl_columns,
                ]

    else:

        return [[], pd.DataFrame().to_dict('rows'), [],
                #                 pd.DataFrame().to_dict('rows'),
                #                 [],
                ]


# *****************************************************************************************************

@app.callback([Output("test_ctrl_selection_model_feature_tbl", "data"),
               Output("test_ctrl_selection_model_feature_tbl", "columns")],
              [Input("raw_data_column_type_setting", "data"),
               Input("raw_data_column_type_setting", "columns")])
def parse_eda_table_to_model_config_table(data_rows, columns):
    if data_rows:

        df_all = pd.DataFrame(data_rows)
        tbl_columns = [{'id': 'Feature', 'name': 'Feature', 'editable': False},
                       {'id': 'Type', 'name': 'Type | editable', 'presentation': 'dropdown'},
                       {'id': 'Prior', 'name': 'Prior | Selection', 'presentation': 'dropdown'}]

        return [df_all.to_dict('rows'), tbl_columns]
    else:
        return [pd.DataFrame().to_dict('rows'), []]


# @app.callback([Output("")],
#               [Input("select_all_rows", "n_c")])


@app.callback([Output('model_setting_summary', 'children'),
               Output('final_model_data', 'data'),
               Output('dependent_variable_list', 'children'),
               Output('target_feature', 'children'),
               Output('prior_distribution_list', 'children'),
               Output("progress-interval","interval"),
               Output("progress-table-interval","interval")
              ],
              [Input("start_modeling", "n_clicks")],
              [State("uploaded_data", "children"),
               State('test_ctrl_selection_model_feature_tbl', 'data'),
               State('test_ctrl_selection_model_feature_tbl', 'selected_rows'),
               State('scaling_option', 'label')
               ])
def model_data_processing(n_clicks, all_data, feature_set_rows, selected_rows, scaling_opt):
    #print(feature_set_rows)
    interval = 12000
    prior_dist = list()
    global start_time, end_time, request_count
    if n_clicks > 0 and all_data:
        if len(selected_rows) > 0:
            df = pd.read_json(all_data)

            feature_set_df_selected = pd.DataFrame(feature_set_rows)
            feature_set_df_selected = feature_set_df_selected.iloc[selected_rows, :]

            print("FEATURE_SET_DF_SELECTED")
            print(feature_set_df_selected)
            print("END OF FEATURE_SET_DF_SELECTED")

            if len(feature_set_df_selected[feature_set_df_selected.Type == 'Target']) != 1:

                return [dbc.Alert('Please select only ONE column as the '
                                  'Target/Dependent/Response Variable.', color="danger"), [], [], [],[],[],[]]
            else:
                num_feature_df = feature_set_df_selected[feature_set_df_selected.Type == 'Numeric'][['Feature']]
                cat_feature_df = feature_set_df_selected[feature_set_df_selected.Type == 'Categorical'][['Feature']]
                target_col = feature_set_df_selected[feature_set_df_selected.Type == 'Target']['Feature'].tolist()[0]
                prior_dist_list = feature_set_df_selected.Prior.tolist()
                #prior_dist_dict[feature_set_df_selected.Type] = feature_set_df_selected.Prior
                for i in range(len(prior_dist_list)):
                    tmp_dict = dict()
                    tmp_dict[feature_set_df_selected.Type.tolist()[i]] = prior_dist_list[i]
                    prior_dist.append(tmp_dict)
                print("prior_dist_col")
                print(prior_dist)

                # TODO add data validation for target variable to be numeric only

                ##########################################

                alert_children = dbc.Card([dbc.CardHeader('Model Configuration'),
                                           dbc.CardBody([
                                               html.P('Selected Numeric Feature(s): ' + str(
                                                   num_feature_df['Feature'].tolist())),
                                               html.P('Selected Categorical Feature(s): ' + str(
                                                   cat_feature_df['Feature'].tolist())),
                                               html.P('Target Feature: ' + str(target_col)),
                                               html.P('Scaling Option: ' + str(scaling_opt))
                                           ])
                                           ],
                                          color="light")


                df, dependent_variable_list = process_data_for_modeling(df=df,
                                                                        target_col=target_col,
                                                                        numeric_feature_df=num_feature_df,
                                                                        cat_feature_df=cat_feature_df)
                print(target_col)
                for i in range(len(prior_dist)):
                    for type,prior in prior_dist[i].items():
                        if type == "Target":
                            if len(df) < 200 and len(feature_set_df_selected) < 5:
                                if str(prior) == "Normal":
                                    interval = 10000
                                elif str(prior) == "Student T":
                                    interval = 18000
                                elif str(prior) == "Skew Normal":
                                    interval = 22000
                            elif len(df) < 200 and len(feature_set_df_selected) >= 5:
                                if str(prior) == "Normal":
                                    interval = 12000
                                elif str(prior) == "Student T":
                                    interval = 20000
                                elif str(prior) == "Skew Normal":
                                    interval = 25000
                            elif len(df) >= 200 and len(feature_set_df_selected) < 5:
                                if str(prior) == "Normal":
                                    interval = int(float(15000) * (len(df)/200))####pass
                                elif str(prior) == "Student T":
                                    interval = int(float(50000) * (len(df)/200))
                                elif str(prior) == "Skew Normal":
                                    interval = int(float(70000) * (len(df)/200))
                            elif len(df) >= 200 and len(feature_set_df_selected) >= 5:
                                if str(prior) == "Normal":
                                    interval = int(float(18000) * (len(df)/200))
                                elif str(prior) == "Student T":
                                    interval = int(float(70000) * (len(df)/200))
                                elif str(prior) == "Skew Normal":
                                    interval = int(float(90000) * (len(df)/200))

                target_feature = str(target_col)
                print("Interval",interval)
                # *********************************************************************************************
                request_count = 0
                start_time = 0.0
                end_time = 0.0
                return [alert_children, df.to_dict('rows'), dependent_variable_list, target_feature, prior_dist,interval,interval]

        else:
            return [dbc.Alert([html.P('Please select features for modeling.')], color="danger"), [], [], [], [],[],[]]
    else:
        return [[], [], [], [], [],[],[]]


@app.callback([Output("coefficient_table", "data"),
               Output('coefficient_table', 'columns'),
               Output('regression_visualization', 'children'),
               Output('posterior_visualization', 'children'),
              ],
              [Input('final_model_data', 'data')],
              [State('dependent_variable_list', 'children'),
               State('prior_distribution_list', 'children'),
               State('target_feature', 'children'),
               State('scaling_option', 'value')
               ])
def modeling_and_visualization(data_rows, dependent_variable_list, prior_distribution_list, target_feature, scaling_opt):
    global start_time, end_time, request_count
    if data_rows:

        model_data = pd.DataFrame(data_rows)

        print("dependent variable list in toggle modal:")
        print(dependent_variable_list)
        print('Target Feature: ')
        print(target_feature)
        # print("Model Data:")
        # print(model_data)
        start_time = time.clock()
        print("###########################",start_time)
        trace_array, img_source, posterior_source = bayesian_regression_modeling(df=model_data,
                                                                                 label_col=dependent_variable_list,
                                                                                 target_col=target_feature,
                                                                                 prior_distribution_list=prior_distribution_list,
                                                                                 draw_sample=1000,
                                                                                 chains=2,
                                                                                 scaling_opt=scaling_opt,
                                                                                 )
        end_time = time.clock()
        
        coef_table = pm.summary(trace_array)
        coef_table_data = coef_table.T.loc[['mean'], :].to_dict('records')
        coef_table_columns = [{"name": i, "id": i} for i in coef_table.T.loc[['mean'], :].columns]

        print(coef_table_columns)

        regression_visualization = html.Img(src=img_source, style={'width': '100%'})
        
        posterior_dist = html.Img(src=posterior_source, style={'width': '100%'})

        print("###########################",end_time)
        return [coef_table_data, coef_table_columns, regression_visualization, posterior_dist]
    else:
        return [[], [], [], []]

@app.callback(
    [Output("progress","value"),Output("progress","children"),Output("progressbar_div","style"),Output("regression_visualization","style"),Output("coff_table_div","style")],
    [Input("progress-interval","n_intervals")]
    )
def regression_update_progress(n):
    global start_time, end_time, request_count
    
    if start_time == 0.0:
        return [1,"",{},{'display': 'none'},{'display': 'none'}]
    if end_time == 0.0:
          request_count += 1
          if request_count == 98:
              progress = 98
              request_count -= 1
              return [progress, f"{progress} %",{},{'display': 'none'},{'display': 'none'}]
          progress = min(request_count % 110, 98)
    else:
        progress = 100
        return [progress, f"{progress} %" ,{'display': 'none'},{},{}]     
    return [progress, f"{progress} %" ,{},{'display': 'none'},{'display': 'none'}]
 #{'display': 'none'}   
@app.callback(
    [Output("progress-table","value"),Output("progress-table","children"),Output("progressbar_table","style")],
    [Input("progress-table-interval","n_intervals")]
    )
def table_update_progress(n):
    global start_time, end_time, request_count
    
    if start_time == 0.0:
        return [1,"",{}]
    if end_time == 0.0:
          request_count += 1
          if request_count == 98:
              progress = 98
              request_count -= 1
              return [progress, f"{progress} %",{}]
          progress = min(request_count % 110, 98)
    else:
        progress = 100
        return [progress, f"{progress} %" ,{'display': 'none'}]     
    return [progress, f"{progress} %" ,{}]


@app.callback(Output('modal_posterior_dist', 'is_open'),
              [Input('open_posterior_dist', 'n_clicks'),
               Input('close_posterior_dist', 'n_clicks')],
              [State('modal_posterior_dist', 'is_open')])
def open_posterior_dist(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    else:
        return is_open


@app.callback([Output("output_data_link", "href"),
               Output("output_data_link", "download")],
              [Input("download_result_button", "n_clicks"),
               Input("coefficient_table", "data")])  # add algorithm name to file name!!!!!!!!!!!
def download_file(n_clicks, output_data):
    if output_data:
        # load the clustering results from the hidden div
        df = pd.DataFrame(output_data)  # , orient="split"
        # convert the table to csv
        csv = df.to_csv(index=False, encoding="utf-8")

        # create the file for download
        file_for_download = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv)

        # use the current time as the file name
        file_name = "regression_coefficients_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"

        return file_for_download, file_name
    else:
        return ['', '']


if __name__ == "__main__":
    app.run_server(port=8080, debug=False)
