import psycopg2
import pandas as pd
import numpy as np
import dash
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go



#conectando e criando o cursor
con = psycopg2.connect(
    dbname='db3k1jiq48kpf7',
    user='gurnumndnupwfw',
    host= 'ec2-34-231-221-151.compute-1.amazonaws.com',
    password='5705908906a69c2531722dc33cb7c4862369ee5cf0ec88cc573eefd6564af01d',
    sslmode='require'
)
cur = con.cursor()



#como o planeta influencia no salário do piloto?
sql_script = '''
SELECT nomeplaneta, funcionario.salario, funcionario.nome FROM viagem 
JOIN funcionario ON codpiloto = funcionario.id
'''
cur.execute(sql_script)
data = cur.fetchall()
data_i = pd.DataFrame(data, columns = ["planeta", "salario", "nome"])



#como a profissão influencia no salário do piloto?
profissoes = ['mecanico', 'pesquisador', 'piloto', 'auxiliarnavegacao']
data = []
for profissao in profissoes:
    sql = f'SELECT codfun, funcionario.salario FROM {profissao} JOIN funcionario ON codfun = funcionario.id'
    cur.execute(sql)
    p = cur.fetchall()
    for pair in p:
        z = list(pair)
        z[0] = profissao
        z[1] = float(z[1])
        data.append(z)
data_ii = pd.DataFrame(data, columns=['profissao', 'salario'])



#qual o salário médio dos pilotos por viagem?
sql = '''
SELECT funcionario.nome,
COUNT(idviagem), funcionario.salario FROM viagem 
JOIN funcionario ON codpiloto = funcionario.id
GROUP BY funcionario.id
'''
cur.execute(sql)
data_iii = cur.fetchall()
data_iii = pd.DataFrame(data_iii, columns = ['nome', 'nviagens', 'salario'])
data_iii['media'] = data_iii['salario'] / data_iii['nviagens']
data_iii = data_iii.sort_values(by='media')



#fechando a conexão
con.close()
cur.close()
pd.DataFrame(data_i.groupby('planeta')['salario'].mean(), columns = ['salario']).reset_index()



#criando gráficos
fig_i = px.bar(data_i, x="planeta", y="salario", barmode="group")
fig_ii = fig_ii = px.bar(pd.DataFrame(data_ii.groupby('profissao')['salario'].mean(), columns = ['salario']).reset_index(), x="profissao", y="salario", color="profissao", barmode="group")
fig_iii = px.bar(data_iii, x="nome", y="media", barmode="group")



#criando aplicativo e layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
opcoes_i = list(data_i['planeta'].unique())
opcoes_i.append("Todos os Planetas")
app.layout = html.Div(children=[
    html.Div(children=[
    html.H1(children='Como o planeta influencia no salário do piloto?'),
    dcc.Dropdown(opcoes_i, 'Todos os Planetas', id='sel_planeta'),
    dcc.Graph(
        id='grafico_planeta_salario',
        figure=fig_i
    )]),
    
    html.Div(children=[
    html.H1(children='Como a profissão influencia no salário do piloto?'),
    dcc.Graph(
        id='grafico_profissao_salario',
        figure=fig_ii
    ),
    
    html.H1(children='Média por Viagem do Salário dos Pilotos'),
    dcc.Graph(
        id='grafico_quantidade_vendas',
        figure=fig_iii
    )]),
    
])



#criando interatividade
@app.callback(
    Output('grafico_planeta_salario', 'figure'),
    Input('sel_planeta', 'value')
)
def update_output(value):
    if value == "Todos os Planetas":
        fig_i = px.bar(pd.DataFrame(data_i.groupby('planeta')['salario'].mean(), columns = ['salario']).reset_index(), x="planeta", y="salario", color="planeta", barmode="group")
    else:
        tabela_filtrada = data_i.loc[data_i['planeta']==value, :]
        fig_i = px.bar(tabela_filtrada.drop_duplicates('nome'), x="nome", y="salario", color="nome", barmode="group")
    return fig_i



#executando servidor
if __name__ == '__main__':
    app.run_server()
