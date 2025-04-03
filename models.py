from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

engine = create_engine("sqlite:///Revisa.db")
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class Tarefa(Base):
    __tablename__ = 'tarefa'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    descricao = Column(String)

def __repr__(self):
    return f'<Tarefa(nome={self.nome}>'

def save(self):
    db_session.add(self)
    db_session.commit()

def delete(self):
    db_session.delete(self)
    db_session.commit()

def serialize(self):
    var_tarefa = {
        'id': self.id,
        'nome': self.nome,
        'descricao': self.descricao
    }
    return var_tarefa

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()