# Sistema FO - v1.5.1

Sistema web em Flask para controle de Fatos Observados.

## Funcionalidades

- Login com senha criptografada
- Bloqueio de acesso para militares Cabo e Soldado
- Permissões múltiplas por usuário
- Cadastro de militares
- Ativação e inativação de militares
- Lançamento de FO
- Homologação
- Ranking restrito a oficiais
- Histórico individual
- Histórico geral de FO por militar, com data do fato, restrito a oficiais
- Controle de dispensas de militares, restrito a oficiais
- Cadastro de companhias
- Nível de acesso por Brigada/Geral, Companhia ou Seção/Pelotão
- Rodapé com direitos autorais
- Exportação para boletim restrita ao perfil BOLETIM
- Auditoria administrativa
- Dashboard operacional
- Tratamento amigável de erros

## Permissões

- USUARIO
- LANCADOR
- CADASTRADOR
- BOLETIM
- HOMOLOGADOR
- ADMIN

## Regras de acesso por posto/graduação

- Cabo e Soldado não acessam o sistema.
- Histórico Geral, Dispensas e Ranking são áreas restritas a oficiais, de Aspirante-a-Oficial para cima.
- O perfil ADMIN mantém acesso administrativo para manutenção do sistema.

## Banco

O banco SQLite `database.db` não deve ser versionado no GitHub.

## Execução com Docker Compose

Crie o arquivo local de configuração e defina uma `SECRET_KEY` forte:

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Edite o valor de `SECRET_KEY` no arquivo `.env` e suba a aplicação:

```bash
docker compose up -d --build
```

As migrações são aplicadas automaticamente na inicialização. No primeiro uso,
carregue os dados iniciais e acesse `http://localhost:5000`:

```bash
docker compose exec app python seed.py
```

O banco SQLite fica armazenado no volume nomeado `controlefo_data`, permanecendo
disponível mesmo quando o contêiner é recriado. Para acompanhar a aplicação ou
encerrá-la, use:

```bash
docker compose logs -f app
docker compose down
```

## Publicação

Atualizar servidor:

```bash
cd ~/ControleFo
sudo systemctl stop sistemafo
git fetch origin
git reset --hard origin/main
source venv/bin/activate
pip install -r requirements.txt
flask --app run.py db upgrade
sudo systemctl start sistemafo
```
