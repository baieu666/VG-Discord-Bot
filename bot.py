#region Imports

import os
import discord
import random
import re
import asyncio
import sqlite3
import traceback
from config import LOGS_CHANNEL_ID
from utils.validacoes import validar_texto
from urllib.parse import quote
from pathlib import Path
from contextlib import closing
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

#endregion

load_dotenv()

#region Intents

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#endregion

class VGBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension('cogs.normais')
        await self.load_extension('cogs.utilitarios')
        await self.load_extension('cogs.moderacao')
        await self.load_extension('cogs.diversao')

#region botStart

bot = VGBot(command_prefix='!', intents=intents, 
allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True, replied_user=False))

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user} ; by baieu666 xD')

#endregion

#region ID

CANAL_BOAS_VINDAS_ID = 1376318643545047040
CANAL_SAIDA_ID = 1376319478090170471
CARGO_AUTOMATICO_ID = 1070059865004855337

#endregion

#region Utilitários

@bot.command()
async def ajuda(ctx):
    await ctx.send('Escolha uma categoria para ver os comandos que o VG oferece:', view=MenuAjuda())

#endregion

#region Diversão

@bot.command(cooldown_after_parsing=True)
@commands.cooldown(1, 10, commands.BucketType.guild)
@commands.guild_only()
async def sortear(ctx):
    try:
        membros = [membro async for membro in ctx.guild.fetch_members(limit=None) if not membro.bot]
    except discord.Forbidden:
        await ctx.reply('Não consegui acessar a lista de membros.')
        return
    except discord.ClientException:
        await ctx.reply('Ative o Server Members Intent no código e no Developer Portal.')
        return
    except discord.HTTPException as erro:
        await ctx.reply(f'Erro ao buscar os membros: {erro}')
        return
    if not membros:
        await ctx.reply('Não encontrei membros para sortear.')
        return
    sorteado = random.choice(membros)
    await ctx.send(f'🎉 A pessoa sorteada foi {sorteado.mention}!')

    prefixo = f'🎱 **{ctx.author.display_name} perguntou:** '
    separador = '\n**Resposta:** '
    maior_resposta = max(len(resposta) for resposta in respostas)

    limite = (
        2000
        - len(prefixo)
        - len(separador)
        - maior_resposta
    )

    if not await validar_texto(ctx, pergunta, limite, 'A pergunta'):
        return

    resposta = random.choice(respostas)

    await ctx.send(f'{prefixo}{pergunta}{separador}{resposta}')

@bot.command()
async def calcular(ctx, numero1: float, operacao: str, numero2: float):
    if operacao == '+':
        resultado = numero1 + numero2
    elif operacao == '-':
        resultado = numero1 - numero2
    elif operacao in ('*', 'x'):
        resultado = numero1 * numero2
    elif operacao == '/':
        if numero2 == 0:
            await ctx.reply('Não dá para dividir por zero.')
            return
        resultado = numero1 / numero2
    else:
        await ctx.reply('Use uma operação: `+`, `-`, `*` ou `/`.')
        return
    await ctx.send(f'🧮 {numero1:g} {operacao} {numero2:g} = **{resultado:g}**')

#endregion

#region RPG

@bot.command()
async def dadorpg(ctx, notacao: str='1d6'):
    if not await validar_texto(ctx, notacao, 50, 'A notação dos dados'):
        return
    resultado = re.fullmatch('(\\d*)d(\\d+)([+-]\\d+)?', notacao.lower())
    if not resultado:
        await ctx.reply('Formato inválido. Exemplos: `d20`, `2d6+3`, `4d8-1`.')
        return
    quantidade = int(resultado.group(1) or 1)
    lados = int(resultado.group(2))
    modificador = int(resultado.group(3) or 0)
    if quantidade < 1 or quantidade > 20 or lados < 2 or (lados > 100):
        await ctx.reply('Use de 1 a 20 dados, com 2 a 100 lados cada.')
        return
    rolagens = [random.randint(1, lados) for _ in range(quantidade)]
    total = sum(rolagens) + modificador
    detalhes = ' + '.join((str(rolagem) for rolagem in rolagens))
    if modificador > 0:
        detalhes += f' + {modificador}'
    elif modificador < 0:
        detalhes += f' - {abs(modificador)}'
    await ctx.send(f'🎲 Rolagem `{notacao}`: **{total}** (`{detalhes}`)')

@bot.command()
async def atributos(ctx):
    nomes = ['Força', 'Destreza', 'Constituição', 'Inteligência', 'Sabedoria', 'Carisma']
    embed = discord.Embed(title=f'Atributos de {ctx.author.display_name}', color=discord.Color.purple())
    for nome in nomes:
        dados = sorted([random.randint(1, 6) for _ in range(4)])
        total = sum(dados[1:])
        embed.add_field(name=nome, value=f'**{total}** — dados: {dados}', inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def modificador(ctx, pontuacao: int):
    if pontuacao < 1 or pontuacao > 30:
        await ctx.reply('Use uma pontuação de 1 a 30.')
        return
    valor = (pontuacao - 10) // 2
    sinal = f'+{valor}' if valor >= 0 else str(valor)
    await ctx.send(f'🎲 Atributo **{pontuacao}** dá modificador **{sinal}**.')

@bot.command()
async def iniciativa(ctx, bonus: int=0):
    d20 = random.randint(1, 20)
    total = d20 + bonus
    await ctx.send(f'⚔️ **{ctx.author.display_name}** rolou iniciativa: d20 ({d20}) {bonus:+} = **{total}**')

@bot.command()
async def teste(ctx, cd: int, bonus: int=0):
    d20 = random.randint(1, 20)
    total = d20 + bonus
    resultado = '✅ Sucesso!' if total >= cd else '❌ Falha!'
    await ctx.send(f'🎲 CD {cd}: d20 ({d20}) {bonus:+} = **{total}** — {resultado}')

@bot.command()
async def dano(ctx, notacao: str):
    if not await validar_texto(ctx, notacao, 50, 'A notação dos dados'):
        return
    resultado = re.fullmatch('(\\d*)d(\\d+)([+-]\\d+)?', notacao.lower())
    if not resultado:
        await ctx.reply('Formato inválido. Exemplo: `!dano 1d8+3`.')
        return
    quantidade = int(resultado.group(1) or 1)
    lados = int(resultado.group(2))
    modificador = int(resultado.group(3) or 0)
    if quantidade < 1 or quantidade > 20 or lados < 2 or (lados > 100):
        await ctx.reply('Use de 1 a 20 dados, com 2 a 100 lados cada.')
        return
    rolagens = [random.randint(1, lados) for _ in range(quantidade)]
    total = sum(rolagens) + modificador
    await ctx.send(f'🗡️ Dano `{notacao}`: **{total}** (rolagens: {rolagens}, modificador: {modificador:+})')

@bot.command()
async def vantagem(ctx):
    dado1 = random.randint(1, 20)
    dado2 = random.randint(1, 20)
    resultado = max(dado1, dado2)
    await ctx.send(f'🎲 Vantagem: tirei **{dado1}** e **{dado2}**. Fico com **{resultado}**!')

@bot.command()
async def desvantagem(ctx):
    dado1 = random.randint(1, 20)
    dado2 = random.randint(1, 20)
    resultado = min(dado1, dado2)
    await ctx.send(f'🎲 Desvantagem: tirei **{dado1}** e **{dado2}**. Fico com **{resultado}**!')

@bot.command()
async def cura(ctx, notacao):
    if not await validar_texto(ctx, notacao, 50, 'A notação dos dados'):
        return
    correspondencia = re.fullmatch('(\\d*)d(\\d+)([+-]\\d+)?', notacao.lower().replace(' ', ''))
    if not correspondencia:
        await ctx.send('Use assim: `!cura 2d8+3`')
        return
    quantidade = int(correspondencia.group(1) or 1)
    lados = int(correspondencia.group(2))
    bonus = int(correspondencia.group(3) or 0)
    if quantidade < 1 or quantidade > 20 or lados < 2 or (lados > 100):
        await ctx.send('Use de 1 a 20 dados, com 2 a 100 lados cada.')
        return
    rolagens = [random.randint(1, lados) for _ in range(quantidade)]
    total = sum(rolagens) + bonus
    bonus_texto = f' {bonus:+}' if bonus else ''
    await ctx.send(f'💚 Cura: **{total}** (dados: {rolagens}{bonus_texto})')

@bot.command()
async def resistencia(ctx, bonus: int=0):
    dado = random.randint(1, 20)
    total = dado + bonus
    await ctx.send(f'🛡️ Resistência: tirei **{dado}** no d20 e somei **{bonus:+}**. Total: **{total}**.')

@bot.command()
async def npc(ctx):
    nomes = ['Aldric', 'Mira', 'Thoren', 'Lys', 'Borin', 'Nara']
    racas = ['Humano', 'Elfo', 'Anão', 'Halfling', 'Meio-orc', 'Tiefling']
    ocupacoes = ['ferreiro', 'mercador', 'guarda', 'curandeiro', 'bardo', 'viajante']
    tracos = ['desconfiado', 'bem-humorado', 'misterioso', 'corajoso', 'distraído']
    nome = random.choice(nomes)
    raca = random.choice(racas)
    ocupacao = random.choice(ocupacoes)
    traco = random.choice(tracos)
    await ctx.send(f'🧙 **NPC: {nome}**\nRaça: {raca}\nProfissão: {ocupacao}\nPersonalidade: {traco}')

@bot.command()
async def tesouro(ctx):
    itens = ['uma poção de cura', 'uma adaga enferrujada', 'um mapa misterioso', 'um anel antigo', 'uma pedra brilhante', 'uma bolsa vazia']
    item = random.choice(itens)
    moedas = random.randint(5, 100)
    await ctx.send(f'🎁 **Tesouro encontrado!**\nItem: {item}\nMoedas de ouro: {moedas}')

@bot.command()
async def missao(ctx):
    objetivos = ['encontrar uma pessoa desaparecida', 'recuperar um objeto roubado', 'proteger uma caravana', 'investigar uma criatura misteriosa', 'entregar uma mensagem secreta']
    lugares = ['numa floresta antiga', 'numa vila abandonada', 'numa caverna perto da montanha', 'num castelo em ruínas', 'numa cidade movimentada']
    complicacoes = ['mas alguém do grupo está escondendo algo', 'mas o tempo está acabando', 'mas o caminho está cheio de armadilhas', 'mas a missão não é o que parece', 'mas outra equipe chegou primeiro']
    await ctx.send(f'📜 **Nova missão!**\nO grupo precisa {random.choice(objetivos)} {random.choice(lugares)}, {random.choice(complicacoes)}.')

@bot.command()
async def monstro(ctx):
    monstros = ['Goblin', 'Esqueleto', 'Lobo sombrio', 'Slime', 'Orc', 'Aranha gigante']
    nome = random.choice(monstros)
    vida = random.randint(10, 40)
    defesa = random.randint(10, 18)
    dano = random.randint(1, 8)
    await ctx.send(f'👹 **{nome} apareceu!**\n❤️ Vida: **{vida}**\n🛡️ Defesa: **{defesa}**\n⚔️ Dano do ataque: **1d{dano}**')

@bot.command()
async def evento(ctx):
    eventos = ['o grupo encontra pegadas recentes no caminho', 'uma tempestade começa de repente', 'um viajante pede ajuda', 'um objeto estranho começa a brilhar', 'o grupo ouve um barulho vindo de perto', 'uma ponte bloqueia o caminho']
    await ctx.send(f'🎲 **Evento da aventura:** {random.choice(eventos)}.')

#endregion

#region Eventos de Entrada e Saída

@bot.event
async def on_member_join(member):
    resultado_boas_vindas = await enviar_aviso(member.guild, CANAL_BOAS_VINDAS_ID, f'Seja bem-vindo(a), {member.mention}! Aproveite o servidor.', mencoes=discord.AllowedMentions(users=[member], roles=False, everyone=False, replied_user=False))
    cargo = member.guild.get_role(CARGO_AUTOMATICO_ID)
    resultado_cargo = 'não encontrado; confira o ID do cargo'
    if cargo is not None:
        try:
            await member.add_roles(cargo, reason='Cargo automático de entrada')
            resultado_cargo = f'atribuído: {cargo.name}'
        except discord.Forbidden:
            resultado_cargo = 'não atribuído; confira as permissões e a posição dos cargos'
        except discord.HTTPException as erro:
            print(f'[Eventos] Falha ao dar cargo ao membro {member.id}: {erro}')
            resultado_cargo = 'não atribuído; erro do Discord'
    texto_log = f'📥 Entrou: {member} (ID: {member.id})\nBoas-vindas: {resultado_boas_vindas}\nCargo automático: {resultado_cargo}'
    print(f'[Servidor {member.guild.id}] {texto_log}')
    await enviar_aviso(member.guild, LOGS_CHANNEL_ID, texto_log)

@bot.event
async def on_member_remove(member):
    resultado_saida = await enviar_aviso(member.guild, CANAL_SAIDA_ID, f'{member.display_name} saiu do servidor. Até mais! 👋')
    texto_log = f'📤 Saiu: {member} (ID: {member.id})\nAviso de saída: {resultado_saida}'
    print(f'[Servidor {member.guild.id}] {texto_log}')
    await enviar_aviso(member.guild, LOGS_CHANNEL_ID, texto_log)

async def enviar_aviso(guild, canal_id, texto, *, mencoes=None):
    canal = guild.get_channel(canal_id)
    if not isinstance(canal, discord.TextChannel):
        print(f'[Eventos] Canal {canal_id} ausente ou inválido no servidor {guild.id}.')
        return 'não enviado; canal ausente ou inválido'
    try:
        await canal.send(texto, allowed_mentions=mencoes if mencoes is not None else discord.AllowedMentions.none())
        return 'enviado'
    except discord.Forbidden as erro:
        print(f'[Eventos] Sem permissão no canal {canal_id}: {erro}')
        return 'não enviado; sem permissão'
    except discord.HTTPException as erro:
        print(f'[Eventos] Falha no canal {canal_id}: {erro}')
        return 'não enviado; erro do Discord'

#endregion

#region Categorias

class MenuAjuda(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(SeletorAjuda())

class SeletorAjuda(discord.ui.Select):

    def __init__(self):
        opcoes = [discord.SelectOption(label='Comandos Normais', value='normal'), discord.SelectOption(label='Comandos Utilitários', value='utilitarios'), discord.SelectOption(label='Comandos de Diversão', value='diversao'), discord.SelectOption(label='Comandos de RPG', value='rpg')]
        super().__init__(placeholder='Escolha uma categoria...', min_values=1, max_values=1, options=opcoes)

    async def callback(self, interaction: discord.Interaction):
        listas = {
'normal':
'**Comandos Normais**\n'
'`!ping` ➔ *Verifica se o bot está funcionando*\n'
'`!oi` ➔ *Cumprimenta o usuário*\n'
'`!eco <mensagem>` ➔ *Repete a mensagem enviada*\n'
'`!avatar [@pessoa]` ➔ *Exibe o avatar do usuário mencionado ou do autor se nenhum for mencionado*\n'
'`!perfil [@pessoa]` ➔ *Exibe informações do perfil do usuário mencionado ou do autor se nenhum for mencionado*\n'
'`!info` ➔ *Exibe informações sobre o bot*\n'
'`!servidor` ➔ *Exibe informações sobre o servidor*\n'

'', 'utilitarios': 
'**Comandos Utilitários**\n'
'`!ajuda` ➔ *Exibe esta mensagem de ajuda*\n'
'`!limpar <quantidade>` ➔ *Limpa a quantidade especificada de mensagens*\n'
'`!lembrar <minutos> <mensagem>` ➔ *Define um lembrete que será enviado após o tempo especificado*\n'
'`!anunciar <mensagem>` ➔ *Envia um anúncio no canal atual (requer permissão de gerenciar mensagens)*\n'
'`!hora` ➔ *Exibe a hora atual*\n'
'`!enquete <pergunta>` ➔ *Cria uma enquete com a pergunta especificada*\n'
'`!denunciar <@pessoa> <motivo>` ➔ *Envia uma denúncia para o canal de logs do servidor*\n'
'`!slowmode <segundos>` ➔ *Define o modo lento do canal atual (requer permissão de gerenciar canais)*\n'
'`!trancar` ➔ *Tranca o canal atual (requer permissão de gerenciar canais)*\n'
'`!destrancar` ➔ *Destranca o canal atual (requer permissão de gerenciar canais)*\n'
'`!timeout <@pessoa> <minutos> [motivo]` ➔ *Aplica timeout a um membro (requer permissão de moderar membros)*\n'

'', 'diversao': 
'**Comandos de Diversão**\n'
'`!sortear` ➔ *Sorteia um membro aleatório do servidor*\n'
'`!jokenpo <pedra/papel/tesoura>` ➔ *Joga jokenpo com o bot (como usar: Dê !jokenpo e escolha entre pedra, papel ou tesoura)*\n'
'`!bola8 <pergunta>` ➔ *Responde a uma pergunta com uma resposta aleatória*\n'
'`!dado <lados>` ➔ *Rola um dado com o número de lados especificado*\n'
'`!escolher <opções separadas por vírgula>` ➔ *Escolhe aleatoriamente entre as opções fornecidas*\n'
'`!calcular <número> <operação> <número>` ➔ *Realiza um cálculo simples*\n'

'', 'rpg': 
'**Comandos de RPG**\n'
'`!dadorpg <dados>` ➔ *Rola dados no formato de RPG (ex: 2d6+3)*\n'
'`!atributos` ➔ *Gera atributos aleatórios de RPG (Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma)*\n'
'`!modificador <pontuação>` ➔ *Calcula o modificador de atributo com base na pontuação fornecida*\n'
'`!iniciativa [bônus]` ➔ *Rola iniciativa*\n'
'`!teste <CD> [bônus]` ➔ *Faz um teste de RPG*\n'
'`!dano <dados>` ➔ *Rola dano, exemplo: `!dano 1d8+3`*\n'
'`!vantagem` ➔ *Rola dois d20 e fica com o maior*\n'
'`!desvantagem` ➔ *Rola dois d20 e fica com o menor*\n'
'`!cura <dados>` ➔ *Rola cura, exemplo: `!cura 2d8+3`*\n'
'`!resistencia [bônus]` ➔ *Rola teste de resistência, exemplo: `!resistencia 2`*\n'
'`!npc` ➔ *Gera um NPC aleatório com nome, raça, profissão e traço de personalidade*\n'
'`!tesouro` ➔ *Encontra um tesouro aleatório com itens e moedas*\n'
'`!missao` ➔ *Gera uma missão aleatória com objetivos, locais e complicações*\n'
'`!monstro` ➔ *Gera um monstro aleatório com estatísticas*\n'
'`!evento` ➔ *Gera um evento aleatório para a aventura*\n'
}
        categoria = self.values[0]
        await interaction.response.edit_message(content=listas[categoria], view=self.view)

#endregion

#region Trancar/Destrancar

ARQUIVO_BLOQUEIOS = Path(__file__).resolve().with_name('bloqueios.sqlite3')
travas_bloqueios = {}

def banco_bloqueios(sql, parametros=()):
    with closing(sqlite3.connect(ARQUIVO_BLOQUEIOS)) as conexao:
        resultado = conexao.execute(sql, parametros).fetchone()
        conexao.commit()
        return resultado
banco_bloqueios('\n\n    CREATE TABLE IF NOT EXISTS bloqueios (\n\n        canal_id INTEGER PRIMARY KEY,\n\n        envio_original INTEGER\n\n    )\n\n')

async def alterar_bloqueio(ctx, bloquear):
    if not isinstance(ctx.channel, discord.TextChannel):
        await ctx.reply('Use este comando em um canal de texto, fora de threads.')
        return
    if not ctx.channel.permissions_for(ctx.author).manage_channels:
        await ctx.reply(
            'Você precisa da permissão **Gerenciar canais** neste canal.'
        )
        return

    if not ctx.channel.permissions_for(ctx.guild.me).manage_roles:
        await ctx.reply(
            'Eu preciso da permissão **Gerenciar cargos** neste canal.'
        )
        return
    trava = travas_bloqueios.setdefault(ctx.channel.id, asyncio.Lock())
    async with trava:
        try:
            canal = await ctx.guild.fetch_channel(ctx.channel.id)
            cargo_todos = ctx.guild.default_role
            permissao = canal.overwrites_for(cargo_todos)
            registro = banco_bloqueios('SELECT envio_original FROM bloqueios WHERE canal_id = ?', (canal.id,))
            if bloquear:
                if registro is not None:
                    await ctx.reply('Já existe um bloqueio salvo. Use `!destrancar` primeiro.')
                    return
                if permissao.send_messages is False:
                    await ctx.reply('O envio de mensagens para @everyone já está negado. Não alterei nada.', allowed_mentions=discord.AllowedMentions.none())
                    return
                banco_bloqueios('INSERT INTO bloqueios (canal_id, envio_original) VALUES (?, ?)', (canal.id, permissao.send_messages))
                permissao.send_messages = False
            else:
                if registro is None:
                    await ctx.reply('Não tenho uma permissão original salva para este canal.')
                    return
                permissao.send_messages = None if registro[0] is None else bool(registro[0])
            await canal.set_permissions(cargo_todos, overwrite=None if permissao.is_empty() else permissao, reason=f"{('Trancar' if bloquear else 'Destrancar')} por {ctx.author} ({ctx.author.id})")
            if not bloquear:
                banco_bloqueios('DELETE FROM bloqueios WHERE canal_id = ?', (canal.id,))
        except discord.Forbidden:
            await ctx.reply('Não consegui alterar as permissões. Se há um registro salvo, corrija minhas permissões e use `!destrancar`.')
            return
        except discord.HTTPException:
            await ctx.reply('O Discord não confirmou a alteração. Se há um registro salvo, use `!destrancar` para restaurar o estado anterior.')
            return
        except sqlite3.Error:
            await ctx.reply('Falha no banco de bloqueios. Confira o terminal antes de tentar novamente.')
            raise
        mensagem = '🔒 Envio de mensagens negado para @everyone.' if bloquear else '🔓 Permissão original de envio restaurada.'
        try:
            await ctx.send(mensagem, allowed_mentions=discord.AllowedMentions.none())
        except discord.HTTPException as erro:
            print(f'Permissão alterada no canal {canal.id}, mas não consegui enviar a confirmação: {erro}')

@bot.command()
@commands.guild_only()
async def trancar(ctx):
    await alterar_bloqueio(ctx, True)

@bot.command()
@commands.guild_only()
async def destrancar(ctx):
    await alterar_bloqueio(ctx, False)

#endregion

#region Tratamento de Erros no Geral

NOMES_PERMISSOES = {
    'manage_messages': 'Gerenciar mensagens', 'manage_roles': 'Gerenciar cargos', 'manage_channels': 'Gerenciar canais', 'moderate_members': 'Moderar membros', 'send_messages': 'Enviar mensagens', 'view_channel': 'Ver canal', 'read_message_history': 'Ler histórico de mensagens', 'embed_links': 'Inserir links' 
 }

@bot.event
async def on_command_error(ctx, erro):
    if ctx.command is not None and ctx.command.has_error_handler():
        return
    if ctx.cog is not None and ctx.cog.has_error_handler():
        return
    uso = f'{ctx.clean_prefix}{ctx.command.qualified_name} {ctx.command.signature}'.strip() if ctx.command is not None else f'{ctx.clean_prefix}ajuda'
    if isinstance(erro, commands.CommandNotFound):
        mensagem = f'Comando não encontrado. Veja `{ctx.clean_prefix}ajuda`.'
    elif isinstance(erro, commands.MissingRequiredArgument):
        mensagem = f'Faltou o argumento `{erro.param.name}`.\nUso: `{uso}`'
    elif isinstance(erro, commands.MemberNotFound):
        mensagem = f'Não encontrei esse membro. Tente mencioná-lo.\nUso: `{uso}`'
    elif isinstance(erro, commands.BadArgument):
        mensagem = f'Um argumento está em formato inválido.\nUso: `{uso}`'
    elif isinstance(erro, commands.UserInputError):
        mensagem = f'Confira os argumentos e as aspas do comando.\nUso: `{uso}`'
    elif isinstance(erro, commands.BotMissingPermissions):
        permissoes = ', '.join((NOMES_PERMISSOES.get(p, p) for p in erro.missing_permissions))
        mensagem = f'Eu preciso destas permissões: **{permissoes}**.'
    elif isinstance(erro, commands.MissingPermissions):
        permissoes = ', '.join((NOMES_PERMISSOES.get(p, p) for p in erro.missing_permissions))
        mensagem = f'Você precisa destas permissões: **{permissoes}**.'
    elif isinstance(erro, commands.NoPrivateMessage):
        mensagem = 'Use este comando dentro de um servidor.'
    elif isinstance(erro, commands.CommandOnCooldown):
        segundos = max(1, int(erro.retry_after) + 1)
        mensagem = f'Aguarde **{segundos}s** para usar este comando novamente.'
    elif isinstance(erro, commands.CheckFailure):
        mensagem = 'Você não atende aos requisitos para usar este comando.'
    else:
        original = getattr(erro, 'original', erro)
        print(f'[Erro no comando] {ctx.command}')
        traceback.print_exception(type(original), original, original.__traceback__)
        if isinstance(original, discord.Forbidden):
            mensagem = 'O Discord recusou a ação. Confira minhas permissões e a posição dos cargos.'
        elif isinstance(original, discord.HTTPException):
            mensagem = 'O Discord retornou um erro ao executar a ação. Confira o terminal.'
        else:
            mensagem = 'Ocorreu um erro ao executar o comando. Os detalhes estão no terminal.'
    try:
        await ctx.reply(mensagem, mention_author=False, allowed_mentions=discord.AllowedMentions.none())
    except discord.HTTPException as erro_envio:
        print(f'[Erros] Não consegui enviar a resposta: {erro_envio}')

#endregion

#region Token'

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise RuntimeError('Não encontrei o token no arquivo .env')
    
    bot.run(token)

#endregion