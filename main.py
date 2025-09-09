# %%
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

# %% [markdown]
# ### PARTE 1: CARREGAMENTO DOS DADOS, LIMPEZA E ANÁLISE EXPLORATÓRIA

# %%
df_diesel = pd.read_excel('data/vendas_distribuidoras_anp 1 (3).xlsx', sheet_name='diesel')
df_gasolina = pd.read_excel('data/vendas_distribuidoras_anp 1 (3).xlsx', sheet_name='gasolina')
df_etanol = pd.read_excel('data/vendas_distribuidoras_anp 1 (3).xlsx', sheet_name='etanol')

# %%
print("\nEtanol:")
print(df_etanol.head())
print("\nDiesel:")
print(df_diesel.head())
print("\nGasolina:")
print(df_gasolina.head())

# %% [markdown]
# Os dataframes estão no formato 'wide' e serão convertidos para 'long format' para a análise.
# 
# Verificando a estrutura: nas 3 planilhas a coluna 2021 possui valores ausentes.
# Os anos restantes apresentam 108 observações cada. Dados de volume em metros cúbicos, não há necessidade de conversão de tipo.

# %%
print("\nDiesel:")
print(df_diesel.info())
print("\nEtanol:")
print(df_etanol.info())
print("\nGasolina:")
print(df_gasolina.info())

# %%
dataframes_dict = {'diesel': df_diesel, 'etanol': df_etanol, 'gasolina': df_gasolina}

def transformar_juntar(dataframes_dict):
    """Transforma dataframes de wide para long format e consolida em um único dataset"""
    dfs_long = []
    
    for nome, df in dataframes_dict.items():
        df_long = df.melt(
            id_vars=["regiao", "meses"],
            var_name="ano",
            value_name="valor"
        )
        df_long['tipo'] = nome
        dfs_long.append(df_long)
    
    df_final = pd.concat(dfs_long, ignore_index=True)
    return df_final

df_consolidado = transformar_juntar(dataframes_dict)

# %%
print("\nPrimeiras linhas:")
print(df_consolidado.head())
print("\nInformações gerais:")
print(df_consolidado.info())
print("\nMeses únicos:", df_consolidado['meses'].unique())
print("\nRegiões únicas:", df_consolidado['regiao'].unique())

# %%
df_consolidado['data'] = pd.to_datetime(
    df_consolidado["ano"].astype(str) + "-" + 
    df_consolidado["meses"].astype(str) + "-01"
)
df_consolidado = df_consolidado.drop(columns=['meses', 'ano'])

print(df_consolidado.info())

# %% [markdown]
# ### PARTE 2: ANÁLISE DE SAZONALIDADE

# %%
df_br = df_consolidado[df_consolidado['regiao'] == 'br']
df_estados = df_consolidado[df_consolidado['regiao'] != 'br']

# %%
df_sazonalidade = df_br.groupby(df_br['data'].dt.month)['valor'].sum()

plt.figure(figsize=(10, 6))
plt.plot(df_sazonalidade.index, df_sazonalidade.values, marker='o')
plt.title('Sazonalidade Geral da Demanda de Combustíveis')
plt.xlabel('Mês')
plt.ylabel('Volume Total (metros cúbicos)')
plt.xticks(range(1, 13))
plt.grid(True, alpha=0.3)
plt.show()

# %% [markdown]
# A sazonalidade de demanda demonstra que a empresa precisa de planejamento para lidar com 
# as variações ao longo do ano. Variação significativa entre fevereiro e março, com outro 
# pico em outubro. Os picos/vales podem estar associados ao escoamento de commodities agrícolas.

# %%
df_mensal = df_br.groupby('data')['valor'].sum().sort_index()
df_mensal = df_mensal[df_mensal.index.year != 2021]

decomp = seasonal_decompose(df_mensal, model='multiplicative', period=12)

plt.figure(figsize=(12, 10))
decomp.plot()
plt.tight_layout()
plt.show()

# %% [markdown]
# **Análise da decomposição:**
# - **Observed**: Evolução total do consumo nacional
# - **Trend**: Crescimento geral até 2014, depois estabilização
# - **Seasonal**: Sazonalidade anual regular
# - **Resid**: Resíduos próximos de 1, confirmando adequação do modelo multiplicativo

# %%
sazonalidade_estados = {}

for estado in df_estados['regiao'].unique():
    df_estado = df_estados[df_estados['regiao'] == estado]
    serie_mensal = df_estado.groupby('data')['valor'].sum().sort_index()
    serie_mensal = serie_mensal[serie_mensal.index.year != 2021]
    
    decomp_estado = seasonal_decompose(serie_mensal, model='multiplicative', period=12)
    sazonalidade_estados[estado] = decomp_estado.seasonal.groupby(decomp_estado.seasonal.index.month).mean()

df_sazon = pd.DataFrame(sazonalidade_estados)

plt.figure(figsize=(12, 6))
for estado in df_sazon.columns:
    plt.plot(df_sazon.index, df_sazon[estado], marker='o', alpha=0.7, label=estado)

plt.title('Padrão Sazonal por Estado')
plt.xlabel('Mês')
plt.ylabel('Fator Sazonal')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# %% [markdown]
# **Destaque para Mato Grosso**: Pico em março muito superior aos outros estados, 
# correlacionado com a produção agrícola (soja, milho, algodão) e distância dos portos. 
# MT também consome menos etanol relativamente, devido ao uso intensivo de máquinas agrícolas.

# %% [markdown]
# ### PARTE 3: ANÁLISE ESTADUAL

# %%
df_evolucao_estados = df_estados[df_estados['data'].dt.year != 2021].groupby([df_estados['data'].dt.year, 'regiao'])['valor'].sum().reset_index()
df_pivot_evolucao = df_evolucao_estados.pivot(index='data', columns='regiao', values='valor')

plt.figure(figsize=(14, 8))
for estado in df_pivot_evolucao.columns:
    plt.plot(df_pivot_evolucao.index, df_pivot_evolucao[estado], marker='o', alpha=0.7, label=estado)

plt.title('Evolução do Consumo por Estado')
plt.xlabel('Ano')
plt.ylabel('Volume Total (m³)')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# %%
df_por_tipo_estado = df_estados.groupby(['regiao', 'tipo'])['valor'].sum().reset_index()
df_pivot_tipo = df_por_tipo_estado.pivot(index='regiao', columns='tipo', values='valor')
df_percent = df_pivot_tipo.div(df_pivot_tipo.sum(axis=1), axis=0) * 100

df_percent.plot(kind='bar', stacked=True, figsize=(12, 6))
plt.title('Distribuição Percentual por Tipo de Combustível por Estado')
plt.ylabel('Percentual (%)')
plt.xlabel('Estado')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %% [markdown]
# **SP apresenta distribuição mais equilibrada** entre combustíveis, refletindo maior diversidade 
# tecnológica. Estados como PA, MA, DF, TO mostram preferência por diesel/gasolina vs etanol, 
# possivelmente relacionado ao desenvolvimento tecnológico.

# %% [markdown]
# ### PARTE 4: ANÁLISE DOS ÚLTIMOS 5 ANOS

# %%
df_evolucao = df_br[df_br['data'].dt.year != 2021].groupby(df_br['data'].dt.year)['valor'].sum()
df_evolucao_5_anos = df_evolucao[(df_evolucao.index >= 2016) & (df_evolucao.index <= 2020)]

def plotar_evolucao(dataframe, titulo):
    """Função para plotar evolução temporal"""
    plt.figure(figsize=(10, 5))
    plt.plot(dataframe.index, dataframe.values, marker='o')
    plt.title(titulo)
    plt.xlabel('Ano')
    plt.ylabel('Volume Total (metros cúbicos)')
    plt.grid(True, alpha=0.4)
    plt.show()

plotar_evolucao(df_evolucao_5_anos, 'Evolução do Mercado Total de Combustíveis (Últimos 5 Anos)')
plotar_evolucao(df_evolucao, 'Evolução do Mercado Total de Combustíveis (Série Completa)')

# %% [markdown]
# Tendência geral de crescimento nos últimos 20 anos, com queda em 2020 
# possivelmente correlacionada com a pandemia do coronavírus. (https://www.gov.br/anp/pt-br/canais_atendimento/imprensa/noticias-comunicados/comercializacao-de-combustiveis-em-2020-teve-queda-de-5-97-na-comparacao-com-2019-devido-a-pandemia)

# %%
df_evolucao_tipos = df_br[df_br['data'].dt.year != 2021].groupby([df_br['data'].dt.year, 'tipo'])['valor'].sum().reset_index()
df_pivot_tipos = df_evolucao_tipos.pivot(index='data', columns='tipo', values='valor')

plt.figure(figsize=(10, 6))
for tipo in df_pivot_tipos.columns:
    plt.plot(df_pivot_tipos.index, df_pivot_tipos[tipo], marker='o', label=tipo.capitalize())

plt.title('Evolução do Consumo por Tipo de Combustível')
plt.xlabel('Ano')
plt.ylabel('Volume Total (m³)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# %% [markdown]
# **Hierarquia de consumo**: Diesel > Gasolina > Etanol
# 
# **Diesel**: Uso intensivo em logística (caminhões, trens, transporte pesado)
# **Etanol/Gasolina**: Veículos leves, diferentes públicos e estratégias de negócio.

# %% [markdown]
# ### CONCLUSÕES

# %% [markdown]

# De forma geral, a distribuidora de combustíveis Aliança S.A precisa ter cautela no momento atual (considerando 2021), já que o cenário mostra incerteza e queda no consumo, puxada principalmente pelo etanol e gasolina.

# Alguns pontos importantes:

# - No horizonte analisado, a tendência geral é de crescimento.
#

# - Etanol e gasolina caíram de 2019 para 2020, enquanto o diesel apresentou leve alta.
#

# O transporte de cargas no Brasil depende fortemente de caminhões, por causa da grande produção de commodities e da malha ferroviária pouco desenvolvida. Isso faz com que o diesel seja essencial para a economia. O mercado de diesel pode ser atrativo, mas a entrada pode exigir custos mais altos. Existe ainda um nicho interessante em Mato Grosso, já que sua sazonalidade se diferencia dos outros estados, uma possível explicação para isso pode ser a grande necessidade de transporte para escoar o produto do agronegócio, e também a distância do estado em relação aos portos. Esses fatos podem ser determinantes e exigem mais investigação para se determinar algum tipo de correlação. 
#
# Também é recomendável, no caso de atuar com um combustível específico, buscar estados em que esse tipo tenha maior demanda, conforme o gráfico de distribuição percentual mostra.

# No geral, o mercado de combustíveis analisado tem volatilidade própria, que deve ser levada em conta na estratégia da empresa.
#
# (Tive a ideia de fazer o gráfico de análise da sazonalidade por tipo de combustível, mas envolveria normalizar os dados, conceito que não domino com clareza ainda, então decidi não arriscar.
#
# Caso a empresa apresente interesse em se integrar e explorar o nicho de fornecimento de combustível para o agronegócio, recomenda-se acompanhar assiduamente as safras das commodities agrícolas de importância nas regiões de fornecimento.
# %%