import numpy as np
from src.utils.graph_plotly import plot_bar


#ARQUIVO: generalDroneData

def _calculate_interval(series):
    mean = series.mean()
    std = series.std()
    n = series.count()
    interval = 1.96 * (std / np.sqrt(n))
    return interval


def calculate_duration_successful_trips_per_execution(df):
    """
    Calcula a duraçao media das viagens com sucesso por execuçao.

    Args:
        df (DataFrame): DataFrame contendo os dados de drones.

    Returns:
        dict: Dicionario contendo 'execucoes', 'media', 'desvio_padrao' e 'intervalo'.
    """
    df.columns = df.columns.str.strip()
    # Remove linhas sem "drone ID"
    df = df.dropna(subset=["drone ID"])

    # Agrupa por "Numero da execucao" e calcula as estatisticas
    df_grouped = (
        df.groupby("Numero da execucao")
        .agg(
            {
                "tempo de viagem total dos drones no tempo estavel": ["mean", "std", _calculate_interval],
            }
        )
        .dropna()
        .reset_index()
    )

    # Extrai as estatisticas
    media = df_grouped[("tempo de viagem total dos drones no tempo estavel", "mean")].values
    desvio_padrao = df_grouped[("tempo de viagem total dos drones no tempo estavel", "std")].values
    intervalo = df_grouped[("tempo de viagem total dos drones no tempo estavel", "_calculate_interval")].values
    execucoes = df_grouped["Numero da execucao"].values.astype(int)

    return {
        "execucoes": execucoes,
        "media": media,
        "desvio_padrao": desvio_padrao,
        "intervalo": intervalo
    }


def plot_duration_successful_trips_per_execution(data_list, labels=None):
    """
    Gera o grafico da duraçao media das viagens com sucesso por execuçao.

    Args:
        data_list (list or dict): Dados calculados pela funçao calculate_duration_successful_trips.
        labels (list, optional): Lista de nomes das simulaçoes.

    Returns:
        Figure: Objeto de figura Plotly.
    """
    if not isinstance(data_list, list):
        data_list = [data_list]

    
    if labels is None:
        labels = [f"Simulaçao {i+1}" for i in range(len(data_list))]

    # Obter todas as execuçoes unicas
    all_execucoes = sorted(set(exec_num for data in data_list for exec_num in data['execucoes']))
    list_exec = [str(exec_num) for exec_num in all_execucoes]

    # Preparar os valores para cada simulaçao
    values_list = []
    intervalos_list = []
    
    for data in data_list:
        
        # Mapear execuçoes para medias e intervalos
        exec_media_dict = dict(zip(data['execucoes'], data['media']))
        # Obter os valores na ordem de all_execucoes
        series_values = [exec_media_dict.get(exec_num, 0) for exec_num in all_execucoes]
        values_list.append(series_values)
        
        # Intervalos sao zeros
        series_intervalos = [0] * len(all_execucoes)
        intervalos_list.append(series_intervalos)

    # Chama a funçao plot_bar
    fig = plot_bar(
        values=values_list,
        intervalos=intervalos_list,
        labels=list_exec,
        x_label='Execuçao',
        y_label='Tempo (s)',
        title='Duraçao das Viagens com Sucesso por Execuçao',
        show_interval=False
    )
    
    # Atualizar os nomes das series
    for i, sim_name in enumerate(labels):
        fig.data[i].name = sim_name

    return fig