import os
import json
import time
from datetime import datetime, timedelta
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from tqdm import tqdm

# Constantes para URL base e cabeçalhos de requisição
URL_BASE = 'https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao'
CABECALHOS = {'accept': '*/*'}
DIRETORIO_DADOS = 'Dados'
ARQUIVO_LOG_ERROS = 'registro_erros.txt'
NOME_ARQUIVO_EXCEL = 'dados_contratacoes_modalidades.xlsx'
MAX_TENTATIVAS = 5
PAUSA_TENTATIVA = 3
MAX_TRABALHADORES = 5
TAMANHO_PAGINA = 10

def formatar_data(data):
    """Formata a data removendo o 'T' se presente."""
    return data.replace('T', ' ') if 'T' in data else data

def buscar_e_salvar_pagina(pagina, data_inicial, data_final, codigo_modalidade):
    """Busca e salva uma página específica de dados da API."""
    parametros = {
        'dataInicial': data_inicial.strftime('%Y%m%d'),
        'dataFinal': data_final.strftime('%Y%m%d'),
        'codigoModalidadeContratacao': codigo_modalidade,
        'uf': 'RJ',
        'pagina': pagina,
        'tamanhoPagina': TAMANHO_PAGINA
    }
    
    tentativas = 0
    while tentativas < MAX_TENTATIVAS:
        try:
            resposta = requests.get(URL_BASE, headers=CABECALHOS, params=parametros)
            if resposta.status_code == 200:
                dados = resposta.json()
                if 'data' in dados and dados['data']:
                    caminho_arquivo = os.path.join(
                        DIRETORIO_DADOS, 
                        f"{data_inicial.strftime('%Y%m%d')}_a_{data_final.strftime('%Y%m%d')}_modalidade_{codigo_modalidade}_pagina_{pagina}.json"
                    )
                    with open(caminho_arquivo, 'w') as arquivo:
                        json.dump(dados, arquivo, indent=4)
                return
            elif resposta.status_code in [500, 422, 504]:
                tentativas += 1
                print(f"Erro {resposta.status_code} na página {pagina}, tentativa {tentativas} de {MAX_TENTATIVAS}. Aguardando {PAUSA_TENTATIVA} segundos antes de tentar novamente.")
                time.sleep(PAUSA_TENTATIVA)
            else:
                print(f"Erro {resposta.status_code}: {resposta.text}")
                break
        except Exception as e:
            print(f"Exceção ao buscar a página {pagina}: {e}")
            break
    else:
        # Registrar tentativas malsucedidas
        with open(ARQUIVO_LOG_ERROS, 'a') as arquivo_log:
            arquivo_log.write(f"Falha em todas as tentativas para a página {pagina} em {data_inicial.strftime('%Y-%m-%d')} com modalidade {codigo_modalidade}\n")

def buscar_todas_paginas_para_modalidade(codigo_modalidade, data_inicial, data_final):
    """Busca todas as páginas de dados para uma modalidade específica e intervalo de datas."""
    parametros_iniciais = {
        'dataInicial': data_inicial.strftime('%Y%m%d'),
        'dataFinal': data_final.strftime('%Y%m%d'),
        'codigoModalidadeContratacao': codigo_modalidade,
        'uf': 'RJ',
        'pagina': 1,
        'tamanhoPagina': TAMANHO_PAGINA
    }
    
    resposta = requests.get(URL_BASE, headers=CABECALHOS, params=parametros_iniciais)
    if resposta.status_code == 200:
        dados = resposta.json()
        total_paginas = dados.get('totalPaginas', 1)

        with ThreadPoolExecutor(max_workers=MAX_TRABALHADORES) as executor:
            tarefas = [executor.submit(buscar_e_salvar_pagina, pagina, data_inicial, data_final, codigo_modalidade) 
                       for pagina in range(1, total_paginas + 1)]
            
            # Barra de progresso
            for _ in tqdm(as_completed(tarefas), total=total_paginas, desc=f"Modalidade {codigo_modalidade}", unit="página"):
                pass

def main():
    """Função principal para executar o processo de coleta e salvamento de dados."""
    # Verifica se o diretório 'Dados' existe; caso contrário, cria-o
    if not os.path.exists(DIRETORIO_DADOS):
        os.makedirs(DIRETORIO_DADOS)

    # Ajustar as datas de início e fim
    data_inicial = datetime.today() - timedelta(days=1)
    data_final = datetime.today() - timedelta(days=1)

    print(data_inicial)
    print(data_final)

    for codigo_modalidade in range(1, 15):
        buscar_todas_paginas_para_modalidade(codigo_modalidade, data_inicial, data_final)

    # Carregar todos os arquivos JSON e salvar como Excel
    todos_dados = []
    for arquivo_json in os.listdir(DIRETORIO_DADOS):
        caminho_completo = os.path.join(DIRETORIO_DADOS, arquivo_json)
        with open(caminho_completo, 'r') as arquivo:
            dados = json.load(arquivo)
            if 'data' in dados:
                todos_dados.extend(dados['data'])

    if todos_dados:
        # Usar json_normalize para achatar a estrutura JSON
        df = pd.json_normalize(todos_dados)
        
        # Filtrar linhas onde orgaoEntidade.esferaId é 'E' ou 'M' e criar uma cópia
        df_filtrado = df[df['orgaoEntidade.esferaId'].isin(['E', 'M'])].copy()
        
        # Definir as colunas de datas
        colunas_data = [
            'dataInclusao', 
            'dataPublicacaoPncp', 
            'dataAtualizacao', 
            'dataAberturaProposta', 
            'dataEncerramentoProposta'
        ]
        
        # Formatar as colunas de datas
        for coluna in colunas_data:
            if coluna in df_filtrado.columns:
                # Corrigir formato das datas, se necessário
                df_filtrado[coluna] = df_filtrado[coluna].apply(lambda x: formatar_data(x) if pd.notnull(x) else x)
                # Converter para datetime, lidando com valores nulos
                df_filtrado[coluna] = pd.to_datetime(df_filtrado[coluna], format='%Y-%m-%d %H:%M:%S', errors='coerce')

        # Salvar os dados filtrados em um arquivo Excel
        df_filtrado.to_excel(NOME_ARQUIVO_EXCEL, index=False)
        print(f"Dados filtrados e salvos com sucesso em {NOME_ARQUIVO_EXCEL}")
    else:
        print("Nenhum dado encontrado para salvar.")

if __name__ == "__main__":
    main()
