import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

PASTA_DADOS = os.path.join(os.getcwd(), "cliente 1", "MeusDadosLGPD")
ARQUIVO_DADOS = "informaçoes.txt"

# Funções de validação ---------------------------------------------

def validar_cpf(cpf):
    return cpf.isdigit() and len(cpf) == 11

def validar_nome(nome):
    return nome.replace(" ", "").isalpha()

def obter_consentimento():
    print("Seus dados (nome, CPF e idade) serão guardados sob sigilo, não serão usados para fins indevidos.")
    print("Você poderá solicitar a exclusão a qualquer momento.")
    resposta = input("Você concorda com isso? (s/n): ").strip().lower()
    return resposta == "s"

dados = []

# Funções principais -----------------------------------------------

def cadastrar_pessoa():
    try:
        if not obter_consentimento():
            print("Cadastro cancelado. Consentimento não concedido.")
            return

        nome = input("Nome completo: ").strip().title()
        if not validar_nome(nome):
            raise ValueError("Nome inválido. Use apenas letras.")

        cpf = input("CPF (somente números): ").strip()
        if not validar_cpf(cpf):
            raise ValueError("CPF inválido. Deve conter 11 dígitos numéricos.")

        idade = int(input("Idade: "))

        pessoa = {
            "nome": nome,
            "cpf": cpf,
            "idade": idade
        }

        dados.append(pessoa)
        print("✅ Pessoa cadastrada com sucesso!")

        salvar = input("Deseja salvar essas informações no arquivo? (s/n): ").strip().lower()
        if salvar == 's':
            if not os.path.exists(PASTA_DADOS):
                os.makedirs(PASTA_DADOS)
            caminho_arquivo = os.path.join(PASTA_DADOS, ARQUIVO_DADOS)
            with open(caminho_arquivo, "a", encoding="utf-8") as f:
                f.write(json.dumps(pessoa, ensure_ascii=False) + "\n")
            print(f"✅ Dados salvos no arquivo {caminho_arquivo}")

    except ValueError as e:
        print(f"Erro: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

def buscar_por_cpf(cpf):
    return [p for p in dados if p["cpf"] == cpf]

def buscar_por_nome(nome_busca):
    nome_busca = nome_busca.strip().lower()
    return [p for p in dados if nome_busca in p["nome"].lower()]

def filtrar_por_idade(min_idade):
    return [p for p in dados if p["idade"] >= min_idade]

def excluir_por_cpf(cpf):
    global dados
    original_len = len(dados)
    dados = [p for p in dados if p["cpf"] != cpf]
    if len(dados) < original_len:
        print("Usuário excluído com sucesso!")
    else:
        print("CPF não encontrado.")

def visualizar_dados_pessoais():
    cpf = input("Digite o CPF para consulta: ").strip()
    pessoa = buscar_por_cpf(cpf)
    if pessoa:
        print(pessoa)
    else:
        print("CPF não encontrado.")

# Servidor HTTP básico ---------------------------------------------

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length)
        texto = post_data.decode('utf-8')

        if not os.path.exists(PASTA_DADOS):
            os.makedirs(PASTA_DADOS)

        caminho_arquivo = os.path.join(PASTA_DADOS, ARQUIVO_DADOS)
        with open(caminho_arquivo, "a", encoding="utf-8") as f:
            f.write(texto + "\n")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Dados recebidos e salvos.')

def iniciar_servidor():
    servidor = HTTPServer(('0.0.0.0', 8000), RequestHandler)
    print("Servidor HTTP rodando em http://localhost:8000")
    servidor.serve_forever()

# Menu do programa -------------------------------------------------

def menu():
    while True:
        print("\n--- MENU ---")
        print("1. Cadastrar pessoa")
        print("2. Buscar por CPF")
        print("3. Buscar por nome")
        print("4. Filtrar por idade")
        print("5. Excluir por CPF")
        print("6. Visualizar Dados Pessoais")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_pessoa()
        elif opcao == "2":
            cpf = input("Digite o CPF para busca: ")
            resultado = buscar_por_cpf(cpf)
            print(resultado if resultado else "Nenhuma pessoa encontrada.")
        elif opcao == "3":
            nome = input("Digite o nome (ou parte dele): ")
            resultado = buscar_por_nome(nome)
            print(resultado if resultado else "Nenhuma pessoa encontrada.")
        elif opcao == "4":
            idade = int(input("Idade mínima: "))
            print(filtrar_por_idade(idade))
        elif opcao == "5":
            cpf = input("Digite o CPF para exclusão: ")
            excluir_por_cpf(cpf)
        elif opcao == "6":
            visualizar_dados_pessoais()
        else:
            print("Opção inválida.")

# Executando -------------------------------------------------------

if __name__ == "__main__":
    thread_servidor = threading.Thread(target=iniciar_servidor, daemon=True)
    thread_servidor.start()

    menu()
