# Manual do Desenvolvedor

## Estrutura básica

```text
ControleFo/
├── app/
│   ├── auth/
│   ├── fo/
│   ├── templates/
│   └── extensions.py
├── migrations/
├── docs/
├── config.py
├── run.py
├── seed.py
└── requirements.txt
```

## Rodar em ambiente de desenvolvimento

```bash
source venv/bin/activate
flask --app run.py run --debug
```

## Migrações

Criar migration:

```bash
flask --app run.py db migrate -m "descricao da alteracao"
```

Aplicar migration:

```bash
flask --app run.py db upgrade
```

## Regra de saldo

Mesmo mantendo a coluna `pontos` por compatibilidade com o banco, a interface e os relatórios usam contagem de FOs:

- positivo = +1;
- negativo = -1.
