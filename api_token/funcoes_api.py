import requests
from api_local import *
def get_usuario():
    url = "http://10.135.232.36:5000/consultar_usuarios"
    response = requests.get(url)
    if response.status_code == 200:
        dados = response.json()
        # print(dados['usuarios_cadastrados'])
        # for u in dados['usuarios_cadastrados']:
        #     print(u['CPF'])

        print(dados['usuarios_cadastrados'][0]['CPF'])

def get_livros():
    headers = {"Authorization": f"Bearer {self.token}"}
    url = "http://10.135.232.36:5000/consultar_livros"
    response = requests.get(f"{url}/livros", headers=headers)
    if response.status_code == 200:
        dados = response.json()
        for l in dados:
            print(l)

def post_livro(titulo, autor, resumo, isbn):
    url = "http://10.135.232.36:5000/cadastrar_livro"
    livro = {"titulo": titulo,
             "autor": autor,
             "resumo": resumo,
             "isbn": isbn}
    response = requests.post(url, json=livro)
    if response.status_code == 200:
        print("Livro cadastrado com sucesso!")
        dados_post = response.json()
        print(dados_post)
    else:
        print("Erro ao cadastrar livro!")
post_livro('titulo','autor','resumo',47795753892)
