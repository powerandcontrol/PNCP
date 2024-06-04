import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import contratos, contratacoes_publicacao, contratacaoes_proposta

# Funções personalizadas para cada botão
def contrato():
    contratos.main()
 
def contratacao_publicacao():
    contratacoes_publicacao.main()
    
def contratacao_proposta():
    contratacaoes_proposta.main()

# Criação da janela principal
root = tk.Tk()
root.title("PNCP")
root.geometry("563x371")
root.configure(bg="#333333")

root.iconbitmap("icon.ico")

# Impede que a janela seja redimensionada
root.resizable(False, False)

# Cria os frames para a estrutura da interface
frame_left = tk.Frame(root, width=218, height=371)
frame_left.grid(row=0, column=0, sticky="nsew")
frame_right = tk.Frame(root, bg="#FFFFFF", width=345, height=371)
frame_right.grid(row=0, column=1, sticky="nsew")

# Ajusta as colunas para ocupar a tela inteira
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Carregar e exibir a imagem como plano de fundo do frame esquerdo
image_path = "frame_esquerdo.png"  # Substitua pelo caminho da sua imagem
image = Image.open(image_path)
image = image.resize((218, 371))  # Redimensionar a imagem se necessário
photo = ImageTk.PhotoImage(image)

canvas = tk.Canvas(frame_left, width=130, height=371,)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, anchor="nw", image=photo)

# Botões do Menu
button1 = tk.Button(frame_right, text="Contratações por Data de Publicação", command=lambda: contratacao_publicacao(), bg="#007bff", fg="white", font=("Arial", 10))
button1.grid(row=1, column=0, pady=(130, 10), padx=20, sticky="ew")

button2 = tk.Button(frame_right, text="Contratações em Aberto", command=lambda: contratacao_proposta(), bg="#DCA50A", fg="white", font=("Arial", 10))
button2.grid(row=2, column=0, pady=5, padx=20, sticky="ew")

button3 = tk.Button(frame_right, text="Contratos por Data de Publicação", command=lambda: contrato(), bg="#28a745", fg="white", font=("Arial", 10))
button3.grid(row=3, column=0, pady=5, padx=20, sticky="ew")

# Ajusta as colunas do frame_right para expandir
frame_right.grid_columnconfigure(0, weight=1)

root.mainloop()
