import requests
import json
import pandas as pd
from tqdm import tqdm
import os
from colorama import Fore, Back, Style, init

# Inicializa a biblioteca colorama
init(autoreset=True)

def consultar_api(url):
    try:
        resposta = requests.get(url)
        resposta.raise_for_status()  # Verifica se a requisição foi bem-sucedida
        dados = resposta.json()  # Converte a resposta para JSON
        return dados
    except requests.RequestException as e:
        print(f"{Fore.RED}{Back.WHITE}Erro na requisição: {e}{Style.RESET_ALL}")
        return None

def salvar_em_xlsx(dados, nome_arquivo):
    if dados is None:
        print(f"{Fore.RED}{Back.WHITE}Nenhum dado para salvar.{Style.RESET_ALL}")
        return

    # Cria um DataFrame do pandas a partir dos dados
    df = pd.json_normalize(dados)
    
    # Salva o DataFrame em um arquivo Excel
    df.to_excel(nome_arquivo, index=False)
    print(f"{Fore.GREEN}{Back.WHITE}Dados salvos em {nome_arquivo}{Style.RESET_ALL}")

def exibir_menu():
    print("Menu de Consulta API PNCP")
    print("1. Amparos Legais")
    print("2. Modalidades")
    print("3. Modos de Disputa")
    print("4. Tipos de Instrumentos Convocatórios")
    print("5. Sair")

def main():
    while True:
        exibir_menu()
        escolha = input("Escolha uma opção (1-5): ")

        if escolha == "5":
            print(f"{Fore.GREEN}{Back.WHITE}Saindo...{Style.RESET_ALL}")
            break

        status_ativo = input("Digite o status ativo (True ou False): ").strip().capitalize()
        if status_ativo not in ["True", "False"]:
            print(f"{Fore.RED}{Back.WHITE}Status inválido. Digite 'True' ou 'False'.{Style.RESET_ALL}")
            continue

        status_ativo = status_ativo == "True"
        url = None
        nome_arquivo = None

        if escolha == "1":
            url = f"https://pncp.gov.br/api/pncp/v1/amparos-legais?statusAtivo={status_ativo}"
            nome_arquivo = "amparos_legais.xlsx"
        elif escolha == "2":
            url = f"https://pncp.gov.br/api/pncp/v1/modalidades?statusAtivo={status_ativo}"
            nome_arquivo = "modalidades.xlsx"
        elif escolha == "3":
            url = f"https://pncp.gov.br/api/pncp/v1/modos-disputas?statusAtivo={status_ativo}"
            nome_arquivo = "modos_disputas.xlsx"
        elif escolha == "4":
            url = f"https://pncp.gov.br/api/pncp/v1/tipos-instrumentos-convocatorios?statusAtivo={status_ativo}"
            nome_arquivo = "tipos_instrumentos.xlsx"
        else:
            print(f"{Fore.RED}{Back.WHITE}Opção inválida. Tente novamente.{Style.RESET_ALL}")
            continue

        print(f"{Fore.YELLOW}{Back.BLACK}Consultando a API, por favor aguarde...{Style.RESET_ALL}")
        with tqdm(total=1, desc="Carregando", bar_format="{l_bar}{bar} [{elapsed}]") as barra:
            dados = consultar_api(url)
            barra.update(1)  # Atualiza a barra de carregamento

        if dados is not None:
            salvar_em_xlsx(dados, nome_arquivo)

if __name__ == "__main__":
    main()
