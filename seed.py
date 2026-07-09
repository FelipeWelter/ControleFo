from datetime import date, datetime

from app import create_app
from app.extensions import db

from werkzeug.security import generate_password_hash

from app.fo.models import (
    Usuario,
    Militar,
    Secao,
    PostoGraduacao,
    TipoDeFato,
    Companhia,
)

app = create_app()

with app.app_context():
    # POSTOS / GRADUAÇÕES
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
        if not PostoGraduacao.query.filter_by(nome=nome).first():
            db.session.add(PostoGraduacao(nome=nome))

    db.session.commit()

    # SEÇÕES / PELOTÕES
    secoes = [
        "Comandante",
        "Subcomandante",
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
        if not Secao.query.filter_by(nome=nome).first():
            db.session.add(Secao(nome=nome))

    db.session.commit()

    # COMPANHIAS
    companhias = [
        {"nome": "Companhia de Comando", "sigla": "Cia Cmdo"},
        {"nome": "1ª Companhia", "sigla": "1ª Cia"},
        {"nome": "2ª Companhia", "sigla": "2ª Cia"},
    ]

    for item in companhias:
        existente = Companhia.query.filter_by(nome=item["nome"]).first()
        if not existente:
            db.session.add(Companhia(**item))

    db.session.commit()

    terceiro_sargento = PostoGraduacao.query.filter_by(nome="3º Sargento").first()
    soldado = PostoGraduacao.query.filter_by(nome="Soldado").first()
    quarta_secao = Secao.query.filter_by(nome="4ª Seção").first()
    cia_cmdo = Companhia.query.filter_by(nome="Companhia de Comando").first()

    # MILITAR ADMINISTRADOR PADRÃO
    militar_admin = Militar.query.filter_by(identidade_militar="1115565978").first()
    if not militar_admin:
        militar_admin = Militar(
            nome_guerra="Ribeiro",
            identidade_militar="1115565978",
            id_posto_graduacao=terceiro_sargento.id,
            data_de_praca=date(2020, 3, 20),
            id_secao=quarta_secao.id,
            id_companhia=cia_cmdo.id if cia_cmdo else None,
            ativo=True,
        )
        db.session.add(militar_admin)
        db.session.flush()
    else:
        militar_admin.nome_guerra = "Ribeiro"
        militar_admin.id_posto_graduacao = terceiro_sargento.id
        militar_admin.data_de_praca = date(2020, 3, 20)
        militar_admin.id_secao = quarta_secao.id
        militar_admin.id_companhia = cia_cmdo.id if cia_cmdo else None
        militar_admin.ativo = True

    # Usuário administrador principal
    usuario_admin = Usuario.query.filter_by(username="1115565978").first()
    if not usuario_admin:
        usuario_admin = Usuario(
            username="1115565978",
            senha_hash=generate_password_hash("1115565978"),
            permissoes="USUARIO,LANCADOR,CADASTRADOR,BOLETIM,HOMOLOGADOR,ADMIN",
            militar_id=militar_admin.id,
            nivel_acesso="BRIGADA",
            companhia_id=cia_cmdo.id if cia_cmdo else None,
            secao_id=quarta_secao.id if quarta_secao else None,
            primeiro_acesso=False,
            aceitou_termos=True,
            data_aceite_termos=datetime.utcnow(),
        )
        db.session.add(usuario_admin)
    else:
        usuario_admin.permissoes = "USUARIO,LANCADOR,CADASTRADOR,BOLETIM,HOMOLOGADOR,ADMIN"
        usuario_admin.militar_id = militar_admin.id
        usuario_admin.nivel_acesso = "BRIGADA"
        usuario_admin.companhia_id = cia_cmdo.id if cia_cmdo else None
        usuario_admin.secao_id = quarta_secao.id if quarta_secao else None
        usuario_admin.primeiro_acesso = False
        usuario_admin.aceitou_termos = True
        usuario_admin.data_aceite_termos = usuario_admin.data_aceite_termos or datetime.utcnow()

    # Conta técnica reserva
    tecnico = Usuario.query.filter_by(username="admin").first()
    if not tecnico:
        tecnico = Usuario(
            username="admin",
            senha_hash=generate_password_hash("admin"),
            permissoes="ADMIN",
            militar_id=None,
            nivel_acesso="BRIGADA",
            primeiro_acesso=False,
            aceitou_termos=True,
            data_aceite_termos=datetime.utcnow(),
        )
        db.session.add(tecnico)
    else:
        tecnico.permissoes = "ADMIN"
        tecnico.primeiro_acesso = False
        tecnico.aceitou_termos = True
        tecnico.data_aceite_termos = tecnico.data_aceite_termos or datetime.utcnow()

    # Militar de teste soldado (sem acesso ao sistema)
    militar_teste = Militar.query.filter_by(identidade_militar="654321").first()
    if not militar_teste and soldado:
        militar_teste = Militar(
            nome_guerra="Teste2",
            identidade_militar="654321",
            id_posto_graduacao=soldado.id,
            data_de_praca=date(2021, 5, 15),
            id_secao=quarta_secao.id,
            id_companhia=cia_cmdo.id if cia_cmdo else None,
            ativo=True,
        )
        db.session.add(militar_teste)

    db.session.commit()

    # TIPOS DE FO
    tipos = [
        {"nome": "Destaque positivo em missão", "sinal": "POSITIVO", "pontos": 1},
        {"nome": "Boa Apresentação Individual", "sinal": "POSITIVO", "pontos": 1},
        {"nome": "Atraso", "sinal": "NEGATIVO", "pontos": 1},
        {"nome": "Falta", "sinal": "NEGATIVO", "pontos": 1},
    ]

    for item in tipos:
        existente = TipoDeFato.query.filter_by(nome=item["nome"]).first()
        if not existente:
            db.session.add(TipoDeFato(**item))

    db.session.commit()

    print("Dados iniciais inseridos/atualizados com sucesso!")
    print("Administrador principal:")
    print("Login: 1115565978")
    print("Senha inicial: 1115565978")
    print("Conta técnica reserva: admin / admin")
