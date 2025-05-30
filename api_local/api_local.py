from flask import Flask, jsonify, request, redirect
from flask_pydantic_spec import FlaskPydanticSpec
from sqlalchemy.exc import IntegrityError

from models_local import *
from sqlalchemy import select

app = Flask(__name__)
spec = FlaskPydanticSpec('flask',
                         title='Livraria API - SENAI',
                         version='1.0.0')
spec.register(app)
app.config['SECRET_KEY'] = 'chave_secretinha'

@app.route('/')
def index():
    """
        API para gerenciar uma biblioteca integrada a um banco de dados

    """
    return redirect('/livros')
@app.route('/livros', methods=['POST'])
def post_livro():
    """
            Cadastrar livros

            ### Endpoint:
                POST /livros

            ### Erros possíveis:
            - **Bad Request**: *status code* **400**

            ### Retorna:
            - **JSON** mensagem de **sucesso**
    """
    db_session = local_session()
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
        form_evento.save(db_session)
        db_session.close()
        return jsonify({'result': 'Livro criado com sucesso!'}), 200
    except ValueError:
        return jsonify({"mensagem": "formato invalido"})

@app.route('/livros', methods=['GET'])
def get_livro():
    """
            Consultar livros

            ### Endpoint:
                GET /livros
                GET /livros/<status>

            ### Parâmetros:
            - `status` **(str)**: **string para ser convertida a boolean**

            ### Erros possíveis:
            - **Bad Request**: *status code* **400**

            ### Retorna:
            - **JSON** com a lista de livros e dados
            - **JSON** com a lista de livros e dados que possuam o `status` igual ao recebido de parâmetro
        """
    db_session = local_session()
    try:
        lista = db_session.execute(select(Livro)).scalars().all()
        resultados = []
        for livro in lista:
            resultados.append(livro.serialize())
        return jsonify(resultados)
    except ValueError:
        return jsonify({"mensagem": "Formato inválido."}), 400
    except TypeError:
        return jsonify({'result': 'Error. Integrity Error (faltam informações ou informações corretas) '}), 400
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        db_session.close()


@app.route('/livros/<int:id_livro>', methods=['PUT'])
def put_livro(id_livro):
    """
            Editar livros

            ### Endpoint:
                PUT /livros/<id_livro>

            ### Parâmetros:
            - `id_livro` **(str)**: **string para ser convertida a inteiro**

            ### Erros possíveis:
            - **Bad Request**: *status code* **400**

            ### Retorna:
            - **JSON** mensagem de **sucesso**
        """
    db_session = local_session()
    try:
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
        livro.save(db_session)
        return jsonify({"mensagem": "Livro atualizado com sucesso!"})
    except ValueError:
        return jsonify({"mensagem": "Formato inválido."}), 400
    except TypeError:
        return jsonify({'result': 'Error. Integrity Error (faltam informações ou informações corretas) '}), 400
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        db_session.close()

@app.route('/livros/<int:id_livro>', methods=['DELETE'])
def delete_livro(id_livro):
    db_session = local_session()
    try:
        var_livro = select(Livro).where(Livro.id_livro == id_livro)
        var_livro = db_session.execute(var_livro).scalar()
        var_livro.delete(db_session)
        return jsonify({"mensagem": "Livro deletado com sucesso!"})
    except ValueError:
        return jsonify({"mensagem": "Formato inválido."}), 400
    except TypeError:
        return jsonify({'result': 'Error. Integrity Error (faltam informações ou informações corretas) '}), 400
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        db_session.close()

@app.route('/usuarios', methods=['POST'])
def post_usuario():
    """
        Cadastrar usuario

        ### Endpoint:
            POST /usuarios

        ### Erros possíveis:
        - **Bad Request**: *status code* **400**

        ### Retorna:
        - **JSON** mensagem de **sucesso**
    """
    db_session = local_session()
    try:
        dados_usuario = request.get_json()
        # Captura os valores dos campos do formulário
        nome = dados_usuario['nome']
        CPF = dados_usuario["CPF"]
        endereco = dados_usuario["endereco"]
        cpf = str(CPF)
        if not nome or not cpf or not endereco or len(cpf) != 11:
            return jsonify({'result': 'Error. Integrity Error (faltam informações) '}), 400
        else:
            cpf_f = '{0}.{1}.{2}-{3}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])
            post = Usuario(nome=nome, CPF=cpf_f, endereco=endereco)
            post.save(db_session)
            db_session.close()
            return jsonify({'mensagem': 'Usuario criado com sucesso!'}), 200
    except ValueError:
        return jsonify({"mensagem": "formato invalido"})
    except IntegrityError:
        return jsonify({"mensagem": "CPF inválido"})
    except TypeError:
        return jsonify({'mensagem': 'Error. Integrity Error (faltam informações ou informações corretas) '}), 400
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        db_session.close()

@app.route('/usuarios', methods=['GET'])
def get_usuario():
    """
        Consultar emprestimos

        ### Endpoint:
            GET /emprestimos

        ### Erros possíveis:
        - **Bad Request**: *status code* **400**

        ### Retorna:
        - **JSON** com a lista de emprestimos
    """
    db_session = local_session()
    try:
        lista = db_session.execute(select(Usuario)).scalars().all()
        resultados = []
        for usuario in lista:
            resultados.append(usuario.serialize())
        return jsonify(resultados)
    except ValueError:
        return jsonify({"mensagem": "formato invalido"})


@app.route('/usuarios/<int:id_usuario>', methods=['PUT'])
def put_usuario(id_usuario):
    """
            Editar usuarios

            ### Endpoint:
                PUT /usuarios/<id_user>

            ### Parâmetros:
            - `id_user` **(str)**: **string para ser convertida a inteiro**

            ### Erros possíveis:
            - **Bad Request**: *status code* **400**

            ### Retorna:
            - **JSON** mensagem de **sucesso**
    """
    db_session = local_session()
    try:
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

        usuario.save(db_session)
        return jsonify({'result': 'Usuario editado com sucesso!'}), 200

    except ValueError:
        return jsonify({"mensagem": "Formato inválido."}), 400
    except TypeError:
        return jsonify({'mensagem': 'Error. (faltam informações ou informações corretas)'}), 400
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        db_session.close()

@app.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
def delete_usuario(id_usuario):
    db_session = local_session()
    try:
        var_usuario = select(Usuario).where(Usuario.id_usuario == id_usuario)
        var_usuario = db_session.execute(var_usuario).scalar()
        var_usuario.delete(db_session)

        return jsonify({"mensagem": "usuario deletado com sucesso!"})
    except ValueError:
        return jsonify({"mensagem": "Formato inválido."}), 400
    except TypeError:
        return jsonify({'result': 'Error. Integrity Error (faltam informações ou informações corretas) '}), 400
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        db_session.close()

@app.route('/emprestimos', methods=['POST'])
def post_emprestimo():
    """
            Cadastrar emprestimos

            ### Endpoint:
                POST /emprestimos

            ### Erros possíveis:
            - **Bad Request**: *status code* **400**

            ### Retorna:
            - **JSON** mensagem de **sucesso**
    """
    db_session = local_session()
    try:
        dados_emprestimo = request.get_json()

        # Captura os valores dos campos do formulário
        data_emprestimo = dados_emprestimo['data_emprestimo']
        data_devolucao = dados_emprestimo["data_devolucao"]
        livro_id = dados_emprestimo["livro_id"]
        usuario_id = dados_emprestimo["usuario_id"]

        # Verifica se os valores "livro_id" e "usuario_id" já estão cadastrados
        livro = db_session.execute(select(Livro).where(Livro.id_livro == livro_id)).scalar()
        usuario = db_session.execute(select(Usuario).where(Usuario.id_usuario == usuario_id)).scalar()

        if not livro:
            if not usuario:
                return jsonify({"mensagem": "Livro e Usuário não encontrados."}), 404
            else:
                return jsonify({"mensagem": "Livro não encontrado."}), 404
        if not usuario:
            return jsonify({"mensagem": "Usuário não encontrado."}), 404

        # Verifica se o livro e o usuário já estão cadastrados em um empréstimo
        emprestimo_existente = db_session.execute(
            select(Emprestimo).where(
                (Emprestimo.livro_id == livro_id) &
                (Emprestimo.usuario_id == usuario_id)
            )
        ).scalar()

        if emprestimo_existente:
            return jsonify({"mensagem": "Este livro já está emprestado para este usuário."}), 409

        # Cria a instância do empréstimo
        novo_emprestimo = Emprestimo(
            data_emprestimo=data_emprestimo,
            data_devolucao=data_devolucao,
            livro_id=livro_id,
            usuario_id=usuario_id
        )
        db_session.add(novo_emprestimo)
        db_session.commit()

        return jsonify({"mensagem": "Empréstimo criado com sucesso!"}), 201
    except ValueError:
        return jsonify({"mensagem": "Formato inválido."}), 400
    except TypeError:
        return jsonify({'result': 'Error. Integrity Error (faltam informações ou informações corretas) '}), 400
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        db_session.close()


@app.route('/emprestimos', methods=['GET'])
def get_emprestimo():
    """
            Consultar emprestimos

            ### Endpoint:
                GET /emprestimos

            ### Erros possíveis:
            - **Bad Request**: *status code* **400**

            ### Retorna:
            - **JSON** com a lista de emprestimos
    """
    db_session = local_session()
    try:
        lista = db_session.execute(select(Emprestimo)).scalars().all()
        resultados = []
        for emprestimo in lista:
            resultados.append(emprestimo.serialize())
        return jsonify(resultados)
    except ValueError:
        return jsonify({"mensagem": "Formato inválido."}), 400
    except TypeError:
        return jsonify({'result': 'Error. Integrity Error (faltam informações ou informações corretas) '}), 400
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        db_session.close()


@app.route('/emprestimos/<int:id_emprestimo>', methods=['PUT'])
def put_emprestimo(id_emprestimo):
    """
            Editar emprestimos

            ### Endpoint:
                PUT /emprestimos/<id_emp>

            ### Parâmetros:
            - `id_emp` **(str)**: **string para ser convertida a inteiro**

            ### Erros possíveis:
            - **Bad Request**: *status code* **400**

            ### Retorna:
            - **JSON** mensagem de **sucesso**
        """
    db_session = local_session()
    try:
        # Fetch the task from the database
        emprestimo = db_session.execute(select(Emprestimo).where(Emprestimo.id_emprestimo == id_emprestimo)).scalar()

        if emprestimo is None:
            return jsonify({"mensagem": "emprestimo não encontrado."})

        dados_emprestimo = request.get_json()
        # Captura os valores dos campos do formulário
        data_emprestimo = dados_emprestimo['data_emprestimo']
        data_devolucao = dados_emprestimo["data_devolucao"]
        livro_id = dados_emprestimo["livro_id"]
        usuario_id = dados_emprestimo["usuario_id"]

        emprestimo.titulo = data_emprestimo
        emprestimo.data_devolucao = data_devolucao
        emprestimo.livro_id = livro_id
        emprestimo.usuario_id = usuario_id

        # Save changes to the database
        emprestimo.save(db_session)

        return jsonify({"mensagem": "emprestimo atualizado com sucesso!"})
    except ValueError:
        return jsonify({"mensagem": "Formato inválido."}), 400
    except TypeError:
        return jsonify({'result': 'Error. Integrity Error (faltam informações ou informações corretas) '}), 400
    except Exception as e:
        return jsonify({"mensagem": str(f"erro no {e}")}), 500
    finally:
        db_session.close()


@app.route('/emprestimos/<int:id_emprestimo>', methods=['DELETE'])
def delete_emprestimo(id_emprestimo):
    db_session = local_session()
    try:
        var_emprestimo = select(Emprestimo).where(Emprestimo.id_emprestimo == id_emprestimo)
        var_emprestimo = db_session.execute(var_emprestimo).scalar()
        var_emprestimo.delete(db_session)

        return jsonify({"mensagem": "emprestimo deletado com sucesso!"})
    except ValueError:
        return jsonify({"mensagem": "Formato inválido."}), 400
    except TypeError:
        return jsonify({'result': 'Error. Integrity Error (faltam informações ou informações corretas) '}), 400
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        db_session.close()

if __name__ == '__main__':
    app.run(debug=True)