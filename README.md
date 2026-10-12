# VG Discord Bot

Bot em Python para o servidor **Esgoto do Ratão**, desenvolvido por baieu666.

Esta versão registra a base atual do projeto antes da separação em módulos. O código principal está em `bot.py`.

## Recursos presentes no código

O bot tem **39 comandos personalizados**, além da ajuda padrão da biblioteca:

| Grupo | Comandos |
| --- | --- |
| Normais | `ping`, `oi`, `eco`, `avatar`, `perfil`, `info` |
| Utilitários | `ajuda`, `servidor`, `lembrar`, `anunciar`, `hora`, `denunciar` |
| Moderação | `limpar`, `slowmode`, `trancar`, `destrancar`, `timeout` |
| Diversão | `sortear`, `enquete`, `jokenpo`, `bola8`, `dado`, `escolher`, `calcular` |
| RPG | `dadorpg`, `atributos`, `modificador`, `iniciativa`, `teste`, `dano`, `vantagem`, `desvantagem`, `cura`, `resistencia`, `npc`, `tesouro`, `missao`, `monstro`, `evento` |

Também existem eventos de boas-vindas, cargo automático, saída de membros e logs. As falhas de envio são tratadas separadamente para não interromper as outras ações.

### Correções incorporadas

- Intents de membros e conteúdo de mensagens configuradas antes de criar o bot.
- Verificações de permissão e hierarquia no timeout.
- Permissão original de envio salva em SQLite ao trancar um canal e restaurada ao destrancar.
- Tratamento geral de erros com mensagens de uso e detalhes técnicos no terminal.
- Menções a `@everyone`, `@here` e cargos bloqueadas por padrão nas mensagens do bot; menções individuais continuam permitidas.
- Intervalos de uso para enquetes, denúncias e sorteios.
- Decoradores de comando e evento de saída duplicados removidos.

## Executar no Windows

Requer Python **3.10 ou superior** e Git. SQLite faz parte do Python.

```powershell
git clone https://github.com/baieu666/VG-Discord-Bot.git
cd VG-Discord-Bot
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Na pasta do projeto, crie um arquivo `.env` com:

```dotenv
DISCORD_TOKEN=seu_token_aqui
```

O arquivo `.env.example` serve como modelo. Ao migrar a instalação atual, copie o `.env` existente para esta pasta. Copie também o `bloqueios.sqlite3` existente para preservar os registros de canais trancados. O banco será criado automaticamente se ainda não existir.

Inicie o bot:

```powershell
.\.venv\Scripts\python.exe bot.py
```

Pare com `Ctrl+C`. Para carregar alterações no código, salve e inicie novamente.

### Configurar o Discord

Em [Discord Developer Portal](https://discord.com/developers/applications), abra a aplicação do bot e ative **Server Members Intent** e **Message Content Intent** na seção **Bot → Privileged Gateway Intents**.

Os IDs dos canais e do cargo automático estão no início de `bot.py`. Ajuste-os para o servidor em que o bot será usado. As mensagens dos eventos procuram os canais dentro do servidor do membro; os demais comandos ainda usam os IDs fixos da configuração atual.

O bot precisa das permissões usadas por cada recurso, como enviar mensagens, adicionar reações, gerenciar mensagens, gerenciar cargos, gerenciar canais e moderar membros. Seu cargo deve estar acima do cargo automático e dos membros que ele vai moderar. Timeout não é aplicado ao dono do servidor nem a administradores.

## Intervalos de uso

| Comando | Limite |
| --- | --- |
| `!enquete` | Uma a cada 30 segundos por canal, compartilhado entre todos |
| `!denunciar` | Uma a cada 60 segundos por membro no servidor |
| `!sortear` | Um a cada 10 segundos por servidor, compartilhado entre todos |

O bot informa o tempo de espera quando o intervalo ainda não terminou. Esses contadores são mantidos em memória e reiniciam quando o bot é reiniciado.

## Validação e pendências

- A sintaxe do arquivo foi validada e os corpos dos 39 comandos foram comparados com o código recebido.
- O desenvolvedor relatou que a versão corrigida iniciou e funcionou no seu computador.
- Timeout e bloqueio/desbloqueio tiveram testes manuais relatados durante o desenvolvimento.
- Os testes manuais dos eventos de entrada e saída após a última correção ficaram pendentes.
- Lembretes usam memória e são perdidos ao reiniciar o bot.
- Denúncias ainda são comandos de texto: o motivo digitado fica visível no canal de origem. Um formulário privado está previsto para uma etapa futura.
- Configuração por servidor, persistência de lembretes, slash commands e organização em módulos são próximas etapas.

Testes rápidos disponíveis:

```text
!ajuda
!lembrar
!lembrar abc teste
!enquete teste
!sortear
```

Os dois comandos de lembrete acima verificam mensagens de erro e não criam lembretes. Repetir uma enquete no mesmo canal antes de 30 segundos deve mostrar o tempo de espera. Repetir um sorteio no mesmo servidor antes de 10 segundos deve fazer o mesmo.

## Trabalhar com Git

A versão funcionando fica registrada em `main`. Para começar a separação em módulos:

```powershell
git switch -c refactor/modulos
```

Depois de uma alteração revisada e testada, registre um commit. Exemplo:

```powershell
git status
git add bot.py README.md
git commit -m "Documenta a configuração do bot"
git push -u origin refactor/modulos
```

Abra um pull request para comparar as mudanças antes de incorporá-las à `main`.

O `.gitignore` exclui o token local, bancos, logs, ambientes virtuais e caches. O GitHub guarda o código e seu histórico; a execução do bot continua no computador ou no serviço de hospedagem configurado.
