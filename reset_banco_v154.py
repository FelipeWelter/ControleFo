from datetime import date, datetime

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
    Companhia,
    DispensaMilitar,
)

try:
    from app.auth.models import SolicitacaoResetSenha
except Exception:
    SolicitacaoResetSenha = None


app = create_app()


with app.app_context():
    print("Limpando banco...")

    # Remove dados dependentes primeiro
    if SolicitacaoResetSenha is not None:
        SolicitacaoResetSenha.query.delete()

    DispensaMilitar.query.delete()
    Auditoria.query.delete()
    HistoricoEdicaoFO.query.delete()
    FatoObservado.query.delete()
    Usuario.query.delete()
    Militar.query.delete()
    TipoDeFato.query.delete()
    Secao.query.delete()
    PostoGraduacao.query.delete()
    Companhia.query.delete()

    db.session.commit()

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
        db.session.add(PostoGraduacao(nome=nome))

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
        db.session.add(Secao(nome=nome))

    # COMPANHIAS
    companhias = [
        {"nome": "Companhia de Comando", "sigla": "Cia Cmdo"},
        {"nome": "6ª Companhia de Comunicações Mecanizada", "sigla": "6ª Cia Com Mec"},
        {"nome": "23º Pelotão de Policia do Exército", "sigla": "23º Pel PE"},
    ]

    for item in companhias:
        db.session.add(Companhia(**item))

    db.session.commit()

    terceiro_sargento = PostoGraduacao.query.filter_by(nome="3º Sargento").first()
    cia_com_mec = Companhia.query.filter_by(nome="6ª Companhia de Comunicações Mecanizada").first()
    primeiro_pelotao = Secao.query.filter_by(nome="1º Pelotão").first()

    # MILITAR ADMINISTRADOR PADRÃO
    militar_admin = Militar(
        nome_guerra="Ribeiro",
        identidade_militar="1115565978",
        id_posto_graduacao=terceiro_sargento.id,
        data_de_praca=date(2020, 3, 1),
        id_secao=primeiro_pelotao.id,
        id_companhia=cia_com_mec.id if cia_com_mec else None,
        ativo=True,
    )

    db.session.add(militar_admin)
    db.session.flush()

    # USUÁRIO ADMINISTRADOR PADRÃO
    # Login e senha inicial: identidade militar.
    usuario_admin = Usuario(
        username="1115565978",
        senha_hash=generate_password_hash("1115565978"),
        permissoes="USUARIO,LANCADOR,CADASTRADOR,BOLETIM,HOMOLOGADOR,ADMIN",
        militar_id=militar_admin.id,
        nivel_acesso="BRIGADA",
        companhia_id=cia_com_mec.id if cia_com_mec else None,
        secao_id=primeiro_pelotao.id if primeiro_pelotao else None,
        primeiro_acesso=False,
        aceitou_termos=True,
        data_aceite_termos=datetime.utcnow(),
    )

    db.session.add(usuario_admin)

    # Usuário técnico reserva, para manutenção do sistema.
    usuario_tecnico = Usuario(
        username="admin",
        senha_hash=generate_password_hash("frsW2803@"),
        permissoes="ADMIN",
        militar_id=None,
        nivel_acesso="BRIGADA",
        primeiro_acesso=False,
        aceitou_termos=True,
        data_aceite_termos=datetime.utcnow(),
    )

    db.session.add(usuario_tecnico)

    # TIPOS BÁSICOS DE FO
    tipos = [
        {"nome": "Destaque positivo em missão", "sinal": "POSITIVO", "pontos": 1},
        {"nome": "Boa Apresentação Individual", "sinal": "POSITIVO", "pontos": 1},
        {"nome": "Atraso", "sinal": "NEGATIVO", "pontos": 1},
        {"nome": "Falta", "sinal": "NEGATIVO", "pontos": 1},
    ]

    for item in tipos:
        db.session.add(TipoDeFato(**item))

    db.session.commit()

    print("Banco resetado com sucesso.")
    print("Conta principal:")
    print("Login: 1115565978")
    print("Senha: 1115565978")
    print("Nome de guerra: Ribeiro")
    print("Permissões: ADMIN completo")
    print("")
    print("Conta técnica reserva:")
    print("Login: admin")
    print("Senha: frsW2803@")
