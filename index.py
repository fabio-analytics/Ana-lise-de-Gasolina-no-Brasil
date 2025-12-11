import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash_bootstrap_templates import ThemeSwitchAIO

# ============ Configurações Iniciais ============ #
template_theme1 = "minty"
template_theme2 = "slate"
url_theme1 = dbc.themes.MINTY
url_theme2 = dbc.themes.SLATE
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"

app = dash.Dash(__name__, external_stylesheets=[url_theme1, dbc_css])
server = app.server

# ============ TRAVAMENTO TOTAL (Modo Imagem) ============ #
# staticPlot: True -> O gráfico vira uma imagem JPG fixa. Impossível se mexer.
config_travada = {"staticPlot": True, "displayModeBar": False}

tab_card = {'height': '100%'}
main_config = {
    "hovermode": "x unified",
    "legend": {"yanchor":"top", "y":0.9, "xanchor":"left", "x":0.1, "title": {"text": None}, "font" :{"color":"white"}, "bgcolor": "rgba(0,0,0,0.5)"},
    "margin": {"l":0, "r":0, "t":10, "b":0}
}

# ===== Carregamento de Dados (Global e Otimizado) ====== #
# Lendo os dados direto na memória do servidor (sem passar pelo navegador)
try:
    # Tenta ler assumindo separador padrão. Se der erro, ajuste conforme seu CSV real.
    df_main = pd.read_csv("data_gas.csv", low_memory=False)
except:
    df_main = pd.DataFrame() # Fallback para não quebrar o server

# Tratamento de Dados
if not df_main.empty:
    df_main.rename(columns={' DATA INICIAL': 'DATA INICIAL'}, inplace=True)
    df_main['DATA INICIAL'] = pd.to_datetime(df_main['DATA INICIAL'], errors='coerce')
    df_main['DATA FINAL'] = pd.to_datetime(df_main['DATA FINAL'], errors='coerce')
    df_main['DATA MEDIA'] = ((df_main['DATA FINAL'] - df_main['DATA INICIAL'])/2) + df_main['DATA INICIAL']
    df_main = df_main.sort_values(by='DATA MEDIA', ascending=True)
    df_main.rename(columns = {'DATA MEDIA':'DATA'}, inplace = True)
    df_main.rename(columns = {'PREÇO MÉDIO REVENDA': 'VALOR REVENDA (R$/L)'}, inplace=True)
    df_main["ANO"] = df_main["DATA"].apply(lambda x: str(x.year) if pd.notnull(x) else "")
    df_main = df_main[df_main.PRODUTO == 'GASOLINA COMUM']
    
    # Garantindo que é numérico para não quebrar o gráfico
    df_main['VALOR REVENDA (R$/L)'] = pd.to_numeric(df_main['VALOR REVENDA (R$/L)'], errors='coerce')

# Valores padrão para Dropdowns (evita erro de carregamento)
anos_disp = df_main['ANO'].unique() if not df_main.empty else []
regioes_disp = df_main['REGIÃO'].unique() if not df_main.empty else []
estados_disp = df_main['ESTADO'].unique() if not df_main.empty else []

val_ano = anos_disp[0] if len(anos_disp) > 0 else ""
val_regiao = regioes_disp[0] if len(regioes_disp) > 0 else ""
val_est1 = estados_disp[0] if len(estados_disp) > 0 else ""
val_est2 = estados_disp[1] if len(estados_disp) > 1 else ""
val_multi = [val_est1, val_est2] if val_est1 and val_est2 else []


# =========  Layout (SEM STORE) =========== #
app.layout = dbc.Container(children=[
    # REMOVI O dcc.Store DAQUI. Isso deixa o site muito mais leve.

    # Row 1 - Topo
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        # Mudança de Título para confirmação visual
                        dbc.Col([html.Legend("Gasolina Dashboard (ESTÁTICO)")], sm=8),
                        dbc.Col([html.I(className='fa fa-filter', style={'font-size': '300%'})], sm=4, align="center")
                    ]),
                    dbc.Row([dbc.Col([ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2]), html.Legend("Fábio Santana")])], style={'margin-top': '10px'}),
                    dbc.Row([dbc.Button("Meu Portfólio", href="https://dashboard-fabio-gasolina.onrender.com", target="_blank")], style={'margin-top': '10px'})
                ])
            ], style=tab_card)
        ], sm=12, md=3, lg=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([dbc.Col([html.H3('Máximos e Mínimos'), dcc.Graph(id='static-maxmin', config=config_travada)])])
                ])
            ], style=tab_card)
        ], sm=12, md=3, lg=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([html.H6('Ano de análise:'), dcc.Dropdown(id="select_ano", value=val_ano, clearable=False, options=[{"label": x, "value": x} for x in anos_disp], style={'background-color': 'rgba(0,0,0,0.3'})], sm=6),
                        dbc.Col([html.H6('Região de análise:'), dcc.Dropdown(id="select_regiao", value=val_regiao, clearable=False, options=[{"label": x, "value": x} for x in regioes_disp], style={'background-color': 'rgba(0,0,0,0.3'})], sm=6)
                    ]),
                    dbc.Row([
                        dbc.Col([dcc.Graph(id='regiaobar_graph', config=config_travada)], sm=12, md=6),
                        dbc.Col([dcc.Graph(id='estadobar_graph', config=config_travada)], sm=12, md=6)    
                    ], style={'column-gap': '0px'})
                ])
            ], style=tab_card)
        ], sm=12, md=6, lg=7)
    ], className='main_row g-2 my-auto', style={'margin-top': '7px'}),
    
    # Row 2
    dbc.Row([
        dbc.Col([        
            dbc.Card([
                dbc.CardBody([
                    html.H3('Preço x Estado'), html.H6('Comparação temporal'),
                    dbc.Row([dbc.Col([dcc.Dropdown(id="select_estados0", value=val_multi, clearable=False, multi=True, options=[{"label": x, "value": x} for x in estados_disp], style={'background-color': 'rgba(0,0,0,0.3'})], sm=10)]),
                    dcc.Graph(id='animation_graph', config=config_travada)
                ])
            ], style=tab_card)
        ], sm=12, md=5, lg=5),

        dbc.Col([    
            dbc.Card([
                dbc.CardBody([
                    html.H3('Comparação Direta'), html.H6('Qual preço é menor?'),
                    dbc.Row([
                        dbc.Col([dcc.Dropdown(id="select_estado1", value=val_est1, clearable=False, options=[{"label": x, "value": x} for x in estados_disp], style={'background-color': 'rgba(0,0,0,0.3'})], sm=10, md=5),
                        dbc.Col([dcc.Dropdown(id="select_estado2", value=val_est2, clearable=False, options=[{"label": x, "value": x} for x in estados_disp], style={'background-color': 'rgba(0,0,0,0.3'})], sm=10, md=6),
                    ], style={'margin-top': '20px'}, justify='center'),
                    dcc.Graph(id='direct_comparison_graph', config=config_travada),
                    html.P(id='desc_comparison', style={'color': 'gray', 'font-size': '80%'}),
                ])
            ], style=tab_card)
        ], sm=12, md=4, lg=4),

        dbc.Col([
            dbc.Row([dbc.Col([dbc.Card([dbc.CardBody([dcc.Graph(id='card1_indicators', config=config_travada, style={'margin-top': '30px'})])], style=tab_card)])], justify='center', style={'padding-bottom': '7px', 'height': '50%'}),
            dbc.Row([dbc.Col([dbc.Card([dbc.CardBody([dcc.Graph(id='card2_indicators', config=config_travada, style={'margin-top': '30px'})])], style=tab_card)])], justify='center', style={'height': '50%'})
        ], sm=12, md=3, lg=3, style={'height': '100%'})
    ], justify='center', className='main_row g-2 my-auto'),

    # Row 3 - Slider (Apenas visual, sem funcionalidade de play automática)
    dbc.Row([
        dbc.Col([
            dbc.Card([                
                dbc.Row([
                    dbc.Col([
                        dbc.Button([html.I(className='fa fa-play')], id="play-button", style={'margin-right': '15px'}),  
                        dbc.Button([html.I(className='fa fa-stop')], id="stop-button")
                    ], sm=12, md=1, style={'justify-content': 'center', 'margin-top': '10px'}),
                    dbc.Col([
                        dcc.RangeSlider(id='rangeslider', marks= {int(x): f'{x}' for x in anos_disp} if len(anos_disp)>0 else {}, step=3, min=2004, max=2021, value=[2004,2021], dots=True, pushable=3, tooltip={'always_visible':False, 'placement':'bottom'})
                    ], sm=12, md=10, style={'margin-top': '15px'}),
                ], className='g-1', style={'height': '20%', 'justify-content': 'center'})
            ], style=tab_card)
        ])
    ], className='main_row g-2 my-auto')

], fluid=True, style={'height': '100%'})


# ======== Callbacks ========== #
# Agora usamos df_main direto da memória global (MUITO mais rápido e estável)

@app.callback(
    Output('static-maxmin', 'figure'),
    [Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def func(toggle):
    template = template_theme1 if toggle else template_theme2
    if df_main.empty: return go.Figure()
    
    max_val = df_main.groupby(['ANO'])['VALOR REVENDA (R$/L)'].max()
    min_val = df_main.groupby(['ANO'])['VALOR REVENDA (R$/L)'].min()
    final_df = pd.concat([max_val, min_val], axis=1)
    final_df.columns = ['Máximo', 'Mínimo']
    
    fig = px.line(final_df, x=final_df.index, y=final_df.columns, template=template)
    fig.update_layout(main_config, height=150, xaxis_title=None, yaxis_title=None, transition={'duration': 0})
    return fig

@app.callback(
    [Output('regiaobar_graph', 'figure'), Output('estadobar_graph', 'figure')],
    [Input('select_ano', 'value'), Input('select_regiao', 'value'), Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def graph1(ano, regiao, toggle):
    template = template_theme1 if toggle else template_theme2
    if df_main.empty: return go.Figure(), go.Figure()

    df_filtered = df_main[df_main.ANO.isin([str(ano)])]
    
    dff_regiao = df_filtered.groupby(['ANO', 'REGIÃO'])['VALOR REVENDA (R$/L)'].mean().reset_index()
    dff_estado = df_filtered.groupby(['ANO', 'ESTADO', 'REGIÃO'])['VALOR REVENDA (R$/L)'].mean().reset_index()
    dff_estado = dff_estado[dff_estado.REGIÃO.isin([regiao])]
    
    # Ordenação fixa para evitar pulos
    dff_regiao = dff_regiao.sort_values(by='VALOR REVENDA (R$/L)', ascending=True)
    dff_estado = dff_estado.sort_values(by='VALOR REVENDA (R$/L)', ascending=True)
    
    dff_regiao['VALOR REVENDA (R$/L)'] = dff_regiao['VALOR REVENDA (R$/L)'].round(decimals = 2)
    dff_estado['VALOR REVENDA (R$/L)'] = dff_estado['VALOR REVENDA (R$/L)'].round(decimals = 2)
    
    fig1_text = [f'{x} - R${y}' for x,y in zip(dff_regiao.REGIÃO.unique(), dff_regiao['VALOR REVENDA (R$/L)'].unique())]
    fig2_text = [f'R${y} - {x}' for x,y in zip(dff_estado.ESTADO.unique(), dff_estado['VALOR REVENDA (R$/L)'].unique())]

    fig1 = go.Figure(go.Bar(x=dff_regiao['VALOR REVENDA (R$/L)'], y=dff_regiao['REGIÃO'], orientation='h', text=fig1_text, textposition='auto', insidetextanchor='end', insidetextfont=dict(family='Times', size=12)))
    fig2 = go.Figure(go.Bar(x=dff_estado['VALOR REVENDA (R$/L)'], y=dff_estado['ESTADO'], orientation='h', text=fig2_text, textposition='auto', insidetextanchor='end', insidetextfont=dict(family='Times', size=12)))
    
    # Configuração de trava visual
    fig1.update_layout(main_config, height=140, xaxis_title=None, yaxis_title=None, template=template, transition={'duration': 0})
    fig2.update_layout(main_config, height=140, xaxis_title=None, yaxis_title=None, template=template, transition={'duration': 0})
    
    # Remove eixos para limpar
    fig1.update_xaxes(showticklabels=False)
    fig1.update_yaxes(showticklabels=False)
    fig2.update_xaxes(showticklabels=False)
    fig2.update_yaxes(showticklabels=False)
    return fig1, fig2

@app.callback(
    Output('animation_graph', 'figure'),
    [Input('select_estados0', 'value'), Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def animation_graph(estados, toggle):
    template = template_theme1 if toggle else template_theme2
    if df_main.empty: return go.Figure()
    
    mask = df_main.ESTADO.isin(estados)
    fig = px.line(df_main[mask], x='DATA', y='VALOR REVENDA (R$/L)', color='ESTADO', template=template)
    fig.update_layout(main_config, height=400, xaxis_title=None, transition={'duration': 0})
    return fig

@app.callback(
    [Output('direct_comparison_graph', 'figure'), Output('desc_comparison', 'children')],
    [Input('select_estado1', 'value'), Input('select_estado2', 'value'), Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def direct_comparison(est1, est2, toggle):
    template = template_theme1 if toggle else template_theme2
    if df_main.empty: return go.Figure(), ""
    
    df1 = df_main[df_main.ESTADO == est1]
    df2 = df_main[df_main.ESTADO == est2]
    df_final = pd.concat([df1, df2])
    
    fig = px.line(df_final, x='DATA', y='VALOR REVENDA (R$/L)', color='ESTADO', template=template)
    fig.update_layout(main_config, height=400, xaxis_title=None, transition={'duration': 0})
    
    val1 = df1['VALOR REVENDA (R$/L)'].iloc[-1] if not df1.empty else 0
    val2 = df2['VALOR REVENDA (R$/L)'].iloc[-1] if not df2.empty else 0
    
    desc = f"{est1} é mais barato que {est2} atualmente." if val1 < val2 else f"{est2} é mais barato que {est1} atualmente."
    return fig, desc

@app.callback(
    [Output('card1_indicators', 'figure'), Output('card2_indicators', 'figure')],
    [Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def indicators(toggle):
    template = template_theme1 if toggle else template_theme2
    fig1, fig2 = go.Figure(), go.Figure()
    fig1.update_layout(template=template, title="Indicador 1", transition={'duration': 0})
    fig2.update_layout(template=template, title="Indicador 2", transition={'duration': 0})
    return fig1, fig2

if __name__ == '__main__':
    app.run_server(debug=False)
