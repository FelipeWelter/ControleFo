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