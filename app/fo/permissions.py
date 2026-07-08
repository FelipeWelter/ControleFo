from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user


def obter_permissoes(usuario):
    if not usuario or not getattr(usuario, "permissoes", None):
        return []

    return [
        permissao.strip()
        for permissao in usuario.permissoes.split(",")
        if permissao.strip()
    ]


def tem_permissao(usuario, *permissoes_exigidas):
    permissoes_usuario = obter_permissoes(usuario)

    if "ADMIN" in permissoes_usuario:
        return True

    return any(
        permissao in permissoes_usuario
        for permissao in permissoes_exigidas
    )


def nome_posto(usuario):
    militar = getattr(usuario, "militar", None)
    posto = getattr(militar, "posto_graduacao", None) if militar else None
    return (getattr(posto, "nome", "") or "").strip().upper()


def militar_bloqueado_por_posto(usuario):
    nome = nome_posto(usuario)
    return nome in {"CABO", "SOLDADO"}


def eh_oficial(usuario):
    nome = nome_posto(usuario)
    postos_oficiais = {
        "CORONEL",
        "TENENTE-CORONEL",
        "TENENTE CORONEL",
        "MAJOR",
        "CAPITÃO",
        "CAPITAO",
        "1º TENENTE",
        "1° TENENTE",
        "PRIMEIRO TENENTE",
        "2º TENENTE",
        "2° TENENTE",
        "SEGUNDO TENENTE",
        "ASPIRANTE-A-OFICIAL",
        "ASPIRANTE A OFICIAL",
        "ASPIRANTE",
    }
    return nome in postos_oficiais


def tem_acesso_oficial(usuario):
    return eh_oficial(usuario) or tem_permissao(usuario, "ADMIN")


def secao_comando_superior(usuario):
    militar = getattr(usuario, "militar", None)
    secao = getattr(militar, "secao", None) if militar else None
    nome = (getattr(secao, "nome", "") or "").strip().upper()
    return nome in {"COMANDANTE", "SUBCOMANDANTE"}


def usuario_tem_historico_pessoal(usuario):
    return bool(getattr(usuario, "militar_id", None)) and not secao_comando_superior(usuario)



def usuario_eh_admin(usuario):
    return "ADMIN" in obter_permissoes(usuario)


def nivel_acesso_usuario(usuario):
    if usuario_eh_admin(usuario):
        return "BRIGADA"

    nivel = (getattr(usuario, "nivel_acesso", None) or "SECAO").upper()
    if nivel not in {"BRIGADA", "COMPANHIA", "SECAO"}:
        return "SECAO"
    return nivel


def companhia_escopo_id(usuario):
    if getattr(usuario, "companhia_id", None):
        return usuario.companhia_id

    militar = getattr(usuario, "militar", None)
    return getattr(militar, "id_companhia", None) if militar else None


def secao_escopo_id(usuario):
    if getattr(usuario, "secao_id", None):
        return usuario.secao_id

    militar = getattr(usuario, "militar", None)
    return getattr(militar, "id_secao", None) if militar else None


def militar_no_escopo(usuario, militar):
    """Valida se o militar consultado/gerenciado está dentro do escopo do usuário."""
    if usuario_eh_admin(usuario):
        return True

    if not militar:
        return False

    nivel = nivel_acesso_usuario(usuario)

    if nivel == "BRIGADA":
        return True

    if nivel == "COMPANHIA":
        companhia_id = companhia_escopo_id(usuario)
        return companhia_id is not None and militar.id_companhia == companhia_id

    if nivel == "SECAO":
        secao_id = secao_escopo_id(usuario)
        return secao_id is not None and militar.id_secao == secao_id

    return False


def aplicar_escopo_militares(query, usuario, modelo_militar):
    """Aplica filtro de escopo em queries que possuem a entidade Militar."""
    if usuario_eh_admin(usuario):
        return query

    nivel = nivel_acesso_usuario(usuario)

    if nivel == "BRIGADA":
        return query

    if nivel == "COMPANHIA":
        companhia_id = companhia_escopo_id(usuario)
        if companhia_id is None:
            return query.filter(False)
        return query.filter(modelo_militar.id_companhia == companhia_id)

    if nivel == "SECAO":
        secao_id = secao_escopo_id(usuario)
        if secao_id is None:
            return query.filter(False)
        return query.filter(modelo_militar.id_secao == secao_id)

    return query.filter(False)


def permissao_requerida(*permissoes):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Faça login para acessar o sistema.", "warning")
                return redirect(url_for("auth.login"))

            if not tem_permissao(current_user, *permissoes):
                flash("Você não possui permissão para acessar esta área.", "danger")

                if request.referrer:
                    return redirect(request.referrer)

                return redirect(url_for("index"))

            return func(*args, **kwargs)

        return wrapper

    return decorator


def oficial_requerido(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Faça login para acessar o sistema.", "warning")
            return redirect(url_for("auth.login"))

        if not tem_acesso_oficial(current_user):
            flash("Área restrita a oficiais: Aspirante-a-Oficial ou posto superior.", "danger")

            if request.referrer:
                return redirect(request.referrer)

            return redirect(url_for("index"))

        return func(*args, **kwargs)

    return wrapper


def requer_admin(func):
    return permissao_requerida("ADMIN")(func)


def requer_homologador(func):
    return permissao_requerida("HOMOLOGADOR")(func)


def requer_boletim(func):
    return permissao_requerida("BOLETIM")(func)


def requer_cadastrador(func):
    return permissao_requerida("CADASTRADOR")(func)


def requer_lancador(func):
    return permissao_requerida("LANCADOR", "HOMOLOGADOR")(func)


def pode_lancar_fo_para(cadastrador, militar_alvo):
    if not hasattr(cadastrador, "militar"):
        return False

    militar_cadastrador = cadastrador.militar

    if not militar_cadastrador:
        return False

    return militar_alvo.id_posto_graduacao > militar_cadastrador.id_posto_graduacao
