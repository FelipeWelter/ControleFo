from app import create_app
from app.extensions import db
from app.fo.models import Militar, Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():

    criados = 0

    militares = Militar.query.all()

    for militar in militares:
        usuario = Usuario.query.filter_by(
            militar_id=militar.id
        ).first()

        if usuario:
            continue

        usuario = Usuario(
            username=militar.identidade_militar,
            senha_hash=generate_password_hash(militar.identidade_militar),
            perfil="MILITAR",
            militar_id=militar.id
        )

        db.session.add(usuario)
        criados += 1

    db.session.commit()

    print(f"Usuários criados: {criados}")