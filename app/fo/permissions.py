from functools import wraps
from flask import abort
from flask_login import current_user


def perfil_permitido(*perfis):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)

            if current_user.perfil not in perfis and current_user.perfil != "ADMIN":
                abort(403)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def requer_admin(func):
    return perfil_permitido("ADMIN")(func)


def requer_homologador(func):
    return perfil_permitido("HOMOLOGADOR")(func)


def requer_boletim(func):
    return perfil_permitido("BOLETIM")(func)


def requer_cadastrador(func):
    return perfil_permitido("CADASTRADOR")(func)


def pode_lancar_fo_para(cadastrador, militar_alvo):
    if not hasattr(cadastrador, "militar"):
        return False

    militar_cadastrador = cadastrador.militar

    if not militar_cadastrador:
        return False

    return militar_alvo.id_posto_graduacao > militar_cadastrador.id_posto_graduacao