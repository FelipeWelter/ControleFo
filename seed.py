from datetime import date

from app import create_app
from app.extensions import db

from werkzeug.security import generate_password_hash

from app.fo.models import (
    Usuario,
    Militar,
    Secao,
    PostoGraduacao,
    TipoDeFato,
)

app = create_app()

with app.app_context():
    # POSTOS

    postos = [
        "Coronel",
        "Tenente-Coronel",
        "Major",
        "Capitão",
        "1º Tenente",
        "2º Tenente",
        "Aspirante-a-Oficial",
        "Subtenente",
        "1º Sargento",
        "2º Sargento",
        "3º Sargento",
        "Aluno CFST",
        "Cabo",
        "Aluno CFC",
        "Soldado",
    ]

    for nome in postos:
        existente = PostoGraduacao.query.filter_by(nome=nome).first()

        if not existente:
            db.session.add(PostoGraduacao(nome=nome))

    db.session.commit()

    # SEÇÕES

    secoes = [
        "1ª Seção",
        "2ª Seção",
        "3ª Seção",
        "4ª Seção",
        "1º Pelotão",
        "2º Pelotão",
        "Subtenência",
        "Relações Públicas",
    ]

    for nome in secoes:
        existente = Secao.query.filter_by(nome=nome).first()

        if not existente:
            db.session.add(Secao(nome=nome))

    db.session.commit()

    # BUSCAS

    sargento = PostoGraduacao.query.filter_by(nome="3º Sargento").first()
    soldado = PostoGraduacao.query.filter_by(nome="Soldado").first()
    quarta_secao = Secao.query.filter_by(nome="4ª Seção").first()

    # MILITARES
    militar1 = Militar.query.filter_by(
        identidade_militar="123456"
    ).first()

    if not militar1:
        militar1 = Militar(
            nome_guerra="Teste",
            identidade_militar="123456",
            id_posto_graduacao=sargento.id,
            data_de_praca=date(2020, 3, 1),
            id_secao=quarta_secao.id,
        )

        db.session.add(militar1)

    militar2 = Militar.query.filter_by(
        identidade_militar="654321"
    ).first()

    if not militar2:
        militar2 = Militar(
            nome_guerra="Teste2",
            identidade_militar="654321",
            id_posto_graduacao=soldado.id,
            data_de_praca=date(2021, 5, 15),
            id_secao=quarta_secao.id,
        )

        db.session.add(militar2)

    db.session.commit()

    # USUÁRIO

    usuario = Usuario.query.filter_by(username="admin").first()
    if not usuario:
        usuario = Usuario(
            username="admin",
            senha_hash=generate_password_hash("admin"),
            perfil="ADMIN",
            militar_id=militar1.id,
        )

        db.session.add(usuario)

    # TIPOS DE FATO
    tipos = [
        {
            "nome": "Destaque positivo em missão",
            "sinal": "POSITIVO",
            "pontos": 10,
        },

        {
            "nome": "Boa Apresentação Individual",
            "sinal": "POSITIVO",
            "pontos": 5,
        },
        {
            "nome": "Atraso",
            "sinal": "NEGATIVO",
            "pontos": 10,
        },

        {
            "nome": "Falta",
            "sinal": "NEGATIVO",
            "pontos": 20,
        },
    ]

    for item in tipos:
        existente = TipoDeFato.query.filter_by(
            nome=item["nome"],
        ).first()

        if not existente:
            db.session.add(TipoDeFato(**item))

    db.session.commit()

    print("Dados de teste inseridos com sucesso!")

