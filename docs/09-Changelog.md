# Changelog — Sistema FO

## v1.5.0 — Grande Atualização

### Adicionado

- Documentação inicial do projeto na pasta `docs`.
- Histórico Geral de FO para oficiais.
- Controle de Dispensas para oficiais.

### Alterado

- Ranking restrito a oficiais.
- Exportação BI restrita ao perfil BOLETIM.
- Pontuação visual substituída por saldo simples de FO.
- FO positivo passa a representar +1.
- FO negativo passa a representar -1.
- Tela de lançamento não exibe mais campo de pontuação.
- Telas de histórico, ranking, dashboard e exportação deixam de exibir pontos brutos.

### Segurança e permissões

- Cabo e Soldado não acessam o sistema.
- Exclusão de usuário permanece desativada.


## v1.5.1 — Companhias e Escopo de Acesso

### Adicionado

- Cadastro de companhias.
- Vinculação de militares a companhias.
- Nível de acesso territorial no cadastro de usuários:
  - Brigada/Geral.
  - Companhia.
  - Seção/Pelotão.
- Filtros por companhia nas telas gerenciais.
- Copyright no rodapé do sistema.

### Alterado

- Homologação passa a respeitar o escopo territorial do usuário.
- Histórico Geral passa a respeitar o escopo territorial do usuário.
- Ranking passa a respeitar o escopo territorial do usuário.
- Dispensas passam a respeitar o escopo territorial do usuário.
- Cadastro/listagem de militares passa a respeitar o escopo territorial do usuário.
- Exportação BI passa a respeitar o escopo territorial do usuário.


## v1.5.2 — Primeiro Acesso, Termos e Ajustes de Interface

### Adicionado
- Obrigatoriedade de alteração de senha no primeiro acesso.
- Aceite obrigatório dos Termos de Uso do Sistema FO.
- Registro da data/hora do aceite dos termos no cadastro do usuário.
- Termos de Uso gerados em tela própria.
- Direitos autorais exibidos também na tela de login.

### Alterado
- Texto de copyright padronizado para: © 2026 Desenvolvido por 3º Sgt Ribeiro. Todos os direitos reservados.
- Nome "Dashboard" alterado para "Página Inicial".
- Nome "Ranking Geral da Tropa" alterado para "Painel de Conceitos da Tropa".
- Removido o aviso de cálculo automático de saldo da tela de Novo FO.
- Exportação BI agora exige permissão BOLETIM explicitamente e lista somente militares da companhia do usuário responsável pelo boletim.

### Segurança
- Reset de senha volta a marcar o usuário como primeiro acesso, exigindo nova senha e novo aceite dos termos.

## v1.5.3 — Ajustes de Acesso, Comando e Perfis

### Adicionado
- Seções/Pelotões especiais: Comandante e Subcomandante.
- Exibição dos perfis atribuídos com ícones na Página Inicial.
- Ícones nos perfis atribuídos no cadastro de usuários.

### Alterado
- Usuário ADMIN passa a visualizar todos os registros, independente de companhia ou seção.
- Primeiro acesso agora solicita a identidade militar em vez da senha atual.
- Menu "Novo FO" alterado para "Lançar FO".
- Seções Comandante e Subcomandante não exibem histórico pessoal.
- Exportação BI mantém restrição ao perfil BOLETIM, respeitando companhia para usuários não administradores.
