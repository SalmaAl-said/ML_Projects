import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Load datasets
global_df = pd.read_csv('covid_19_clean_complete.csv')
country_df = pd.read_csv('country_wise_latest.csv')

# Preprocessing for the global dataset
total_cases = global_df['Confirmed'].sum()
total_deaths = global_df['Deaths'].sum()
total_recoveries = global_df['Recovered'].sum()

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("COVID-19 Dashboard", className="text-center mb-4")),
    ]),

    # Global Metrics
    dbc.Row([
        dbc.Col(dbc.Card([
            html.H3("Total Cases", className="text-center"),
            html.H4(f"{total_cases:,}", className="text-center text-danger")
        ]), width=4),
        dbc.Col(dbc.Card([
            html.H3("Total Deaths", className="text-center"),
            html.H4(f"{total_deaths:,}", className="text-center text-dark")
        ]), width=4),
        dbc.Col(dbc.Card([
            html.H3("Total Recoveries", className="text-center"),
            html.H4(f"{total_recoveries:,}", className="text-center text-success")
        ]), width=4),
    ], className="mb-4"),

    # Dropdown for country-specific data
    html.Div([
        html.Label("Select Country:", className="font-weight-bold"),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': 'Global', 'value': 'Global'}] +
                    [{'label': country, 'value': country} for country in country_df['Country/Region'].unique()],
            value='Global',
            placeholder="Select a country",
        )
    ], style={'width': '50%', 'margin': '0 auto'}),

    # Country-specific Metrics
    html.Div(id='country-metrics', style={'textAlign': 'center', 'marginTop': '20px'}),

    # Graphs
    dbc.Row([
        dbc.Col(dcc.Graph(id="cases-by-country"), width=6),
        dbc.Col(dcc.Graph(id="cases-over-time"), width=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="bar-chart"), width=6),
        dbc.Col(dcc.Graph(id="pie-chart"), width=6),
    ])
], fluid=True)

# Callbacks for interactivity
@app.callback(
    [
        Output('country-metrics', 'children'),
        Output('cases-by-country', 'figure'),
        Output('cases-over-time', 'figure'),
        Output('bar-chart', 'figure'),
        Output('pie-chart', 'figure')
    ],
    [Input('country-dropdown', 'value')]
)
def update_dashboard(country):
    if country == 'Global':
        filtered_df = global_df.copy()
        country_data = country_df[['Country/Region', 'Confirmed', 'Deaths', 'Recovered']].copy()
        metrics_text = [
            html.Div([
                html.H4("Global Metrics", className="text-primary"),
                html.P(f"Total Confirmed: {filtered_df['Confirmed'].sum():,}"),
                html.P(f"Total Deaths: {filtered_df['Deaths'].sum():,}"),
                html.P(f"Total Recovered: {filtered_df['Recovered'].sum():,}")
            ])
        ]
    else:
        filtered_df = global_df[global_df['Country/Region'] == country]
        country_data = country_df[country_df['Country/Region'] == country]
        metrics_text = [
            html.Div([
                html.H4(f"{country} Metrics", className="text-primary"),
                html.P(f"Total Confirmed: {country_data['Confirmed'].sum():,}"),
                html.P(f"Total Deaths: {country_data['Deaths'].sum():,}"),
                html.P(f"Total Recovered: {country_data['Recovered'].sum():,}")
            ])
        ]

    # Visualizations
    cases_by_country_fig = px.bar(country_data, x="Country/Region", y="Confirmed", title="Cases by Country")
    cases_over_time_fig = px.line(filtered_df, x="Date", y="Confirmed", title="Cases Over Time")
    bar_chart_fig = px.bar(country_data, x="Country/Region", y=['Confirmed', 'Deaths', 'Recovered'],
                           title=f"COVID-19 Cases in {country}",
                           labels={'value': 'Cases', 'variable': 'Type'},
                           barmode='group')
    pie_chart_fig = px.pie(
        values=[country_data['Confirmed'].sum(), country_data['Deaths'].sum(), country_data['Recovered'].sum()],
        names=['Confirmed', 'Deaths', 'Recovered'],
        title=f"Distribution of Cases in {country}"
    )

    return metrics_text, cases_by_country_fig, cases_over_time_fig, bar_chart_fig, pie_chart_fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
