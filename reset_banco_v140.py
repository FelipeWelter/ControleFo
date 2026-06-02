from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.fo.models import (
    Usuario,
    Militar,
    Secao,
    PostoGraduacao,
    TipoDeFato,
    FatoObservado,
    HistoricoEdicaoFO,
    Auditoria,
)

app = create_app()

with app.app_context():
    print("Limpando banco...")

    Auditoria.query.delete()
    HistoricoEdicaoFO.query.delete()
    FatoObservado.query.delete()
    Usuario.query.delete()
    Militar.query.delete()
    TipoDeFato.query.delete()
    Secao.query.delete()
    PostoGraduacao.query.delete()

    db.session.commit()

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
        db.session.add(PostoGraduacao(nome=nome))

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
        db.session.add(Secao(nome=nome))

    db.session.commit()

    admin = Usuario(
        username="admin",
        senha_hash=generate_password_hash("admin"),
        permissoes="ADMIN",
        militar_id=None,
    )

    db.session.add(admin)
    db.session.commit()

    print("Banco resetado com sucesso.")
    print("Login: admin")
    print("Senha: admin")