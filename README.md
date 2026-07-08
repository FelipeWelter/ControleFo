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
