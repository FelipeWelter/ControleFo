# Sistema FO - v1.4.1

Sistema web em Flask para controle de Fatos Observados.

## Funcionalidades

- Login com senha criptografada
- Permissões múltiplas por usuário
- Cadastro de militares
- Ativação e inativação de militares
- Lançamento de FO
- Homologação
- Ranking
- Histórico individual
- Exportação para boletim
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

## Banco

O banco SQLite `database.db` não deve ser versionado no GitHub.

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