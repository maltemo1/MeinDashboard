import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import math

# Daten einlesen
dateipfad = 'gesamter_Datensatz_nach_Land_sortiert.csv'  # Stelle sicher, dass sich die Datei im richtigen Verzeichnis befindet
all_sorted = pd.read_csv(dateipfad, encoding='utf-8')

# Sicherstellen, dass die Zeitraum-Spalte als Datum erkannt wird
all_sorted['Zeitraum'] = pd.to_datetime(all_sorted['Zeitraum'])
all_sorted['Jahr'] = all_sorted['Zeitraum'].dt.year
all_sorted['Monat'] = all_sorted['Zeitraum'].dt.month

# Gruppierung der Daten nach Jahr
gesamt_deutschland = all_sorted.groupby('Jahr').agg(
    gesamt_export=('Ausfuhr: Wert', 'sum'),
    gesamt_import=('Einfuhr: Wert', 'sum')
).reset_index()

gesamt_deutschland['gesamt_handelsvolumen'] = gesamt_deutschland['gesamt_export'] + gesamt_deutschland['gesamt_import']

def formatter(value):
    if value >= 1e9:
        return f'{value / 1e9:.1f} Mrd'
    elif value >= 1e6:
        return f'{value / 1e6:.1f} Mio'
    elif value >= 1e3:
        return f'{value / 1e3:.1f} K'
    else:
        return str(value)

# Dash-App erstellen
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Deutschlands Handelsentwicklung"),
    dcc.Graph(id='handel_graph'),
    dcc.Dropdown(
        id='jahr_dropdown',
        options=[{'label': str(j), 'value': j} for j in sorted(all_sorted['Jahr'].unique())],
        value=2024,
        clearable=False,
        style={'width': '50%'}
    ),
    dcc.Graph(id='monatlicher_handel_graph'),
])

@app.callback(
    Output('handel_graph', 'figure'),
    Input('handel_graph', 'id')
)
def update_graph(_):
    fig = go.Figure()
    for col, name, color in zip(
        ['gesamt_export', 'gesamt_import', 'gesamt_handelsvolumen'],
        ['Exportvolumen', 'Importvolumen', 'Gesamthandelsvolumen'],
        ['#1f77b4', '#ff7f0e', '#2ca02c']
    ):
        fig.add_trace(go.Scatter(
            x=gesamt_deutschland['Jahr'],
            y=gesamt_deutschland[col],
            mode='lines+markers',
            name=name,
            line=dict(width=2, color=color),
            hovertemplate=f'<b>{name}</b><br>Jahr: %{{x}}<br>Wert: %{{y:,.0f}} €'
        ))
    return fig

@app.callback(
    Output('monatlicher_handel_graph', 'figure'),
    Input('jahr_dropdown', 'value')
)
def update_monthly_graph(year_selected):
    df_year_monthly = all_sorted[all_sorted['Jahr'] == year_selected].groupby('Monat').agg(
        export_wert=('Ausfuhr: Wert', 'sum'),
        import_wert=('Einfuhr: Wert', 'sum')
    ).reset_index()
    df_year_monthly['handelsvolumen_wert'] = df_year_monthly['export_wert'] + df_year_monthly['import_wert']

    fig = go.Figure()
    for col, name, color in zip(
        ['export_wert', 'import_wert', 'handelsvolumen_wert'],
        ['Exportvolumen', 'Importvolumen', 'Gesamthandelsvolumen'],
        ['#1f77b4', '#ff7f0e', '#2ca02c']
    ):
        fig.add_trace(go.Scatter(
            x=df_year_monthly['Monat'],
            y=df_year_monthly[col],
            mode='lines+markers',
            name=name,
            line=dict(width=2, color=color),
            hovertemplate=f'<b>{name}</b><br>Monat: %{{x}}<br>Wert: %{{y:,.0f}} €'
        ))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
