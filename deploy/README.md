# Postiz — CMKIA / Contabo

Fork: https://github.com/cmkia/app-postiz

Produção: https://postiz.cmkia.com — servidor Contabo existente, stack `app-postiz`.
Esta pasta adapta a composição oficial para o Docker Swarm e Traefik já instalados.
Não altera o n8n nem usa bancos ou credenciais de clientes existentes.

## Implantação

Arquivos desta pasta em `/opt/app-postiz`, com `.env` privado de modo 600.
Gerar senhas hexadecimais distintas para PostgreSQL/Temporal e um JWT de pelo menos
64 caracteres. Usar imagem oficial Postiz fixada pelo digest `sha256`, obtido após
`docker pull`; a implantação inicial reutiliza a imagem oficial e conserva o código
upstream no fork. Para publicar futuras customizações, construir `Dockerfile.dev`
do commit revisado e substituir `POSTIZ_IMAGE` pela imagem própria com digest.

```sh
cd /opt/app-postiz
# Preencher .env a partir de .env.example, sem imprimir valores em diagnósticos.
sh deploy.sh
docker stack services app-postiz
```

Manter `POSTIZ_PUBLIC_ENABLED=false` até o primeiro administrador estar criado.
Após a API interna ficar saudável, `python3 init-admin.py` cria a conta
`adm@cmkia.com`/organização CMKIA e confere login; a senha aleatória fica somente
em `/opt/app-postiz/admin.private.json` (600). Com o DNS exato configurado para a
Contabo, definir `POSTIZ_PUBLIC_ENABLED=true` e executar `sh deploy.sh` novamente.
O Traefik existente emite o certificado Let's Encrypt.

`DISABLE_REGISTRATION=true` permite apenas a primeira organização vazia, segundo
o comportamento upstream. Após o bootstrap, novos cadastros públicos são recusados.
Convidar colaboradores pelas configurações do aplicativo. Não há provedor de email
configurado nesta implantação; usar links de convite compartilhados manualmente.

Banco Postiz, Redis, PostgreSQL Temporal e Elasticsearch não publicam portas.
Somente a aplicação entra na rede `traefik-proxy`. Não há Temporal UI pública.
Recursos persistem em `/opt/app-postiz/data`; todos os serviços têm política de
reinício e limites de memória/CPU. O host precisa manter a rede externa
`traefik-proxy` e Docker Swarm disponíveis. Arquitetura inicial: nó único.

## Uso com clientes

Entrar com a conta administrativa e conectar os canais de cada cliente pelo OAuth
oficial. Agrupar os canais pelo nome do cliente (Customer groups) e filtrar o
calendário por esse grupo; preparar rascunhos, revisar e só então agendar.
Grupos organizam canais, não constituem isolamento de permissões entre clientes.
Antes de convidar um cliente externo, definir organizações e permissões próprias
e verificar o isolamento. Não misturar tokens ou aprovações da Aloha com outros.

Facebook/Instagram, YouTube e demais canais exigem seus aplicativos de desenvolvedor,
client IDs/secrets e callbacks HTTPS cadastrados. Não basta copiar um token de Ads.
Esses segredos ficam no ambiente privado do serviço; nunca no fork. A implantação
não cria aplicativos OAuth nem conecta/publica em canais existentes automaticamente.
IA e emails também exigem provedores próprios, configurados em etapa específica.

## Verificação, backup e atualização

```sh
docker stack services app-postiz
curl -fsS https://postiz.cmkia.com/api/auth/can-register
# Após bootstrap: {"register":false}
sh backup.sh
```

`backup.sh` produz dump Postiz, dump PostgreSQL Temporal, uploads/config e ambiente
privado em `/opt/app-postiz/backups/<UTC>`. Backup contém segredos e deve permanecer
privado. Não há cópia externa ou recorrência configurada. Dumps capturam os bancos
separadamente; para uma restauração coerente de uma instância com posts agendados,
pausar o serviço app antes do backup/restauro, preservando a agenda e conferindo
os workflows Temporal. Elasticsearch é índice derivado e não integra este backup.

Antes de atualizar: backup, ler notas da versão, fixar novo digest, executar
`deploy.sh` e conferir login/calendário/Temporal. Não usar `docker stack rm`,
`docker compose down -v`, reset Prisma ou limpeza de volumes para atualizar.
Voltar ao digest anterior só é seguro quando o schema do banco for compatível;
caso contrário restaurar o conjunto completo de backup e validar a agenda.

Fontes: [instalação oficial](https://docs.postiz.com/self-host/installation/docker-compose),
[composição canônica](https://github.com/gitroomhq/postiz-docker-compose),
[código upstream](https://github.com/gitroomhq/postiz-app). Consultadas em 2026-10-21.
