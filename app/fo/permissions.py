from functools import wraps
from flask import abort
from flask_login import current_user

def requer_homologador(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)  # Unauthorized

        if getattr(current_user, "nivel_permissao", 0) < 2:  # Nível de permissão 2 ou superior é necessário
            abort(403)  # Forbidden

        return func(*args, **kwargs)

    return wrapper

def pode_lancar_fo_para(cadastrador, militar_alvo):
    """
    Regra:
    Militar pode lançar FO para outro militar se o militar for seu subordinado:
    Quanto menor o id_posto_graduacao, mais antigo/superior é o militar. 
    Exemplo:
    1 = Capitão
    2 = Tenente
    3 = Sargento
    """

    if not hasattr(cadastrador, "militar"):
        return False

    militar_cadastrador = cadastrador.militar

    if not militar_cadastrador:
        return False

    return militar_alvo.id_posto_graduacao > militar_cadastrador.id_posto_graduacao
    
