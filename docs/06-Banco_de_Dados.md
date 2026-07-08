# Banco de Dados

O sistema utiliza SQLite em ambiente simples/intranet.

## Tabelas principais

- usuarios
- militares
- posto_graduacao
- companhias
- secoes
- tipo_de_fato
- fatos_observados
- historico_edicao_fo
- dispensas_militares
- auditoria

## Observação sobre pontos

A coluna `pontos` permanece no banco por compatibilidade, mas a regra funcional adotada na v1.5.0 é saldo fixo:

- FO positivo: +1.
- FO negativo: -1.


## Novas tabelas e campos da v1.5.1

### companhias

| Campo | Descrição |
|---|---|
| id | Identificador da companhia |
| nome | Nome completo da companhia |
| sigla | Abreviação ou sigla |
| ativa | Define se a companhia está ativa |

### militares

Novo campo:

| Campo | Descrição |
|---|---|
| id_companhia | Companhia à qual o militar pertence |

### usuarios

Novos campos:

| Campo | Descrição |
|---|---|
| nivel_acesso | BRIGADA, COMPANHIA ou SECAO |
| companhia_id | Companhia de escopo do usuário |
| secao_id | Seção/Pelotão de escopo do usuário |


## Campos adicionados em `usuarios` para primeiro acesso

| Campo | Tipo | Descrição |
|---|---|---|
| primeiro_acesso | Boolean | Indica se o usuário ainda precisa cumprir o fluxo inicial. |
| aceitou_termos | Boolean | Indica se o usuário aceitou os Termos de Uso. |
| data_aceite_termos | DateTime | Data e hora do aceite dos termos. |
