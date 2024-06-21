# Importing the necessary libraries
import pandas as pd
import plotly.express as px
import dash
from dash import Dash, html, dcc, dash_table, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dotenv import dotenv_values, load_dotenv
from sqlalchemy import create_engine
import os

# Environment variables
load_dotenv(dotenv_path='/Users/hande/Spiced/dashboard/token.env')

username = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PW')
host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
db_climate = os.getenv('DB_CLIMATE')

# Reading daily data from db
url = f'postgresql://{username}:{password}@{host}:{port}/{db_climate}'
engine = create_engine(url, echo=True)

sql = "SELECT date, city, lat, lon, country, avg_temp_c, max_temp_c, min_temp_c, max_wind_kph FROM mart_forecast_day"

df = pd.read_sql(sql,con=engine)
df = df.sort_values(by= ['city', 'date'], ascending= [True, True])

# Reading monthly data
sql_2 = "SELECT year_and_month, city, country, ROUND(avg_temp_c, 1) AS avg_temp_c, max_temp_c, min_temp_c, will_it_rain_days, will_it_snow_days FROM mart_forecast_month"
df_month = pd.read_sql(sql_2,con=engine)

# Reading ISO codes
iso = pd.read_csv('iso_codes.csv')


# Joining df & iso
df = pd.merge(df, iso, how= 'left', on= 'country')
df.rename(columns= {'alpha-3': 'iso_code'}, inplace= True)


# adding figures
fig1 = px.scatter(df, x= 'date', y= 'avg_temp_c', color= 'city',
                       width= 1000, height= 600,
                       title= 'Overview of Average Temperatures for 6 Cities')


graph1 = dcc.Graph(figure= fig1)

fig2 = px.choropleth(df, locations='iso_code', 
                    projection='orthographic',
                    scope='world',   #we are adding the scope as europe
                    color='avg_temp_c', locationmode='ISO-3', 
                    color_continuous_scale=px.colors.sequential.YlOrRd,
                    animation_frame= 'date',
                    width= 600, height= 600,
                    title= 'Avg. Temperatures of Cities Over The Year')

graph2 = dcc.Graph(figure=fig2)

fig3 = px.bar(df_month, x= 'year_and_month', y= 'will_it_rain_days', 
             color= 'city', barmode='group', orientation='v', 
             width= 1600, height= 600,
             labels={'year_and_month':'date', 'will_it_rain_days': 'number of rainy days'},
             title= 'Monthly Rainy Days')

graph3 = dcc.Graph(figure= fig3)

fig4 = px.line(df, x= 'date', y= 'avg_temp_c', color= 'city',
               width= 800, height= 500,
               title= 'Avg. Temperatures(C)',
               )

graph4 = dcc.Graph(figure= fig4)

fig5 = px.line(df, x= 'date', y= 'max_wind_kph', color= 'city',
                     width= 800, height= 500,
                     title= 'Max Wind (kph)')

graph5 = dcc.Graph(figure= fig5)

fig6 = px.bar(df_month[df_month['city'].isin(['Istanbul'])],
             x= 'max_temp_c',
             y= 'year_and_month',
             color= 'city',
             barmode= 'group',
             orientation = 'h',
             height= 600,
             width= 900,
             labels={'year_and_month':'date'},
             title= 'Max Temperatures for Istanbul vs',
             color_discrete_sequence=px.colors.qualitative.D3)

graph6 = dcc.Graph(figure= fig6)

fig7 = px.bar(df_month[df_month['city'].isin(['Istanbul'])],
             x= 'min_temp_c',
             y= 'year_and_month',
             color= 'city',
             barmode= 'group',
             orientation = 'h',
             height= 600,
             width= 900,
             labels={'year_and_month':'date'},
             title= 'Min Temperatures for Istanbul vs',
             color_discrete_sequence=px.colors.qualitative.D3)

graph7 = dcc.Graph(figure= fig7)

# adding dcc
dropdown = dcc.Dropdown(options= ['Bali', 'Berlin', 'Cairo', 'Florence', 'Goteborg', 'Istanbul'], value= 'Istanbul', clearable=False)
radio = dcc.RadioItems(options= ['Bali', 'Berlin', 'Cairo', 'Florence', 'Goteborg'])

# instanciate the app
app = dash.Dash(external_stylesheets=[dbc.themes.SUPERHERO])

server = app.server

# set app layout
app.layout = html.Div([html.H1('🌏🌤️ Weather Forecast Dashboard 🌟🌧️', style={'textAlign': 'center', 'color': 'white', 'marginBottom': '40px' , 'marginTop': '40px'}),
                       html.Div(html.P("We're looking for data between 01-07-2023 and 01-06-2024 for 6 cities."),
                                style= {'marginLeft': 40, 'marginRight': 25}), 
                       html.Div([html.Div('Overview of Average Temperatures', 
                                          style={'backgroundColor': '#FF007F', 'color': 'white', 'textAlign': 'center', 'fontSize': 26}),
                        html.Div([
                                dbc.Row([
                                    dbc.Col(html.Div(graph1, style={'display': 'flex', 'justifyContent': 'center'})),
                                    dbc.Col(html.Div(graph2, style={'display': 'flex', 'justifyContent': 'center'})),
                                    ])
                                ], style= {'marginLeft': '30px', 'marginRight': '30px'}),
                            ]),
                        html.Div([html.P('How Many Rainy Days in a Month?', style= {'backgroundColor': '#00CCCC', 'color': 'white', 'textAlign': 'center', 'fontSize': 26, 'marginTop': '30px'}),
                                  html.Div(graph3, style= {'display': 'flex', 'justifyContent': 'center'}),
                                  ]),
                        html.Div([html.P('Average Temperatures and Max Wind View For The Selected City', 
                                          style={'backgroundColor': '#FF00FF', 'color': 'white', 'textAlign': 'center', 'fontSize': 26, 'marginTop': '30px'}),
                        html.Div([
                            html.Label('Please select a city:', style= {'fontSize': 16, 'marginLeft': '10px'}),
                            html.Div(dropdown, style= {'marginLeft': '10px', 'marginBottom': '10px', 'width': '200px', 'color': 'black'}), 
                            ]),
                        html.Div([
                                dbc.Row([
                                    dbc.Col(html.Div(graph4, style={'display': 'flex', 'justifyContent': 'center'})),
                                    dbc.Col(html.Div(graph5, style={'display': 'flex', 'justifyContent': 'center'})),
                                    ])
                                ], style= {'marginLeft': '30px', 'marginRight': '30px'}), 
                            ]),
                        html.Div([
                            html.P('Comparison Of The Selected City With Istanbul', style= {'backgroundColor': 'coral', 'color': 'white', 'textAlign': 'center', 'fontSize': 26, 'marginTop': '30px'}),
                            html.Div([
                                html.Label('Please select a city for comparison:', style= {'fontSize': 16, 'marginLeft': '10px'}),
                                html.Div(radio, style= {'marginLeft': '10px', 'marginBottom': '10px', 'width': '200px'}),
                                html.Div([
                                    dbc.Row([
                                    dbc.Col(html.Div(graph6, style={'display': 'flex', 'justifyContent': 'center'})),
                                    dbc.Col(html.Div(graph7, style={'display': 'flex', 'justifyContent': 'center'})),
                                    ])
                                ], style= {'marginLeft': '30px', 'marginRight': '30px'}), 
                                ]),
                            ])
                        ])





# Output(component_id='my-output', component_property='children'),
# Input(component_id='my-input', component_property='value')

# decorator - decorate functions
@callback(
    Output(graph4, "figure"),
    Input(dropdown, "value"))
def update_temp_chart(city): 
    #mask =  # coming from the function parameter
    fig4 = px.line(df[df['city'] == city], x= 'date', y= 'avg_temp_c', color= 'city',
               width= 800, height= 500,
               title= 'Avg. Temperatures(C)',
               )
    return fig4

@callback(
    Output(graph5, "figure"),
    Input(dropdown, "value"))
def update_wind_chart(city): 
    #mask =  # coming from the function parameter
    fig5 = px.line(df[df['city'] == city], x= 'date', y= 'max_wind_kph', color= 'city',
               width= 800, height= 500,
               title= 'Max Wind (kph)',
               )
    return fig5 # whatever you are returning here is connected to the component property of the output

@callback(
    Output(graph6, "figure"),
    Input(radio, "value"))
def update_comparison_chart(city): 
    #mask =  # coming from the function parameter
    fig6 = px.bar(df_month[df_month['city'].isin(['Istanbul', city])],
             x= 'max_temp_c',
             y= 'year_and_month',
             color= 'city',
             barmode= 'group',
             orientation = 'h',
             height= 600,
             width= 900,
             labels={'year_and_month':'date'},
             title= f'Max Temperatures for Istanbul vs {city}',
             color_discrete_sequence=px.colors.qualitative.D3
             )      
    return fig6

@callback(
    Output(graph7, "figure"),
    Input(radio, "value"))
def update_comparison_min_chart(city): 
    #mask =  # coming from the function parameter
    fig7 = px.bar(df_month[df_month['city'].isin(['Istanbul', city])],
             x= 'min_temp_c',
             y= 'year_and_month',
             color= 'city',
             barmode= 'group',
             orientation = 'h',
             height= 600,
             width= 900,
             labels={'year_and_month':'date'},
             title= f'Min Temperatures for Istanbul vs {city}',
             color_discrete_sequence=px.colors.qualitative.D3
             )      
    return fig7

if __name__ == '__main__':
     app.run_server()


