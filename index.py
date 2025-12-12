import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash_bootstrap_templates import ThemeSwitchAIO

# Configurações
template_theme1 = "minty"
template_theme2 = "slate"
url_theme1 = dbc.themes.MINTY
url_theme2 = dbc.themes.SLATE
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"

app = dash.Dash(__name__, external_stylesheets=[url_theme1, dbc_css])
server = app.server

# Configurações Travadas (Igual ao Teste de Estabilidade)
config_travada = {"staticPlot": True, "displayModeBar": False}
main_config = {"hovermode": False, "dragmode": False, "margin": {"l":0, "r":0, "t":10, "b":0}, "legend": {"yanchor":"top", "y":0.9, "xanchor":"left", "x":0.1, "font":{"color":"white"}, "bgcolor": "rgba(0,0,0,0.5)"}}
tab_card = {'height': '100%'}

# ===== CARREGAMENTO BLINDADO (CSV LEVE) ====== #
try:
    df_barras = pd.read_csv("resumo_barras.csv")
    df_maxmin = pd.read_csv("resumo_maxmin.csv")
    
    df_barras['ANO'] = df_barras['ANO'].astype(str)
    df_maxmin['ANO'] = df_maxmin['ANO'].astype(str)
except Exception:
    df_barras = pd.DataFrame(columns=['ANO', 'REGIÃO', 'ESTADO', 'VALOR REVENDA (R$/L)'])
    df_maxmin = pd.DataFrame(columns=['ANO', 'max', 'min'])

# Listas
anos_disp = sorted(df_barras['ANO'].unique()) if not df_barras.empty else []
regioes_disp = df_barras['REGIÃO'].unique() if not df_barras.empty else []

val_ano = anos_disp[0] if anos_disp else ""
val_regiao = regioes_disp[0] if regioes_disp else ""

# Layout IDÊNTICO ao Teste de Estabilidade (Sem a parte de baixo)
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardBody([
                html.H4("Gasolina Dashboard", style={"font-weight": "bold"}),
                html.P("Igual ao Teste (Sem Linhas)"), # TÍTULO
                ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2]),
                dbc.Button("Portfólio", href="https://dashboard-fabio-gasolina.onrender.com", target="_blank", size="sm", style={'margin-top': '5px'})
            ])], style=tab_card)
        ], sm=12, md=3),
        dbc.Col([
            dbc.Card([dbc.CardBody([html.H5('Máximos e Mínimos'), dcc.Graph(id='static-maxmin', config=config_travada)])], style=tab_card)
        ], sm=12, md=3),
        dbc.Col([
            dbc.Card([dbc.CardBody([
                dbc.Row([
                    dbc.Col([html.H6('Ano:'), dcc.Dropdown(id="select_ano", value=val_ano, options=[{"label": x, "value": x} for x in anos_disp], clearable=False)], sm=6),
                    dbc.Col([html.H6('Região:'), dcc.Dropdown(id="select_regiao", value=val_regiao, options=[{"label": x, "value": x} for x in regioes_disp], clearable=False)], sm=6)
                ]),
                dbc.Row([
                    dbc.Col([dcc.Graph(id='regiaobar_graph', config=config_travada)], sm=12, md=6),
                    dbc.Col([dcc.Graph(id='estadobar_graph', config=config_travada)], sm=12, md=6)
                ])
            ])], style=tab_card)
        ], sm=12, md=6)
    ], className='g-2 my-2'),

    # REMOVI A PARTE DE BAIXO QUE PODE ESTAR CAUSANDO O "ESCORRIMENTO"
], fluid=True, style={'min-height': '100vh'}) # Garante tela cheia sem pular

# Callbacks
@app.callback(Output('static-maxmin', 'figure'), [Input(ThemeSwitchAIO.ids.switch("theme"), "value")])
def func(toggle):
    template = template_theme1 if toggle else template_theme2
    if df_maxmin.empty: return {}
    fig = px.line(df_maxmin, x='ANO', y=['max', 'min'], template=template)
    fig.update_layout(main_config, height=150, xaxis_title=None, yaxis_title=None, transition={'duration': 0})
    return fig

@app.callback(
    [Output('regiaobar_graph', 'figure'), Output('estadobar_graph', 'figure')],
    [Input('select_ano', 'value'), Input('select_regiao', 'value'), Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def graph1(ano, regiao, toggle):
    template = template_theme1 if toggle else template_theme2
    if df_barras.empty: return {}, {}
    
    df_filt = df_barras[df_barras['ANO'] == str(ano)]
    
    # Mantive a cor Laranja e Ordem Alfabética (Visual Misturado)
    dff_regiao = df_filt.groupby(['REGIÃO'])['VALOR REVENDA (R$/L)'].mean().reset_index().sort_values('REGIÃO', ascending=False)
    dff_estado = df_filt[df_filt['REGIÃO'] == regiao].sort_values('ESTADO', ascending=False)

    fig1 = px.bar(dff_regiao, x='VALOR REVENDA (R$/L)', y='REGIÃO', orientation='h', text_auto='.2f', template=template, color_discrete_sequence=['orange'])
    fig2 = px.bar(dff_estado, x='VALOR REVENDA (R$/L)', y='ESTADO', orientation='h', text_auto='.2f', template=template, color_discrete_sequence=['orange'])
    
    fig1.update_yaxes(categoryorder='category ascending')
    fig2.update_yaxes(categoryorder='category ascending')

    for fig in [fig1, fig2]:
        fig.update_layout(main_config, height=140, xaxis_title=None, yaxis_title=None, transition={'duration': 0})
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)
    return fig1, fig2

if __name__ == '__main__':
    app.run_server(debug=False)