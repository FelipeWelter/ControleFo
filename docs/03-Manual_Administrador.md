# Manual do Administrador

## Perfis de permissão

- ADMIN: administração geral do sistema.
- CADASTRADOR: cadastro e manutenção de militares.
- LANCADOR: lançamento de FO.
- HOMOLOGADOR: homologação de FO.
- BOLETIM: exportação para boletim.
- USUARIO: consulta pessoal, quando autorizado.

## Regras importantes

- A exclusão de usuários está desativada.
- Reset de senha define a senha como a identidade militar vinculada.
- Militares com posto/graduação Cabo ou Soldado não acessam o sistema.
- Ranking, Histórico Geral e Dispensas são restritos a oficiais, Aspirante-a-Oficial ou superior, além do ADMIN.


## Companhias

A partir da v1.5.1, o sistema permite cadastrar companhias para uso por mais de uma subunidade/companhia dentro da Brigada.

Caminho:

```text
Menu > Companhias
```

Campos:

- Nome da companhia.
- Sigla.
- Situação ativa/inativa.

Após cadastrar a companhia, vincule os militares à companhia no cadastro de militares.

## Nível de acesso territorial

Na criação ou edição de usuário, além das permissões funcionais, existe o nível de acesso territorial:

- **Brigada/Geral:** visualiza e gerencia dados de todas as companhias.
- **Companhia:** visualiza e gerencia apenas militares vinculados à companhia definida.
- **Seção/Pelotão:** visualiza e gerencia apenas militares vinculados à seção/pelotão definido.

Esse nível afeta as telas de:

- Novo FO.
- Homologação.
- Ranking.
- Histórico Geral.
- Dispensas.
- Militares.
- Página Inicial.
- Exportação BI.


## Primeiro acesso e reset de senha

Ao cadastrar um novo usuário, o sistema considera o acesso como inicial. O usuário deverá alterar a senha e aceitar os Termos de Uso antes de acessar as funcionalidades.

Quando o administrador resetar a senha de um usuário, a senha volta a ser a identidade militar vinculada e o sistema exigirá novamente a troca de senha e o aceite dos termos.

## Exportação BI

A tela de Exportação BI é restrita a usuários com a permissão BOLETIM. A listagem de FOs publicados é limitada à companhia vinculada ao usuário responsável pelo boletim.

## Seções especiais

A partir da v1.5.3, o cadastro de seções/pelotões inclui:

- Comandante.
- Subcomandante.

Essas seções servem para vincular o comandante e o subcomandante da companhia/unidade, permitindo cadastro e acesso administrativo sem exibição de histórico pessoal.

## Administrador

Usuários com perfil ADMIN possuem acesso total ao sistema e visualizam todos os dados, independentemente da companhia, seção ou pelotão.
