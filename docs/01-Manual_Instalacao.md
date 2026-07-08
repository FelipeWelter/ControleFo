# Manual de Instalação — Sistema FO

## 1. Pré-requisitos

Ambiente recomendado:

- Ubuntu Server ou WSL Ubuntu.
- Python 3.
- Git.
- Acesso ao repositório do projeto.

Instale os pacotes básicos:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

## 2. Clonar o projeto

```bash
git clone https://github.com/FelipeWelter/ControleFo.git
cd ControleFo
```

## 3. Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

Confirme se o Python está usando o ambiente virtual:

```bash
which python
```

O resultado deve apontar para a pasta `venv`.

## 4. Instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Aplicar banco de dados

```bash
flask --app run.py db upgrade
```

## 6. Popular dados iniciais

```bash
python seed.py
```

Usuário inicial esperado:

- Usuário: `admin`
- Senha: `admin`

## 7. Rodar o sistema para teste

```bash
python run.py
```

ou:

```bash
flask --app run.py run --host=0.0.0.0 --port=5000
```

Acesse no navegador:

```text
http://127.0.0.1:5000
```

## 8. Problemas comuns

### Erro: No module named flask

Ative o ambiente virtual e reinstale os requisitos:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Login admin não funciona

Execute o script de população ou reset do banco:

```bash
python seed.py
```

ou:

```bash
python reset_banco_v140.py
```
