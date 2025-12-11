import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash_bootstrap_templates import ThemeSwitchAIO
import numpy as np # Importando numpy para gerar dados falsos

# ============ Configurações Iniciais ============ #
template_theme1 = "minty"
template_theme2 = "slate"
url_theme1 = dbc.themes.MINTY
url_theme2 = dbc.themes.SLATE
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"

app = dash.Dash(__name__, external_stylesheets=[url_theme1, dbc_css])
server = app.server

# ============ GERADOR DE DADOS (Substitui o CSV) ============ #
# Isso garante que o site NÃO VAI CRASHAR por erro de arquivo
dados_falsos = {
    'ANO': np.random.choice(['2018', '2019', '2020', '2021'], 100),
    'REGIÃO': np.random.choice(['NORTE', 'SUL', 'SUDESTE', 'NORDESTE', 'CENTRO OESTE'], 100),
    'ESTADO': np.random.choice(['SAO PAULO', 'RIO DE JANEIRO', 'MINAS GERAIS', 'BAHIA', 'AMAZONAS'], 100),
    'VALOR REVENDA (R$/L)': np.random.uniform(4.0, 7.0, 100),
    'DATA': pd.date_range(start='1/1/2018', periods=100)
}
df_main = pd.DataFrame(dados_falsos)
# Ajustes simples
df_main['VALOR REVENDA (R$/L)'] = df_main['VALOR REVENDA (R$/L)'].round(2)

# Listas para os filtros
anos_disp = sorted(df_main['ANO'].unique())
regioes_disp = df_main['REGIÃO'].unique()
estados_disp = df_main['ESTADO'].unique()

# Configuração de gráfico estático
config_travada = {"staticPlot": True, "displayModeBar": False}

# =========  Layout (Ultra Simples) =========== #
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2("TESTE DE ESTABILIDADE", style={"color": "red", "font-weight": "bold"}),
                    html.P("Se este texto estiver parado, o erro era o CSV."),
                    ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2])
                ])
            ], style={"margin-bottom": "20px"})
        ])
    ]),

    # Filtros
    dbc.Row([
        dbc.Col([
            html.Label("Selecione Ano"),
            dcc.Dropdown(id="select_ano", value=anos_disp[0], options=[{"label": x, "value": x} for x in anos_disp], clearable=False)
        ], md=6),
        dbc.Col([
            html.Label("Selecione Região"),
            dcc.Dropdown(id="select_regiao", value=regioes_disp[0], options=[{"label": x, "value": x} for x in regioes_disp], clearable=False)
        ], md=6)
    ], style={"margin-bottom": "20px"}),

    # Gráficos (Travados)
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardBody([html.H4("Gráfico 1"), dcc.Graph(id='grafico1', config=config_travada)])])
        ], md=6),
        dbc.Col([
            dbc.Card([dbc.CardBody([html.H4("Gráfico 2"), dcc.Graph(id='grafico2', config=config_travada)])])
        ], md=6)
    ])
], fluid=True, style={'padding': '20px'})

# ======== Callbacks Simples ========== #
@app.callback(
    [Output('grafico1', 'figure'), Output('grafico2', 'figure')],
    [Input('select_ano', 'value'), Input('select_regiao', 'value'), Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def atualizar_graficos(ano, regiao, toggle):
    template = template_theme1 if toggle else template_theme2
    
    # Filtragem simples
    dff = df_main[df_main['ANO'] == str(ano)]
    
    # Gráfico 1 - Barras
    fig1 = px.bar(dff, x='VALOR REVENDA (R$/L)', y='ESTADO', orientation='h', template=template)
    fig1.update_layout(transition={'duration': 0}) # Sem animação
    
    # Gráfico 2 - Scatter
    fig2 = px.scatter(dff, x='DATA', y='VALOR REVENDA (R$/L)', template=template)
    fig2.update_layout(transition={'duration': 0}) # Sem animação

    return fig1, fig2

if __name__ == '__main__':
    app.run_server(debug=False)
