from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base, relationship

engine = create_engine("sqlite:///banco.db")
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


class Livro(Base):
    __tablename__ = 'livros'
    id_livro = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False, index=True)
    autor = Column(String, nullable=False, index=True)
    ISBN = Column(String(13), nullable=False, index=True)
    resumo = Column(String, index=True)

    def __repr__(self):
        return f'<Livro(Título={self.titulo}, id{self.id_livro})>'

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def serialize(self):
        var_livro = {
            'id_livro': self.id_livro,
            'titulo': self.titulo,
            'autor': self.autor,
            'ISBN': self.ISBN,
            'resumo': self.resumo
        }
        return var_livro


class Usuario(Base):
    __tablename__ = 'usuarios'
    id_usuario = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    CPF = Column(String, nullable=False, unique=True)
    endereco = Column(String)

    def __repr__(self):
        return f'<Usuário(nome={self.nome}, id{self.id_usuario})>'

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def serialize(self):
        var_usuario = {
            'id_usuario': self.id_usuario,
            'nome': self.nome,
            'CPF': self.CPF,
            'endereco': self.endereco
        }
        return var_usuario


class Emprestimo(Base):
    __tablename__ = 'emprestimos'
    id_emprestimo = Column(Integer, primary_key=True)
    data_emprestimo = Column(String, nullable=False, index=True)
    data_devolucao = Column(String, nullable=False, index=True)
    livro_id = Column(Integer, ForeignKey('livros.id_livro'))
    livros = relationship('Livro')
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario'))
    usuarios = relationship('Usuario')

    def __repr__(self):
        return f'<Empréstimo(livro={self.livro_id}, usuario{self.usuario_id})>'

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def serialize(self):
        var_emprestimo = {
            'id_emprestimo': self.id_emprestimo,
            'data_emprestimo': self.data_emprestimo,
            'data_devolucao': self.data_devolucao,
            'livro': self.livro_id,
            'usuario': self.usuario_id
        }
        return var_emprestimo

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()