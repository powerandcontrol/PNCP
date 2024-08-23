# PNCP
Este projeto é uma solução para coletar e processar dados de contratações públicas utilizando a API do Portal Nacional de Contratações Públicas (PNCP). O objetivo principal é automatizar a coleta de dados sobre contratações públicas em um intervalo de datas específico e para modalidades de contratação distintas. 

# Coleta e Processamento de Dados da API PNCP

Este projeto coleta e processa dados de contratações públicas através da API do Portal Nacional de Contratações Públicas (PNCP). O script coleta dados paginados e salva em arquivos JSON, e depois compila esses dados em um arquivo Excel filtrado.

## Funcionalidades

- Coleta dados paginados da API PNCP para um intervalo de datas específico e modalidades de contratação.
- Salva os dados em arquivos JSON.
- Compila e filtra os dados coletados em um arquivo Excel.

## Requisitos

- Python 3.6 ou superior
- Bibliotecas: `requests`, `pandas`, `tqdm`

## Instalação

Clone o repositório e instale as bibliotecas necessárias.

```bash
git clone https://github.com/seu_usuario/seu_repositorio.git
cd seu_repositorio
pip install -r requirements.txt
