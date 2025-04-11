from flask import Flask, jsonify, request
from flask_pydantic_spec import FlaskPydanticSpec
from sqlalchemy.exc import IntegrityError

from models import *
from sqlalchemy import select

app = Flask(__name__)

spec = FlaskPydanticSpec('flask',
                         title='Livraria API - SENAI',
                         version='1.0.0')
spec.register(app)

app.config['SECRET_KEY'] = 'vc_senha_sua_protecao'

"""
try
"""
@app.route('/livros', methods=['POST'])
def cadastrar_livro():
    try:
        dados_livro = request.get_json()
        # Captura os valores dos campos do formulário
        titulo = dados_livro['titulo']
        autor = dados_livro["autor"]
        ISBN = dados_livro["ISBN"]
        resumo = dados_livro["resumo"]

        # Validação de cada campo
        if not titulo:
            return jsonify({"mensagem": "erro no titulo"})
        if not autor:
            return jsonify({"mensagem": "erro no autor"})
        if not ISBN:
            return jsonify({"mensagem": "erro no ISBN"})
        if not resumo:
            return jsonify({"mensagem": "erro no resumo"})

        # Se todos os campos estiverem preenchidos, cria o Livro
        form_evento = Livro(
            titulo=titulo,
            autor=autor,
            ISBN=ISBN,
            resumo=resumo
        )
        form_evento.save()
        return jsonify({"mensagem": "Livro criado com sucesso!"})
    except ValueError:
        return jsonify({"mensagem": "formato invalido"})

@app.route('/livros', methods=['GET'])
def listar_livro():
    lista = db_session.execute(select(Livro)).scalars().all()
    resultados = []
    for livro in lista:
        resultados.append(livro.serialize())
    return jsonify(resultados)


@app.route('/livros/<int:id_livro>', methods=['PUT'])
def editar_livro(id_livro):
    # Fetch the task from the database
    livro = db_session.execute(select(Livro).where(Livro.id_livro == id_livro)).scalar()

    if livro is None:
        return jsonify({"mensagem": "Livro não encontrado."})

    dados_livro = request.get_json()
    # Captura os valores dos campos do formulário
    titulo = dados_livro['titulo']
    autor = dados_livro["autor"]
    ISBN = dados_livro["ISBN"]
    resumo = dados_livro["resumo"]

    livro.titulo = titulo
    livro.autor = autor
    livro.ISBN = ISBN
    livro.resumo = resumo

    # Save changes to the database
    livro.save()
    return jsonify({"mensagem": "Livro atualizado com sucesso!"})


@app.route('/livros/<int:id_livro>', methods=['DELETE'])
def deletar_livro(id_livro):

    var_livro = select(Livro).where(Livro.id_livro == id_livro)
    var_livro = db_session.execute(var_livro).scalar()
    var_livro.delete()

    return jsonify({"mensagem": "Livro deletado com sucesso!"})

@app.route('/usuarios', methods=['POST'])
def cadastrar_usuario():
    try:
        dados_usuario = request.get_json()
        # Captura os valores dos campos do formulário
        nome = dados_usuario['nome']
        CPF = dados_usuario["CPF"]
        endereco = dados_usuario["endereco"]

        # Validação de cada campo
        if not nome:
            return jsonify({"mensagem": "erro no nome"})
        if not CPF:
            return jsonify({"mensagem": "erro no CPF"})
        if not endereco:
            return jsonify({"mensagem": "erro no endereco"})

        # Se todos os campos estiverem preenchidos, cria o usuario
        form_evento = Usuario(
            nome=nome,
            CPF=CPF,
            endereco=endereco,
        )
        form_evento.save()
        return jsonify({"mensagem": "Usuario criado com sucesso!"})
    except ValueError:
        return jsonify({"mensagem": "formato invalido"})
    except IntegrityError:
        return jsonify({"mensagem": "CPF inválido"})

@app.route('/usuarios', methods=['GET'])
def listar_usuario():
    lista = db_session.execute(select(Usuario)).scalars().all()
    resultados = []
    for usuario in lista:
        resultados.append(usuario.serialize())
    return jsonify(resultados)


@app.route('/usuarios/<int:id_usuario>', methods=['PUT'])
def editar_usuario(id_usuario):
    # Fetch the task from the database
    usuario = db_session.execute(select(Usuario).where(Usuario.id_usuario == id_usuario)).scalar()

    if usuario is None:
        return jsonify({"mensagem": "usuario não encontrado."})

    dados_usuario = request.get_json()
    # Captura os valores dos campos do formulário
    nome = dados_usuario['nome']
    CPF = dados_usuario["CPF"]
    endereco = dados_usuario["endereco"]

    usuario.nome = nome
    usuario.CPF = CPF
    usuario.endereco = endereco

    # Save changes to the database
    usuario.save()
    return jsonify({"mensagem": "usuario atualizado com sucesso!"})


@app.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
def deletar_usuario(id_usuario):

    var_usuario = select(Usuario).where(Usuario.id_usuario == id_usuario)
    var_usuario = db_session.execute(var_usuario).scalar()
    var_usuario.delete()

    return jsonify({"mensagem": "usuario deletado com sucesso!"})

@app.route('/emprestimos', methods=['POST'])
def cadastrar_emprestimo():
    try:
        dados_emprestimo = request.get_json()
        # Captura os valores dos campos do formulário
        data_emprestimo = dados_emprestimo['data_emprestimo']
        data_devolucao = dados_emprestimo["data_devolucao"]
        livro_id = dados_emprestimo["livro_id"]
        usuario_id = dados_emprestimo["usuario_id"]

        # Validação de cada campo
        if not data_emprestimo:
            return jsonify({"mensagem": "erro na data_emprestimo"})
        if not data_devolucao:
            return jsonify({"mensagem": "erro na data_devolucao"})
        if not livro_id:
            return jsonify({"mensagem": "erro no livro_id"})
        if not usuario_id:
            return jsonify({"mensagem": "erro no usuario_id"})

        # Se todos os campos estiverem preenchidos, cria o emprestimo
        form_evento = Emprestimo(
            data_emprestimo=data_emprestimo,
            data_devolucao=data_devolucao,
            livro_id=livro_id,
            usuario_id=usuario_id
        )
        form_evento.save()
        return jsonify({"mensagem": "Emprestimo criado com sucesso!"})
    except ValueError:
        return jsonify({"mensagem": "formato invalido"})

@app.route('/emprestimos', methods=['GET'])
def listar_emprestimo():
    lista = db_session.execute(select(Emprestimo)).scalars().all()
    resultados = []
    for emprestimo in lista:
        resultados.append(emprestimo.serialize())
    return jsonify(resultados)


@app.route('/emprestimos/<int:id_emprestimo>', methods=['PUT'])
def editar_emprestimo(id_emprestimo):
    # Fetch the task from the database
    emprestimo = db_session.execute(select(Emprestimo).where(Emprestimo.id_emprestimo == id_emprestimo)).scalar()

    if emprestimo is None:
        return jsonify({"mensagem": "emprestimo não encontrado."})

    dados_emprestimo = request.get_json()
    # Captura os valores dos campos do formulário
    titulo = dados_emprestimo['titulo']
    data_devolucao = dados_emprestimo["data_devolucao"]
    livro_id = dados_emprestimo["livro_id"]
    usuario_id = dados_emprestimo["usuario_id"]

    emprestimo.titulo = titulo
    emprestimo.data_devolucao = data_devolucao
    emprestimo.livro_id = livro_id
    emprestimo.usuario_id = usuario_id

    # Save changes to the database
    emprestimo.save()
    return jsonify({"mensagem": "emprestimo atualizado com sucesso!"})


@app.route('/emprestimos/<int:id_emprestimo>', methods=['DELETE'])
def deletar_emprestimo(id_emprestimo):

    var_emprestimo = select(Emprestimo).where(Emprestimo.id_emprestimo == id_emprestimo)
    var_emprestimo = db_session.execute(var_emprestimo).scalar()
    var_emprestimo.delete()

    return jsonify({"mensagem": "emprestimo deletado com sucesso!"})

if __name__ == '__main__':
    app.run(debug=True)