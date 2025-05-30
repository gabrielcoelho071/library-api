from flask import Flask, jsonify, request, redirect
from flask_pydantic_spec import FlaskPydanticSpec
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from functools import wraps
from models_local import Usuario, Livro, local_session, init_db, Emprestimo
from sqlalchemy import select

app = Flask(__name__)
spec = FlaskPydanticSpec('flask',
                         title='Livraria API - SENAI',
                         version='1.0.0')
spec.register(app)
app.config["JWT_SECRET_KEY"] = "senha_SECRETINHA"
jwt = JWTManager(app)

# ---------------- DECORADOR ADMIN ----------------
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        db = local_session()
        try:
            id = get_jwt_identity()
            usuario = db.execute(select(Usuario).where(Usuario.id_usuario == id)).scalar()
            if usuario and usuario.papel == 'admin':
                return fn(*args, **kwargs)
            return jsonify({"msg": "Acesso negado: apenas administradores"}), 403
        finally:
            db.close()
    return wrapper

@app.route('/')
def index():
    """
        API para gerenciar uma biblioteca integrada a um banco de dados

    """
    return redirect('/livros')

@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    nome = dados['nome']
    senha = dados['senha']
    with local_session() as db_session:
        try:
            user = db_session.execute(select(Usuario).where(Usuario.nome == nome)).scalar()
            if user and user.check_password(senha):
                access_token = create_access_token(identity=str(user.id_usuario))
                return jsonify(access_token=access_token), 200
            return jsonify({"mensagem": "Credenciais inválidas."}), 401
        except Exception as e:
            return jsonify({"mensagem": str(e)}), 500

@app.route('/livros', methods=['POST'])
@admin_required
@jwt_required()
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
        titulo = dados_livro.get('titulo')
        autor = dados_livro.get("autor")
        ISBN = dados_livro.get("ISBN")
        resumo = dados_livro.get("resumo")

        # Validação de campos obrigatórios
        if not all([titulo, autor, ISBN, resumo]):
            return jsonify({"mensagem": "Todos os campos são obrigatórios"}), 400

        # Se todos os campos estiverem preenchidos, cria o Livro
        form_evento = Livro(
            titulo=titulo,
            autor=autor,
            ISBN=ISBN,
            resumo=resumo,
            status=True
        )
        form_evento.save(db_session)
        db_session.close()
        return jsonify({'result': 'Livro criado com sucesso!'}), 200
    except ValueError:
        return jsonify({"mensagem": "formato invalido"}), 400
    finally:
        db_session.close()

@app.route('/livros', methods=['GET'])
@jwt_required()
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
@admin_required
@jwt_required()
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
    Cadastrar usuário

    ### Endpoint:
        POST /usuarios

    ### Corpo da Requisição (JSON):
    {
        "nome": "João da Silva",
        "CPF": "12345678901",
        "endereco": "Rua Exemplo, 123",
        "papel": "admin"  # ou "usuario"
    }

    ### Erros possíveis:
    - 400: Faltam informações ou CPF inválido
    - 500: Erro interno

    ### Retorna:
    - 200: Usuário criado com sucesso
    """
    db_session = local_session()
    try:
        dados = request.get_json()

        nome = dados.get('nome')
        cpf = str(dados.get('CPF', '')).replace('.', '').replace('-', '')
        endereco = dados.get('endereco')
        papel = dados.get('papel', 'usuario')  # valor padrão: usuario
        senha = dados.get('senha')

        # Validações básicas
        if not nome or not cpf or not senha or not endereco or len(cpf) != 11:
            return jsonify({"mensagem": "Dados incompletos ou CPF inválido."}), 400

        # Formata CPF
        cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

        # Verifica duplicidade de CPF
        usuario_existente = db_session.execute(
            select(Usuario).where(Usuario.CPF == cpf_formatado)
        ).scalar()
        if usuario_existente:
            return jsonify({"mensagem": "Usuário com este CPF já existe."}), 400

        novo_usuario = Usuario(
            nome=nome,
            CPF=cpf_formatado,
            endereco=endereco,
            papel=papel
        )
        novo_usuario.set_senha_hash(senha)
        novo_usuario.save(db_session)
        return jsonify({"mensagem": "Usuário criado com sucesso!"}), 201

    except IntegrityError:
        db_session.rollback()
        return jsonify({"mensagem": "Erro de integridade (CPF duplicado ou inválido)."}), 400
    except Exception as e:
        db_session.rollback()
        return jsonify({"mensagem": f"Erro interno: {str(e)}"}), 500
    finally:
        db_session.close()


@app.route('/usuarios', methods=['GET'])
@jwt_required()
def get_usuario():
    """
        Consultar usuários

        ### Endpoint:
            GET /usuarios

        ### Comportamento:
        - Usuários com papel 'admin' podem visualizar todos os usuários.
        - Usuários com papel 'cliente' ou 'usuario' podem visualizar apenas seus próprios dados.

        ### Erros possíveis:
        - **Bad Request**: *status code* **400**
        - **Forbidden**: *status code* **403** (caso o usuário não tenha permissão)
        - **Internal Server Error**: *status code* **500**

        ### Retorna:
        - **JSON** com a lista de usuários (para admin) ou dados do usuário autenticado (para cliente/usuario)
    """
    with local_session() as db_session:
        try:
            # Obtém o ID do usuário autenticado a partir do JWT
            current_user_id = get_jwt_identity()
            # Busca o usuário autenticado no banco de dados para verificar o papel
            usuario_autenticado = db_session.execute(
                select(Usuario).where(Usuario.id_usuario == current_user_id)
            ).scalars().first()
            if not usuario_autenticado:
                return jsonify({"mensagem": "Usuário não encontrado."}), 404

            # Verifica o papel do usuário
            if usuario_autenticado.papel == 'admin':
                # Admin pode ver todos os usuários
                lista = db_session.execute(select(Usuario)).scalars().all()
                return jsonify([usuario.serialize() for usuario in lista])
            else:
                # Usuários normais (cliente ou usuario) veem apenas os seus próprios dados
                return jsonify(usuario_autenticado.serialize())

        except ValueError:
            return jsonify({"mensagem": "Formato inválido."}), 400
        except Exception as e:
            return jsonify({"mensagem": str(e)}), 500
        finally:
            db_session.close()

@app.route('/usuarios/<int:id_usuario>', methods=['PUT'])
@admin_required
@jwt_required()
def put_usuario_admin(id_usuario):
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
    with local_session() as db_session:
        try:
            # Fetch the task from the database
            usuario = db_session.execute(select(Usuario).where(Usuario.id_usuario == id_usuario)).scalar()

            if usuario is None:
                return jsonify({"mensagem": "usuario não encontrado."})

            dados_usuario = request.get_json()
            # Captura os valores dos campos do formulário
            nome = dados_usuario['nome']
            cpf = str(dados_usuario.get('CPF', '')).replace('.', '').replace('-', '')
            endereco = dados_usuario["endereco"]

            # Validações básicas
            if not nome or not cpf or not endereco or len(cpf) != 11:
                return jsonify({"mensagem": "Dados incompletos ou CPF inválido."}), 400

            # Formata CPF
            cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

            # Verifica duplicidade de CPF
            usuario_existente = db_session.execute(
                select(Usuario).where(Usuario.CPF == cpf_formatado)
            ).scalar()
            if usuario_existente:
                return jsonify({"mensagem": "Usuário com este CPF já existe."}), 400

            usuario.nome = nome
            usuario.CPF = cpf_formatado
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

@app.route('/usuarios', methods=['PUT'])
@jwt_required()
def put_usuario():
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
    with local_session() as db_session:
        try:
            # Obtém o ID do usuário autenticado a partir do JWT
            current_user_id = get_jwt_identity()
            # Busca o usuário autenticado no banco de dados para verificar o papel
            usuario_autenticado = db_session.execute(
                select(Usuario).where(Usuario.CPF == current_user_id)
            ).scalars().first()
            if not usuario_autenticado:
                return jsonify({"mensagem": "Usuário não encontrado."}), 404

            dados_usuario = request.get_json()
            # Captura os valores dos campos do formulário
            nome = dados_usuario['nome']
            cpf = str(dados_usuario.get('CPF', '')).replace('.', '').replace('-', '')
            endereco = dados_usuario["endereco"]

            # Validações básicas
            if not nome or not cpf or not endereco or len(cpf) != 11:
                return jsonify({"mensagem": "Dados incompletos ou CPF inválido."}), 400

            # Formata CPF
            cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

            # Verifica duplicidade de CPF
            usuario_existente = db_session.execute(
                select(Usuario).where(Usuario.CPF == cpf_formatado)
            ).scalar()
            if usuario_existente:
                return jsonify({"mensagem": "Usuário com este CPF já existe."}), 400

            usuario_autenticado.nome = nome
            usuario_autenticado.CPF = cpf_formatado
            usuario_autenticado.endereco = endereco

            usuario_autenticado.save(db_session)
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
@jwt_required()
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
        # Obtém o ID do usuário autenticado a partir do JWT
        current_user_id = get_jwt_identity()
        # Busca o usuário autenticado no banco de dados para verificar o papel
        usuario_autenticado = db_session.execute(
            select(Usuario).where(Usuario.id_usuario == current_user_id)
        ).scalars().first()
        if not usuario_autenticado:
            return jsonify({"mensagem": "Usuário não encontrado."}), 404

        dados_emprestimo = request.get_json()

        # Captura os valores dos campos do formulário
        data_emprestimo = dados_emprestimo['data_emprestimo']
        data_devolucao = dados_emprestimo["data_devolucao"]
        livro_id = dados_emprestimo["livro_id"]
        usuario_id = current_user_id

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
@jwt_required()
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
        # Obtém o ID do usuário autenticado a partir do JWT
        current_user_id = get_jwt_identity()
        # Busca o usuário autenticado no banco de dados para verificar o papel
        usuario_autenticado = db_session.execute(
            select(Usuario).where(Usuario.id_usuario == current_user_id)
        ).scalars().first()
        if not usuario_autenticado:
            return jsonify({"mensagem": "Usuário não encontrado."}), 404
        # Verifica o papel do usuário
        resultados = []
        if usuario_autenticado.papel == 'admin':
            lista = db_session.execute(select(Emprestimo)).scalars().all()
            for emprestimo in lista:
                resultados.append(emprestimo.serialize())
        else:
            lista = db_session.execute(select(Emprestimo).where(Emprestimo.usuario_id == current_user_id)).scalars().all()
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
@admin_required
@jwt_required()
def put_emprestimo_admin(id_emprestimo):
    with local_session() as db_session:
        try:
            emprestimo = db_session.execute(select(Emprestimo).where(Emprestimo.id_emprestimo == id_emprestimo)).scalar()
            if not emprestimo:
                return jsonify({"mensagem": "Empréstimo não encontrado."}), 404

            dados_emprestimo = request.get_json()
            emprestimo.data_emprestimo = dados_emprestimo['data_emprestimo']
            emprestimo.data_devolucao = dados_emprestimo['data_devolucao']
            emprestimo.livro_id = dados_emprestimo['livro_id']
            emprestimo.usuario_id = dados_emprestimo['usuario_id']

            emprestimo.save(db_session)
            return jsonify({"mensagem": "Empréstimo atualizado com sucesso!"}), 200
        except ValueError:
            return jsonify({"mensagem": "Formato inválido."}), 400
        except TypeError:
            return jsonify({"mensagem": "Faltam informações ou informações incorretas."}), 400
        except Exception as e:
            return jsonify({"mensagem": str(e)}), 500
        finally:
            db_session.close()

@app.route('/emprestimos', methods=['PUT'])
@jwt_required()
def put_emprestimo():
    with local_session() as db_session:
        try:
            # Obtém o ID do usuário autenticado a partir do JWT
            current_user_id = get_jwt_identity()
            # Busca o usuário autenticado no banco de dados para verificar o papel
            usuario_autenticado = db_session.execute(
                select(Usuario).where(Usuario.id_usuario == current_user_id)
            ).scalars().first()
            if not usuario_autenticado:
                return jsonify({"mensagem": "Usuário não encontrado."}), 404

            emprestimo = db_session.execute(select(Emprestimo).where(Emprestimo.id_emprestimo == current_user_id)).scalar()
            if not emprestimo:
                return jsonify({"mensagem": "Empréstimo não encontrado."}), 404

            dados_emprestimo = request.get_json()
            emprestimo.data_emprestimo = dados_emprestimo['data_emprestimo']
            emprestimo.data_devolucao = dados_emprestimo['data_devolucao']
            emprestimo.livro_id = dados_emprestimo['livro_id']
            emprestimo.usuario_id = current_user_id

            emprestimo.save(db_session)
            return jsonify({"mensagem": "Empréstimo atualizado com sucesso!"}), 200
        except ValueError:
            return jsonify({"mensagem": "Formato inválido."}), 400
        except TypeError:
            return jsonify({"mensagem": "Faltam informações ou informações incorretas."}), 400
        except Exception as e:
            return jsonify({"mensagem": str(e)}), 500
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
    app.run(debug=True, host="0.0.0.0", port=5000)