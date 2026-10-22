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
from pathlib import Path
from contextlib import closing
from discord.ext import commands
from dotenv import load_dotenv

#endregion

load_dotenv()

#region Intents

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#endregion

#region botStart

class VGBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension('cogs.normais')
        await self.load_extension('cogs.utilitarios')
        await self.load_extension('cogs.moderacao')
        await self.load_extension('cogs.diversao')
        await self.load_extension('cogs.rpg')

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

#region RPG

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