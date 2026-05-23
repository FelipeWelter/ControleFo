from datetime import datetime
from app.extensions import db
from flask_login import UserMixin

class PostoGraduacao(db.Model):
    __tablename__ = 'posto_graduacao'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)

class Secao(db.Model):
    __tablename__ = 'secoes'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)

class Militar(db.Model):
    __tablename__ = "militares"

    id = db.Column(db.Integer, primary_key=True)
    nome_guerra = db.Column(db.String(120), nullable=False)
    identidade_militar = db.Column(db.String(30), unique=True, nullable=False)

    id_posto_graduacao = db.Column(
        db.Integer,
        db.ForeignKey("posto_graduacao.id", ondelete="RESTRICT"),
        nullable=False
    )

    data_de_praca = db.Column(db.Date, nullable=False)
    id_secao = db.Column(
        db.Integer,
        db.ForeignKey("secoes.id", ondelete="RESTRICT"),
        nullable=False
    )

    foto_url = db.Column(db.String(255), nullable=True)

    posto_graduacao = db.relationship("PostoGraduacao")
    secao = db.relationship("Secao")

class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)

    ######### A implementação de níveis de permissão pode ser feita de várias formas, dependendo das necessidades do sistema. Uma abordagem comum é usar um campo de enumeração ou um campo de string para representar o nível de permissão do usuário.
    # 
    # nivel_permissao = db.Column(db.Integer, default=1, nullable=False) # "Cadastrador", "Homologador", "Administrador"
##################################

    perfil = db.Column(
        db.String(20),
        nullable=False,
        default="MILITAR"
    )
    
    militar_id = db.Column(
        db.Integer,
        db.ForeignKey("militares.id", ondelete="RESTRICT"),
        nullable=False
    )

    militar = db.relationship("Militar")

class TipoDeFato(db.Model):
    __tablename__ = 'tipo_de_fato'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    sinal = db.Column(db.String(10), nullable=False) #positivo ou negativo
    pontos = db.Column(db.Integer, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<TipoDeFato {self.nome} ({self.pontos})>"

class FatoObservado(db.Model):
    __tablename__ = "fatos_observados"

    id = db.Column(db.Integer, primary_key=True)

    militar_id = db.Column(
        db.Integer,
        db.ForeignKey("militares.id", ondelete="RESTRICT"),
        nullable=False
    )

    cadastrador_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False
    )

    homologador_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=True
    )

    tipo_de_fato_id = db.Column(
        db.Integer,
        db.ForeignKey("tipo_de_fato.id", ondelete="RESTRICT"),
        nullable=False
    )

    sinal = db.Column(db.String(10), nullable=False) #positivo ou negativo
    pontos = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(20), default="Pendente", nullable=False)
    justificativa_recusa = db.Column(db.Text, nullable=True)

    data_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_homologacao = db.Column(db.DateTime, nullable=True)

    militar = db.relationship("Militar", foreign_keys=[militar_id])
    cadastrador = db.relationship("Usuario", foreign_keys=[cadastrador_id])
    homologador = db.relationship("Usuario", foreign_keys=[homologador_id])
    tipo_fato = db.relationship("TipoDeFato")

    def __repr__(self):
        return f"<FO {self.id} - {self.sinal} - {self.status}>"

class HistoricoEdicaoFO(db.Model):
    __tablename__ = "historico_edicao_fo"

    id = db.Column(db.Integer, primary_key=True)

    fato_id = db.Column(
        db.Integer,
        db.ForeignKey("fatos_observados.id", ondelete="RESTRICT"),
        nullable=False
    )

    editor_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False
    )

    descricao_antiga = db.Column(db.Text, nullable=True)
    descricao_nova = db.Column(db.Text, nullable=True)
    data_edicao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    fato = db.relationship("FatoObservado")
    editor = db.relationship("Usuario")
