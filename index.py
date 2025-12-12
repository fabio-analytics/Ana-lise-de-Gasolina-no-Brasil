import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash_bootstrap_templates import ThemeSwitchAIO
import gc # Coletor de lixo para limpar memória

# ============ Configurações Iniciais ============ #
template_theme1 = "minty"
template_theme2 = "slate"
url_theme1 = dbc.themes.MINTY
url_theme2 = dbc.themes.SLATE
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"

app = dash.Dash(__name__, external_stylesheets=[url_theme1, dbc_css])
server = app.server

# Configurações de travamento visual
config_travada = {"staticPlot": True, "displayModeBar": False}
tab_card = {'height': '100%'}
main_config = {
    "hovermode": False, 
    "dragmode": False,
    "legend": {"yanchor":"top", "y":0.9, "xanchor":"left", "x":0.1, "title": {"text": None}, "font" :{"color":"white"}, "bgcolor": "rgba(0,0,0,0.5)"},
    "margin": {"l":0, "r":0, "t":10, "b":0}
}

# ===== CARREGAMENTO INTELIGENTE (RESUMO) ====== #
try:
    print("Lendo dados...")
    df_raw = pd.read_parquet("data_gas_otimizado.parquet")
    
    # --- TRUQUE DE MESTRE: CRIAR RESUMOS E DELETAR O PESADO ---
    
    # 1. Resumo para os Gráficos de Barra (Muito leve)
    # Agrupa por Ano, Região e Estado de uma vez só
    df_resumo = df_raw.groupby(['ANO', 'REGIÃO', 'ESTADO'])['VALOR REVENDA (R$/L)'].mean().reset_index()
    
    # 2. Resumo para Máximos e Mínimos (Levíssimo)
    df_maxmin = df_raw.groupby(['ANO'])['VALOR REVENDA (R$/L)'].agg(['max', 'min']).reset_index()
    
    # 3. Resumo para Gráfico de Linha (Só média mensal para não pesar)
    # Cria uma coluna Mês/Ano para agrupar e reduzir pontos
    df_raw['DATA'] = pd.to_datetime(df_raw['DATA'])
    df_raw['MES_ANO'] = df_raw['DATA'].dt.to_period('M').astype(str)
    df_linha = df_raw.groupby(['MES_ANO', 'ESTADO'])['VALOR REVENDA (R$/L)'].mean().reset_index()
    
    # 4. JOGA FORA O ARQUIVO PESADO DA MEMÓRIA
    del df_raw
    gc.collect() # Faxina na memória RAM
    print("Dados pesados deletados. Rodando apenas com resumos.")

except Exception as e:
    print(f"Erro: {e}")
    df_resumo = pd.DataFrame(columns=['ANO', 'REGIÃO', 'ESTADO', 'VALOR REVENDA (R$/L)'])
    df_maxmin = pd.DataFrame(columns=['ANO', 'max', 'min'])
    df_linha = pd.DataFrame(columns=['MES_ANO', 'ESTADO', 'VALOR REVENDA (R$/L)'])

# Listas para filtros (usando o resumo leve)
anos_disp = sorted(df_resumo['ANO'].unique()) if not df_resumo.empty else []
regioes_disp = df_resumo['REGIÃO'].unique() if not df_resumo.empty else []
estados_disp = df_resumo['ESTADO'].unique() if not df_resumo.empty else []

val_ano = anos_disp[0] if len(anos_disp) > 0 else ""
val_regiao = regioes_disp[0] if len(regioes_disp) > 0 else ""
val_est1 = estados_disp[0] if len(estados_disp) > 0 else ""
val_est2 = estados_disp[1] if len(estados_disp) > 1 else ""


# =========  Layout =========== #
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Gasolina Dashboard", style={"font-weight": "bold"}),
                    html.P("Modo Ultra Leve (Resumido)"), # TÍTULO NOVO
                    ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2]),
                    dbc.Button("Portfólio", href="https://dashboard-fabio-gasolina.onrender.com", target="_blank", size="sm", style={'margin-top': '5px'})
                ])
            ], style=tab_card)
        ], sm=12, md=3),
        dbc.Col([
            dbc.Card([dbc.CardBody([html.H5('Máximos e Mínimos'), dcc.Graph(id='static-maxmin', config=config_travada)])], style=tab_card)
        ], sm=12, md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([html.H6('Ano:'), dcc.Dropdown(id="select_ano", value=val_ano, options=[{"label": x, "value": x} for x in anos_disp], clearable=False)], sm=6),
                        dbc.Col([html.H6('Região:'), dcc.Dropdown(id="select_regiao", value=val_regiao, options=[{"label": x, "value": x} for x in regioes_disp], clearable=False)], sm=6)
                    ]),
                    dbc.Row([
                        dbc.Col([dcc.Graph(id='regiaobar_graph', config=config_travada)], sm=12, md=6),
                        dbc.Col([dcc.Graph(id='estadobar_graph', config=config_travada)], sm=12, md=6)    
                    ])
                ])
            ], style=tab_card)
        ], sm=12, md=6)
    ], className='g-2 my-2'),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5('Histórico por Estado (Mensal)'),
                    dcc.Dropdown(id="select_estados0", value=[val_est1, val_est2], multi=True, options=[{"label": x, "value": x} for x in estados_disp]),
                    dcc.Graph(id='animation_graph', config=config_travada)
                ])
            ], style=tab_card)
        ], md=8),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5('Comparação Direta'),
                    dbc.Row([
                        dbc.Col([dcc.Dropdown(id="select_estado1", value=val_est1, options=[{"label": x, "value": x} for x in estados_disp], clearable=False)]),
                        dbc.Col([dcc.Dropdown(id="select_estado2", value=val_est2, options=[{"label": x, "value": x} for x in estados_disp], clearable=False)])
                    ]),
                    dcc.Graph(id='direct_comparison_graph', config=config_travada)
                ])
            ], style=tab_card)
        ], md=4)
    ], className='g-2 my-2')
], fluid=True)

# ======== Callbacks (Usando apenas os RESUMOS) ========== #
@app.callback(
    Output('static-maxmin', 'figure'),
    [Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def func(toggle):
    template = template_theme1 if toggle else template_theme2
    if df_maxmin.empty: return go.Figure()
    
    # Usa a tabelinha pronta de max/min (instantâneo)
    fig = px.line(df_maxmin, x='ANO', y=['max', 'min'], template=template)
    fig.update_layout(main_config, height=150, xaxis_title=None, yaxis_title=None, transition={'duration': 0})
    return fig

@app.callback(
    [Output('regiaobar_graph', 'figure'), Output('estadobar_graph', 'figure')],
    [Input('select_ano', 'value'), Input('select_regiao', 'value'), Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def graph1(ano, regiao, toggle):
    template = template_theme1 if toggle else template_theme2
    if df_resumo.empty: return go.Figure(), go.Figure()
    
    # Filtra direto no resumo (super rápido)
    df_filtered = df_resumo[df_resumo.ANO == str(ano)]
    
    dff_regiao = df_filtered.groupby(['REGIÃO'])['VALOR REVENDA (R$/L)'].mean().reset_index().sort_values('REGIÃO', ascending=False)
    dff_estado = df_filtered[df_filtered.REGIÃO == regiao].sort_values('ESTADO', ascending=False)

    fig1 = px.bar(dff_regiao, x='VALOR REVENDA (R$/L)', y='REGIÃO', orientation='h', text_auto='.2f', template=template, color_discrete_sequence=['orange'])
    fig2 = px.bar(dff_estado, x='VALOR REVENDA (R$/L)', y='ESTADO', orientation='h', text_auto='.2f', template=template, color_discrete_sequence=['orange'])
    
    # Força ordem alfabética para não escorrer
    fig1.update_yaxes(categoryorder='category ascending')
    fig2.update_yaxes(categoryorder='category ascending')

    for fig in [fig1, fig2]:
        fig.update_layout(main_config, height=140, xaxis_title=None, yaxis_title=None, transition={'duration': 0})
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)
    return fig1, fig2

@app.callback(
    Output('animation_graph', 'figure'),
    [Input('select_estados0', 'value'), Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def animation_graph(estados, toggle):
    template = template_theme1 if toggle else template_theme2
    if df_linha.empty: return go.Figure()
    if not isinstance(estados, list): estados = [estados]
    
    mask = df_linha.ESTADO.isin(estados)
    # Usa o resumo mensal (df_linha) em vez do diário
    fig = px.line(df_linha[mask], x='MES_ANO', y='VALOR REVENDA (R$/L)', color='ESTADO', template=template)
    fig.update_layout(main_config, height=350, xaxis_title=None, transition={'duration': 0})
    return fig

@app.callback(
    Output('direct_comparison_graph', 'figure'),
    [Input('select_estado1', 'value'), Input('select_estado2', 'value'), Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def direct_comparison(est1, est2, toggle):
    template = template_theme1 if toggle else template_theme2
    if df_linha.empty: return go.Figure()
    
    df_final = df_linha[df_linha.ESTADO.isin([est1, est2])]
    fig = px.line(df_final, x='MES_ANO', y='VALOR REVENDA (R$/L)', color='ESTADO', template=template)
    fig.update_layout(main_config, height=350, xaxis_title=None, transition={'duration': 0})
    return fig

if __name__ == '__main__':
    app.run_server(debug=False)
