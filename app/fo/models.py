from datetime import datetime
from app.extensions import db

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
    evidencias = db.relationship("EvidenciaFO", backref="fato", lazy=True)

    def __repr__(self):
        return f"<FO {self.id} - {self.sinal} - {self.status}>"

class EvidenciaFO(db.Model):
    __tablename__ = "evidencias_fo"

    id = db.Column(db.Integer, primary_key=True)

    fato_id = db.Column(
        db.Integer,
        db.ForeignKey("fatos_observados.id", ondelete="RESTRICT"),
        nullable=False
    )

    nome_original = db.Column(db.String(255), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    caminho = db.Column(db.String(500), nullable=False)
    tipo_mime = db.Column(db.String(100), nullable=False)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

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