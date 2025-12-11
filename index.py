import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash_bootstrap_templates import ThemeSwitchAIO

# ============ Configurações Iniciais e Temas ============ #
template_theme1 = "minty"
template_theme2 = "slate"
url_theme1 = dbc.themes.MINTY
url_theme2 = dbc.themes.SLATE
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"

app = dash.Dash(__name__, external_stylesheets=[url_theme1, dbc_css])
server = app.server

# ========== Styles ============ #
tab_card = {'height': '100%'}

main_config = {
    "hovermode": "x unified",
    "legend": {"yanchor":"top", 
                "y":0.9, 
                "xanchor":"left",
                "x":0.1,
                "title": {"text": None},
                "font" :{"color":"white"},
                "bgcolor": "rgba(0,0,0,0.5)"},
    "margin": {"l":0, "r":0, "t":10, "b":0}
}

# ===== Reading n cleaning File ====== #
df_main = pd.read_csv("data_gas.csv")

# Tratamento de Dados
df_main.rename(columns={' DATA INICIAL': 'DATA INICIAL'}, inplace=True)
df_main['DATA INICIAL'] = pd.to_datetime(df_main['DATA INICIAL'])
df_main['DATA FINAL'] = pd.to_datetime(df_main['DATA FINAL'])
df_main['DATA MEDIA'] = ((df_main['DATA FINAL'] - df_main['DATA INICIAL'])/2) + df_main['DATA INICIAL']
df_main = df_main.sort_values(by='DATA MEDIA',ascending=True)
df_main.rename(columns = {'DATA MEDIA':'DATA'}, inplace = True)
df_main.rename(columns = {'PREÇO MÉDIO REVENDA': 'VALOR REVENDA (R$/L)'}, inplace=True)
df_main["ANO"] = df_main["DATA"].apply(lambda x: str(x.year))
df_main = df_main.reset_index()
df_main = df_main[df_main.PRODUTO == 'GASOLINA COMUM']
df_main.drop(['UNIDADE DE MEDIDA', 'COEF DE VARIAÇÃO REVENDA', 'COEF DE VARIAÇÃO DISTRIBUIÇÃO', 
    'NÚMERO DE POSTOS PESQUISADOS', 'DATA INICIAL', 'DATA FINAL', 'PREÇO MÁXIMO DISTRIBUIÇÃO', 'PREÇO MÍNIMO DISTRIBUIÇÃO', 
    'DESVIO PADRÃO DISTRIBUIÇÃO', 'MARGEM MÉDIA REVENDA', 'PREÇO MÍNIMO REVENDA', 'PREÇO MÁXIMO REVENDA', 'DESVIO PADRÃO REVENDA', 
    'PRODUTO', 'PREÇO MÉDIO DISTRIBUIÇÃO'], inplace=True, axis=1)

df_store = df_main.to_dict()


# =========  Layout  =========== #
app.layout = dbc.Container(children=[
    # Armazenamento de dataset
    dcc.Store(id='dataset', data=df_store),
    dcc.Store(id='dataset_fixed', data=df_store),
    dcc.Store(id='controller', data={'play': False}),

    # Layout
    # Row 1 - Topo
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([  
                            html.Legend("Dashboard Combustíveis (FINAL)")
                        ], sm=8),
                        dbc.Col([        
                            html.I(className='fa fa-filter', style={'font-size': '300%'})
                        ], sm=4, align="center")
                    ]),
                    dbc.Row([
                        dbc.Col([
                            ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2]),
                            html.Legend("Fábio Santana de Castro")
                        ])
                    ], style={'margin-top': '10px'}),
                    dbc.Row([
                        dbc.Button("Meu Portfólio", href="https://dashboard-fabio-gasolina.onrender.com", target="_blank")
                    ], style={'margin-top': '10px'})
                ])
            ], style=tab_card)
        ], sm=12, md=3, lg=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H3('Máximos e Mínimos'),
                            dcc.Graph(id='static-maxmin', config={"displayModeBar": False, "showTips": False})
                        ])
                    ])
                ])
            ], style=tab_card)
        ], sm=12, md=3, lg=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6('Ano de análise:'),
                            dcc.Dropdown(
                                id="select_ano",
                                value=df_main.at[df_main.index[1],'ANO'],
                                clearable = False,
                                options=[
                                    {"label": x, "value": x} for x in df_main.ANO.unique()
                                ], style={'background-color': 'rgba(0, 0, 0, 0.3'}),
                        ], sm=6),
                        dbc.Col([
                            html.H6('Região de análise:'),
                            dcc.Dropdown(
                                id="select_regiao",
                                value=df_main.at[df_main.index[1],'REGIÃO'],
                                clearable = False,
                                options=[
                                    {"label": x, "value": x} for x in df_main.REGIÃO.unique()
                                ], style={'background-color': 'rgba(0, 0, 0, 0.3'}),
                        ], sm=6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='regiaobar_graph', config={"displayModeBar": False, "showTips": False})
                        ], sm=12, md=6),
                        dbc.Col([
                            dcc.Graph(id='estadobar_graph', config={"displayModeBar": False, "showTips": False})
                        ], sm=12, md=6)    
                    ], style={'column-gap': '0px'})
                ])
            ], style=tab_card)
        ], sm=12, md=6, lg=7)
    ], className='main_row g-2 my-auto', style={'margin-top': '7px'}),
    
    # Row 2 - Gráficos Principais
    dbc.Row([
        dbc.Col([        
            dbc.Card([
                dbc.CardBody([
                    html.H3('Preço x Estado'),
                    html.H6('Comparação temporal entre estados'),
                    dbc.Row([
                        dbc.Col([
                                dcc.Dropdown(
                                id="select_estados0",
                                value=[df_main.at[df_main.index[3],'ESTADO'], df_main.at[df_main.index[13],'ESTADO'], df_main.at[df_main.index[6],'ESTADO']],
                                clearable = False,
                                multi=True,
                                options=[
                                    {"label": x, "value": x} for x in df_main.ESTADO.unique()
                                ], style={'background-color': 'rgba(0, 0, 0, 0.3'}),
                        ], sm=10),
                    ]),
                    dcc.Graph(id='animation_graph', config={"displayModeBar": False, "showTips": False})
                ])
            ], style=tab_card)
        ], sm=12, md=5, lg=5),

        dbc.Col([    
            dbc.Card([
                dbc.CardBody([
                    html.H3('Comparação Direta'),
                    html.H6('Qual preço é menor em um dado período de tempo?'),
                    dbc.Row([
                        dbc.Col([                                    
                            dcc.Dropdown(
                                id="select_estado1",
                                value=df_main.at[df_main.index[3],'ESTADO'],
                                clearable = False,
                                options=[
                                    {"label": x, "value": x} for x in df_main.ESTADO.unique()
                                ], style={'background-color': 'rgba(0, 0, 0, 0.3'}),
                        ], sm=10, md=5),
                        dbc.Col([
                            dcc.Dropdown(
                                id="select_estado2",
                                value=df_main.at[df_main.index[1],'ESTADO'],
                                clearable = False,
                                options=[
                                    {"label": x, "value": x} for x in df_main.ESTADO.unique()
                                ], style={'background-color': 'rgba(0, 0, 0, 0.3'}),
                        ], sm=10, md=6),
                    ], style={'margin-top': '20px'}, justify='center'),
                    dcc.Graph(id='direct_comparison_graph', config={"displayModeBar": False, "showTips": False}),
                    html.P(id='desc_comparison', style={'color': 'gray', 'font-size': '80%'}),
                ])
            ], style=tab_card)
        ], sm=12, md=4, lg=4),

        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='card1_indicators', config={"displayModeBar": False, "showTips": False}, style={'margin-top': '30px'})
                        ])
                    ], style=tab_card)
                ])
            ], justify='center', style={'padding-bottom': '7px', 'height': '50%'}),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='card2_indicators', config={"displayModeBar": False, "showTips": False}, style={'margin-top': '30px'})
                        ])
                    ], style=tab_card)
                ])
            ], justify='center', style={'height': '50%'})
        ], sm=12, md=3, lg=3, style={'height': '100%'})
    ], justify='center', className='main_row g-2 my-auto'),

    # Row 3 - RangeSlider
    dbc.Row([
        dbc.Col([
            dbc.Card([                
                dbc.Row([
                    dbc.Col([
                        dbc.Button([html.I(className='fa fa-play')], id="play-button", style={'margin-right': '15px'}),  
                        dbc.Button([html.I(className='fa fa-stop')], id="stop-button")
                    ], sm=12, md=1, style={'justify-content': 'center', 'margin-top': '10px'}),
                    dbc.Col([
                        dcc.RangeSlider(
                            id='rangeslider',
                            marks= {int(x): f'{x}' for x in df_main['ANO'].unique()},
                            step=3,                
                            min=2004,
                            max=2021,
                            value=[2004,2021],   
                            dots=True,             
                            pushable=3,
                            tooltip={'always_visible':False, 'placement':'bottom'},
                        )
                    ], sm=12, md=10, style={'margin-top': '15px'}),
                ], className='g-1', style={'height': '20%', 'justify-content': 'center'})
                
            ], style=tab_card)
        ])
    ], className='main_row g-2 my-auto')

], fluid=True, style={'height': '100%'})


# ======== Callbacks ========== #
@app.callback(
    Output('static-maxmin', 'figure'),
    [Input('dataset', 'data'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def func(data, toggle):
    template = template_theme1 if toggle else template_theme2
    dff = pd.DataFrame(data)
    max = dff.groupby(['ANO'])['VALOR REVENDA (R$/L)'].max()
    min = dff.groupby(['ANO'])['VALOR REVENDA (R$/L)'].min()
    final_df = pd.concat([max, min], axis=1)
    final_df.columns = ['Máximo', 'Mínimo']
    fig = px.line(final_df, x=final_df.index, y=final_df.columns, template=template)
    fig.update_layout(main_config, height=150, xaxis_title=None, yaxis_title=None)
    return fig

@app.callback(
    [Output('regiaobar_graph', 'figure'),
    Output('estadobar_graph', 'figure')],
    [Input('dataset_fixed', 'data'),
    Input('select_ano', 'value'),
    Input('select_regiao', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def graph1(data, ano, regiao, toggle):
    template = template_theme1 if toggle else template_theme2
    df = pd.DataFrame(data)
    df_filtered = df[df.ANO.isin([ano])]
    dff_regiao = df_filtered.groupby(['ANO', 'REGIÃO'])['VALOR REVENDA (R$/L)'].mean().reset_index()
    dff_estado = df_filtered.groupby(['ANO', 'ESTADO', 'REGIÃO'])['VALOR REVENDA (R$/L)'].mean().reset_index()
    dff_estado = dff_estado[dff_estado.REGIÃO.isin([regiao])]
    dff_regiao = dff_regiao.sort_values(by='VALOR REVENDA (R$/L)',ascending=True)
    dff_estado = dff_estado.sort_values(by='VALOR REVENDA (R$/L)',ascending=True)
    dff_regiao['VALOR REVENDA (R$/L)'] = dff_regiao['VALOR REVENDA (R$/L)'].round(decimals = 2)
    dff_estado['VALOR REVENDA (R$/L)'] = dff_estado['VALOR REVENDA (R$/L)'].round(decimals = 2)
    
    fig1_text = [f'{x} - R${y}' for x,y in zip(dff_regiao.REGIÃO.unique(), dff_regiao['VALOR REVENDA (R$/L)'].unique())]
    fig2_text = [f'R${y} - {x}' for x,y in zip(dff_estado.ESTADO.unique(), dff_estado['VALOR REVENDA (R$/L)'].unique())]

    fig1 = go.Figure(go.Bar(
        x=dff_regiao['VALOR REVENDA (R$/L)'],
        y=dff_regiao['REGIÃO'],
        orientation='h',
        text=fig1_text,
        textposition='auto',
        insidetextanchor='end',
        insidetextfont=dict(family='Times', size=12)
    ))
    fig2 = go.Figure(go.Bar(
        x=dff_estado['VALOR REVENDA (R$/L)'],
        y=dff_estado['ESTADO'], 
        orientation='h',
        text=fig2_text,
        textposition='auto',
        insidetextanchor='end',
        insidetextfont=dict(family='Times', size=12)
    ))
    
    # === TRAVA DE ANIMAÇÃO ===
    # O transition={'duration': 0} remove qualquer efeito de "deslizar"
    fig1.update_layout(main_config, height=140, xaxis_title=None, yaxis_title=None, template=template, transition={'duration': 0})
    fig2.update_layout(main_config, height=140, xaxis_title=None, yaxis_title=None, template=template, transition={'duration': 0})
    
    fig1.update_xaxes(showticklabels=False)
    fig1.update_yaxes(showticklabels=False)
    fig2.update_xaxes(showticklabels=False)
    fig2.update_yaxes(showticklabels=False)
    return fig1, fig2

@app.callback(
    Output('animation_graph', 'figure'),
    [Input('dataset', 'data'),
    Input('select_estados0', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def animation_graph(data, estados, toggle):
    template = template_theme1 if toggle else template_theme2
    df = pd.DataFrame(data)
    mask = df.ESTADO.isin(estados)
    # Adicionei transition 0 aqui também para garantir
    fig = px.line(df[mask], x='DATA', y='VALOR REVENDA (R$/L)', color='ESTADO', template=template)
    fig.update_layout(main_config, height=400, xaxis_title=None, transition={'duration': 0})
    return fig

@app.callback(
    [Output('direct_comparison_graph', 'figure'),
     Output('desc_comparison', 'children')],
    [Input('dataset', 'data'),
    Input('select_estado1', 'value'),
    Input('select_estado2', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def direct_comparison(data, est1, est2, toggle):
    template = template_theme1 if toggle else template_theme2
    df = pd.DataFrame(data)
    df1 = df[df.ESTADO == est1]
    df2 = df[df.ESTADO == est2]
    df_final = pd.concat([df1, df2])
    # Adicionei transition 0 aqui também
    fig = px.line(df_final, x='DATA', y='VALOR REVENDA (R$/L)', color='ESTADO', template=template)
    fig.update_layout(main_config, height=400, xaxis_title=None, transition={'duration': 0})
    val1 = df1['VALOR REVENDA (R$/L)'].iloc[-1]
    val2 = df2['VALOR REVENDA (R$/L)'].iloc[-1]
    if val1 < val2:
        desc = f"{est1} é mais barato que {est2} atualmente."
    else:
        desc = f"{est2} é mais barato que {est1} atualmente."
    return fig, desc

@app.callback(
    [Output('card1_indicators', 'figure'),
     Output('card2_indicators', 'figure')],
    [Input('dataset', 'data'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def indicators(data, toggle):
    template = template_theme1 if toggle else template_theme2
    fig1 = go.Figure()
    fig1.update_layout(template=template, title="Indicador 1")
    fig2 = go.Figure()
    fig2.update_layout(template=template, title="Indicador 2")
    return fig1, fig2

if __name__ == '__main__':
    app.run_server(debug=True)
