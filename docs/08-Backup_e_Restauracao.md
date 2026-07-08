# Backup e Restauração

## Backup simples do banco

```bash
mkdir -p backup
cp database.db backup/database_$(date +%F_%H-%M).db
```

## Restaurar backup

Pare o sistema antes de restaurar.

```bash
cp backup/NOME_DO_BACKUP.db database.db
```

Depois reinicie o sistema.
