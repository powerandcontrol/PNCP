import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
import json
import requests
from datetime import datetime
import os
import time

def main():
    def pncp():
        data_inicial = data_inicial_entry.get()
        data_final = data_final_entry.get()
        uf_sigla = uf_combobox.get()

        if not data_inicial or not data_final:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return

        if not validar_data(data_inicial) or not validar_data(data_final):
            messagebox.showerror("Erro", "Por favor, insira datas válidas no formato AAAAMMDD.")
            return

        if not verificar_intervalo_de_datas(data_inicial, data_final):
            messagebox.showerror("Erro", "Por favor, insira datas dentro do intervalo permitido.")
            return

        url = 'https://pncp.gov.br/api/consulta/v1/contratos'
        headers = {'accept': '*/*'}
        todos_os_registros = []

        params = {
            'dataInicial': '20240522',
            'dataFinal': '20240523',
            'pagina': '1',
            'tamanhoPagina': '300'
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            dados = response.json()
            total_paginas = dados['totalPaginas']
            todos_os_registros.extend(dados['data'])
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro", f"Erro ao consultar a API: {e}")
            return
        
        for pagina in range(2, 10):
            params['pagina'] = str(pagina)
            try:
                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()
                dados = response.json()
                todos_os_registros.extend(dados['data'])
                # Adiciona um atraso para evitar ultrapassar o limite de requisições
                time.sleep(5)
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Erro", f"Erro ao consultar a API na página {pagina}: {e}")
                return

        registros_filtrados = [
        item for item in todos_os_registros
        if (item['orgaoEntidade']['esferaId'] == "E" or item['orgaoEntidade']['esferaId'] == "M") 
        and item['unidadeOrgao']['ufSigla'] == uf_sigla
        ]

        pasta = 'pncp_dados'
        if not os.path.exists(pasta):
            os.makedirs(pasta)

        nome_arquivo = f"contratos{data_inicial}_{data_final}.json"
        file_path = os.path.join(pasta, nome_arquivo)

        dados_para_salvar = {
            'totalPaginas': total_paginas,
            'totalRegistrosFiltrados': len(registros_filtrados),
            'registros': registros_filtrados
        }

        with open(file_path, "w") as file:
            json.dump(dados_para_salvar, file, indent=4)

        messagebox.showinfo("Sucesso", f"Total de registros para UF '{uf_sigla}': {len(registros_filtrados)} \n Total de páginas: {total_paginas} \nDados filtrados salvos em: {file_path}")

    def validar_data(data):
        try:
            datetime.strptime(data, "%Y%m%d")
            return True
        except ValueError:
            return False
 
    def verificar_intervalo_de_datas(data_inicial, data_final):
        data_atual = datetime.now()
        ano_atual = data_atual.year
        mes_atual = data_atual.month
 
        data_inicial_dt = datetime.strptime(data_inicial, "%Y%m%d")
        data_final_dt = datetime.strptime(data_final, "%Y%m%d")
 
        if not 2000 <= data_inicial_dt.year <= ano_atual or not 2000 <= data_final_dt.year <= ano_atual:
            return False
 
        if data_inicial_dt.year == ano_atual and data_inicial_dt.month > mes_atual:
            return False
 
        return True
 
    root = tk.Tk()
    root.title("PNCP")
    root.configure(bg="#0D2649")
    
    data_inicial_label = tk.Label(root, text="Data Inicial (AAAAMMDD):", font=("Arial", 12), bg="#0D2649", fg="white")
    data_inicial_label.grid(row=1, column=0, padx=10, pady=(20, 5), sticky="e")
    data_inicial_entry = tk.Entry(root, font=("Arial", 12))
    data_inicial_entry.grid(row=1, column=1, padx=10, pady=(20, 5))
    
    data_final_label = tk.Label(root, text="Data Final (AAAAMMDD):", font=("Arial", 12), bg="#0D2649", fg="white")
    data_final_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
    data_final_entry = tk.Entry(root, font=("Arial", 12))
    data_final_entry.grid(row=2, column=1, padx=10, pady=5)

    uf_label = tk.Label(root, text="UF Sigla:", font=("Arial", 12), bg="#0D2649", fg="white")
    uf_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
    
    estados_brasil = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
        "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    ]
    uf_combobox = ttk.Combobox(root, values=estados_brasil, font=("Arial", 12), state="readonly")
    uf_combobox.grid(row=4, column=1, padx=10, pady=5)
 
    filtrar_button = tk.Button(root, text="Filtrar e Salvar", font=("Arial", 14, "bold"), bg="#28a745", fg="white", command=pncp, bd=0, relief=tk.RAISED)
    filtrar_button.grid(row=5, column=0, columnspan=2, padx=10, pady=20, sticky="we")
 
    root.mainloop()

if __name__ == "__main__":
    main()
