from flask import Blueprint

fo_bp = Blueprint(
    "fo",
    __name__,
    template_folder="../templates/fo",
    url_prefix="/fo"
)

from . import routes
