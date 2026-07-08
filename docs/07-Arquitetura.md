# Arquitetura do Sistema

Fluxo simplificado:

```text
Usuário
  ↓
Login
  ↓
Permissões
  ↓
Rotas Flask / Blueprints
  ↓
Serviços de negócio
  ↓
Modelos SQLAlchemy
  ↓
Banco SQLite
```

## Camadas

- Autenticação: `app/auth`.
- Regras e permissões: `app/fo/permissions.py`.
- Rotas funcionais: `app/fo/routes.py`.
- Serviços: `app/fo/services.py`.
- Modelos: `app/fo/models.py`.
- Templates: `app/templates`.
