from flask import Flask, jsonify, request
from flask_pydantic_spec import FlaskPydanticSpec
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
            return jsonify({"erro no titulo"})
        if not autor:
            return jsonify({"erro no titulo"})
        if not ISBN:
            return jsonify({"erro no titulo"})
        if not resumo:
            return jsonify({"erro no resumo"})

        # Se todos os campos estiverem preenchidos, cria o Livro
        form_evento = Livro(
            titulo=titulo,
            autor=autor,
            ISBN=ISBN,
            resumo=resumo
        )
        form_evento.save()
        return jsonify("Livro criado com sucesso!", "success")
    except ValueError:
        return jsonify({"formato invalido"})

@app.route('/livros', methods=['GET'])
def listar_livro():
    lista = db_session.execute(select(Livro)).scalars().all()
    resultados = []
    for livro in lista:
        resultados.append(livro.serialize())
    return jsonify(resultados)


@app.route('/livros/<int:id_livro>', methods=['PUT'])
def editar(id_livro):
    # Fetch the task from the database
    livro = db_session.execute(select(Livro).where(Livro.id_livro == id_livro)).scalar()
    dados_livro = request.get_json()
    if livro is None:
        return jsonify("Livro não encontrado.")

    # Captura os valores dos campos do formulário
    titulo = dados_livro['titulo']
    autor = dados_livro["autor"]
    ISBN = dados_livro["ISBN"]
    resumo = dados_livro["resumo"]

    # Save changes to the database
    db_session.commit()
    return jsonify("Livro atualizado com sucesso!")



@app.route('/delete/<int:id_livro>', methods=['GET'])
def deletar(id_livro):

    var_livro = select(Livro).where(Livro.id_livro == id_livro)
    var_livro = db_session.execute(var_livro).scalar()
    var_livro.delete()

    return jsonify("Livro atualizado com sucesso!")

if __name__ == '__main__':
    app.run(debug=True)
