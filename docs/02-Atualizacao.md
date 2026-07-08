# Atualização do Sistema

## Atualizar código pelo Git

```bash
cd ControleFo
git pull
source venv/bin/activate
pip install -r requirements.txt
flask --app run.py db upgrade
```

Depois reinicie o serviço usado no servidor.

## Teste local após atualização

```bash
flask --app run.py run --host=0.0.0.0 --port=5000
```
