import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import os
import json
import requests

def main():
    def pncp():
        #esfera = esfera_combobox.get()
        #uf_sigla = uf_combobox.get()
        data_final = data_final_entry.get()
        cod_modalidade = cod_modalidade_contra_combobox.get()
        cod_municipio_ibge = cod_municipio.get()

        # Verifica se os campos foram preenchidos
        if not data_final or not cod_municipio_ibge or not cod_modalidade:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return

        # Verifica se as datas estão no formato correto
        if not validar_data(data_final):
            messagebox.showerror("Erro", "Por favor, insira datas válidas no formato AAAAMMDD.")
            return

        if not datetime.strptime(data_final, "%Y%m%d") > datetime.now():
            messagebox.showerror("Erro", f'Por favor, a data precisa ser superior a data atual {datetime.now()}')
            return
        
        url = 'https://pncp.gov.br/api/consulta/v1/contratacoes/proposta'
        headers = {'accept': '*/*'}
        todos_os_registros = []

        params = {
            'dataFinal': data_final,
            'codigoModalidadeContratacao': cod_modalidade,
            'pagina': '1',
            'tamanhoPagina': '25',
            'codigoMunicipioIbge': cod_municipio_ibge
        }

        #if uf_sigla:
        #    params['uf'] = uf_sigla

        # Primeira requisição para obter o total de páginas
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            dados = response.json()
            total_paginas = dados['totalPaginas']
            todos_os_registros.extend(dados['data'])
        else:
            messagebox.showerror("Erro", f"Erro ao consultar a API: {response.status_code}")
            return

        # Loop para percorrer todas as páginas
        for pagina in range(2, total_paginas + 1):
            params['pagina'] = str(pagina)
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                dados = response.json()
                todos_os_registros.extend(dados['data'])
            else:
                messagebox.showerror("Erro", f"Erro ao consultar a API na página {pagina}: {response.status_code}")
                return

        # Filtra os registros conforme especificado
        registros_filtrados = [item for item in todos_os_registros if item['orgaoEntidade']['esferaId'] == "E" or item['orgaoEntidade']['esferaId'] == "M"]

        # Criar a pasta 'pncp_dados' se não existir
        pasta = 'pncp_dados'
        if not os.path.exists(pasta):
            os.makedirs(pasta)

        # Nome do arquivo com o formato padrão
        nome_arquivo = f"contratacoes_proposta{data_final}.json"
        file_path = os.path.join(pasta, nome_arquivo)

        # Dados a serem salvos no arquivo JSON
        dados_para_salvar = {
            'totalPaginas': total_paginas,
            'totalRegistrosFiltrados': len(registros_filtrados),
            'registros': registros_filtrados
        }

        with open(file_path, "w") as file:
            json.dump(dados_para_salvar, file, indent=4)

        messagebox.showinfo("Sucesso", f"Total de registros para o Munícipio '{cod_municipio_ibge}': {len(registros_filtrados)} \nTotal de páginas: {total_paginas} \nDados filtrados salvos em: {file_path}")

    def validar_data(data):
        try:
            datetime.strptime(data, "%Y%m%d")
            return True
        except ValueError:
            return False

    def carregar_municipios():
        with open("municipios.json", "r", encoding="utf-8") as arquivo:
            municipios = json.load(arquivo)
        return [f"{municipio['Codigo']}" for municipio in municipios]
    
    # Criando a janela principal
    root = tk.Tk()
    root.title("PNCP")
    root.configure(bg="#0D2649")  # Cor de fundo azul marinho

    # Configuração da interface
    config = {
        'font': ("Arial", 12),
        'bg': "#0D2649",
        'fg': "white"
    }
    root.iconbitmap("icon.ico")

    # Widgets da interface
    data_final_label = tk.Label(root, text="Data Final (AAAAMMDD):", **config)
    data_final_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    data_final_entry = tk.Entry(root, font=("Verdana", 12))
    data_final_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    cod_modalidade_contra_label = tk.Label(root, text="Código Modalidade Contratação:", **config)
    cod_modalidade_contra_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")

    # Lista de Modalidades de Contratação
    modalidades = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]
    cod_modalidade_contra_combobox = ttk.Combobox(root, values=modalidades, font=("Verdana", 12), state="readonly")
    cod_modalidade_contra_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    cod_municipio_label = tk.Label(root, text="Código Munícipio IBGE:", **config)
    cod_municipio_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")

    municipios = carregar_municipios()
    cod_municipio = ttk.Combobox(root, values=municipios, font=("Verdana", 12), state="readonly")
    cod_municipio.grid(row=4, column=1, padx=5, pady=5)

    """
    esfera_label = tk.Label(root, text="Esfera:", **config)
    esfera_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")

    esferas = ["E", "M"]
    esfera_combobox = ttk.Combobox(root, values=esferas, font=("Verdana", 12), state="readonly")
    esfera_combobox.grid(row=4, column=1, padx=5, pady=5, sticky="w")
    

    uf_label = tk.Label(root, text="UF Sigla:", **config)
    uf_label.grid(row=5, column=0, padx=5, pady=5, sticky="e")

    # Lista de estados do Brasil
    estados_brasil = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
        "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    ]
    uf_combobox = ttk.Combobox(root, values=estados_brasil, font=("Verdana", 12), state="readonly")
    uf_combobox.grid(row=5, column=1, padx=5, pady=5, sticky="w")
    """
    filtrar_button = tk.Button(root, text="Filtrar e Salvar", font=("Arial", 14, "bold"), bg="#28a745", fg="white", command=pncp, bd=0, relief=tk.RAISED)
    filtrar_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="we")

    # Iniciando o loop principal da interface
    root.mainloop()

