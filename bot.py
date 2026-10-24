#region Imports

import os
import discord
import traceback
from config import LOGS_CHANNEL_ID
from utils.validacoes import validar_texto
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