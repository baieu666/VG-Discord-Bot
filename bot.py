import os
import discord
import random
import re
import asyncio
import sqlite3
import traceback
from pathlib import Path
from contextlib import closing
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timedelta
load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True, replied_user=False))
CANAL_BOAS_VINDAS_ID = 1376318643545047040
LOGS_CHANNEL_ID = 1553817590424404148
CANAL_SAIDA_ID = 1376319478090170471
CARGO_AUTOMATICO_ID = 1070059865004855337

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

@bot.command(cooldown_after_parsing=True)
@commands.cooldown(1, 60, commands.BucketType.member)
@commands.guild_only()
async def denunciar(ctx, membro: discord.Member, *, motivo):
    canal_logs = bot.get_channel(LOGS_CHANNEL_ID)
    if canal_logs is None:
        await ctx.send('Não encontrei o canal de logs.')
        return
    embed = discord.Embed(title='Denúncia recebida', color=discord.Color.orange())
    embed.add_field(name='Pessoa denunciada', value=membro.mention)
    embed.add_field(name='Quem denunciou', value=ctx.author.mention)
    embed.add_field(name='Motivo', value=motivo, inline=False)
    await canal_logs.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
    await ctx.send('Denúncia enviada para a equipe do servidor.')

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.command()
async def ping(ctx):
    await ctx.send('pong!')

@bot.command()
async def oi(ctx):
    await ctx.send(f'Salve, {ctx.author.mention}!')

class SeletorAjuda(discord.ui.Select):

    def __init__(self):
        opcoes = [discord.SelectOption(label='Comandos Normais', value='normal'), discord.SelectOption(label='Comandos Utilitários', value='utilitarios'), discord.SelectOption(label='Comandos de Diversão', value='diversao'), discord.SelectOption(label='Comandos de RPG', value='rpg')]
        super().__init__(placeholder='Escolha uma categoria...', min_values=1, max_values=1, options=opcoes)

    async def callback(self, interaction: discord.Interaction):
        listas = {'normal': '**Comandos Normais**\n`!ping` ➔ *Verifica se o bot está funcionando*\n`!oi` ➔ *Cumprimenta o usuário*\n`!eco <mensagem>` ➔ *Repete a mensagem enviada*\n`!avatar [@pessoa]` ➔ *Exibe o avatar do usuário mencionado ou do autor se nenhum for mencionado*\n`!perfil [@pessoa]` ➔ *Exibe informações do perfil do usuário mencionado ou do autor se nenhum for mencionado*\n`!info` ➔ *Exibe informações sobre o bot*\n', 'utilitarios': '**Comandos Utilitários**\n`!ajuda` ➔ *Exibe esta mensagem de ajuda*\n`!servidor` ➔ *Exibe informações sobre o servidor*\n`!limpar <quantidade>` ➔ *Limpa a quantidade especificada de mensagens*\n`!lembrar <minutos> <mensagem>` ➔ *Define um lembrete que será enviado após o tempo especificado*\n`!anunciar <mensagem>` ➔ *Envia um anúncio no canal atual (requer permissão de gerenciar mensagens)*\n`!hora` ➔ *Exibe a hora atual*\n`!enquete <pergunta>` ➔ *Cria uma enquete com a pergunta especificada*\n`!denunciar <@pessoa> <motivo>` ➔ *Envia uma denúncia para o canal de logs do servidor*\n`!slowmode <segundos>` ➔ *Define o modo lento do canal atual (requer permissão de gerenciar canais)*\n`!trancar` ➔ *Tranca o canal atual (requer permissão de gerenciar canais)*\n`!destrancar` ➔ *Destranca o canal atual (requer permissão de gerenciar canais)*\n`!timeout <@pessoa> <minutos> [motivo]` ➔ *Aplica timeout a um membro (requer permissão de moderar membros)*\n', 'diversao': '**Comandos de Diversão**\n`!sortear` ➔ *Sorteia um membro aleatório do servidor*\n`!enquete <pergunta>` ➔ *Cria uma enquete com a pergunta especificada*\n`!jokenpo <pedra/papel/tesoura>` ➔ *Joga jokenpo com o bot (como usar: Dê !jokenpo e escolha entre pedra, papel ou tesoura)*\n`!bola8 <pergunta>` ➔ *Responde a uma pergunta com uma resposta aleatória*\n`!dado <lados>` ➔ *Rola um dado com o número de lados especificado*\n`!escolher <opções separadas por vírgula>` ➔ *Escolhe aleatoriamente entre as opções fornecidas*\n`!calcular <número> <operação> <número>` ➔ *Realiza um cálculo simples*\n', 'rpg': '**Comandos de RPG**\n`!dadorpg <dados>` ➔ *Rola dados no formato de RPG (ex: 2d6+3)*\n`!atributos` ➔ *Gera atributos aleatórios de RPG (Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma)*\n`!modificador <pontuação>` ➔ *Calcula o modificador de atributo com base na pontuação fornecida*\n`!iniciativa [bônus]` ➔ *Rola iniciativa*\n`!teste <CD> [bônus]` ➔ *Faz um teste de RPG*\n`!dano <dados>` ➔ *Rola dano, exemplo: `!dano 1d8+3`*\n`!vantagem` ➔ *Rola dois d20 e fica com o maior*\n`!desvantagem` ➔ *Rola dois d20 e fica com o menor*\n`!cura <dados>` ➔ *Rola cura, exemplo: `!cura 2d8+3`*\n`!resistencia [bônus]` ➔ *Rola teste de resistência, exemplo: `!resistencia 2`*\n`!npc` ➔ *Gera um NPC aleatório com nome, raça, profissão e traço de personalidade*\n`!tesouro` ➔ *Encontra um tesouro aleatório com itens e moedas*\n`!missao` ➔ *Gera uma missão aleatória com objetivos, locais e complicações*\n`!monstro` ➔ *Gera um monstro aleatório com estatísticas*\n`!evento` ➔ *Gera um evento aleatório para a aventura*\n'}
        categoria = self.values[0]
        await interaction.response.edit_message(content=listas[categoria], view=self.view)

class MenuAjuda(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(SeletorAjuda())

@bot.command()
async def ajuda(ctx):
    await ctx.send('Escolha uma categoria para ver os comandos que o VG oferece:', view=MenuAjuda())

@bot.command()
async def eco(ctx, *, mensagem):
    await ctx.send(mensagem)

@bot.command()
async def info(ctx):
    await ctx.send('Eu sou um bot que tem o intuito de auxiliar o Esgoto do Ratão.\nDeveloped by: baieu666\nVersão: 1.0.0')

@bot.command()
@commands.has_permissions(manage_messages=True)
@commands.bot_has_permissions(manage_messages=True)
async def limpar(ctx, quantidade: int):
    if quantidade < 1 or quantidade > 100:
        await ctx.reply('Escolha um número entre 1 e 100 para limpar as mensagens.')
        return
    await ctx.message.delete()
    apagas = await ctx.channel.purge(limit=quantidade)
    unidade = 'mensagem' if len(apagas) == 1 else 'mensagens'
    await ctx.send(f'Apaguei {len(apagas)} {unidade}.', delete_after=5)

@bot.command()
async def avatar(ctx, membro: discord.Member=None):
    membro = membro or ctx.author
    await ctx.send(membro.display_avatar.url)

@bot.command()
@commands.guild_only()
async def perfil(ctx, membro: discord.Member | None=None):
    membro = membro or ctx.author
    entrou = discord.utils.format_dt(membro.joined_at, style='D') if membro.joined_at else 'Data indisponível'
    embed = discord.Embed(title=f'Perfil de {membro.display_name}', color=discord.Color.blurple())
    embed.add_field(name='ID', value=membro.id, inline=False)
    embed.add_field(name='Conta criada', value=discord.utils.format_dt(membro.created_at, style='D'))
    embed.add_field(name='Entrou no servidor', value=entrou)
    embed.set_thumbnail(url=membro.display_avatar.url)
    await ctx.send(embed=embed)

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

@bot.command()
async def dado(ctx, lados: int=6):
    if lados < 2 or lados > 100:
        await ctx.reply('Escolha um dado de 2 a 100 lados.')
        return
    resultado = random.randint(1, lados)
    await ctx.send(f'🎲 O dado de {lados} lados caiu em **{resultado}**!')

@bot.command()
async def dadorpg(ctx, notacao: str='1d6'):
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

@bot.command(cooldown_after_parsing=True)
@commands.cooldown(1, 30, commands.BucketType.channel)
async def enquete(ctx, *, pergunta: str):
    mensagem = await ctx.send(f'📊 **Enquete:** {pergunta}')
    await mensagem.add_reaction('👍')
    await mensagem.add_reaction('👎')

@bot.command()
async def jokenpo(ctx, escolha: str):
    escolha = escolha.lower()
    opcoes = ['pedra', 'papel', 'tesoura']
    if escolha not in opcoes:
        await ctx.reply('Escolha pedra, papel ou tesoura.')
        return
    bot_escolheu = random.choice(opcoes)
    if escolha == bot_escolheu:
        resultado = 'Empate!'
    elif escolha == 'pedra' and bot_escolheu == 'tesoura' or (escolha == 'papel' and bot_escolheu == 'pedra') or (escolha == 'tesoura' and bot_escolheu == 'papel'):
        resultado = 'Você ganhou!'
    else:
        resultado = 'Eu ganhei!'
    await ctx.send(f'Você: **{escolha}** | Eu: **{bot_escolheu}**\n{resultado}')

@bot.command()
@commands.guild_only()
async def servidor(ctx):
    servidor = ctx.guild
    embed = discord.Embed(title=f'Sobre {servidor.name}', color=discord.Color.blurple())
    embed.add_field(name='Membros', value=servidor.member_count or 'Indisponível', inline=True)
    embed.add_field(name='Criado em', value=discord.utils.format_dt(servidor.created_at, style='D'), inline=True)
    if servidor.icon:
        embed.set_thumbnail(url=servidor.icon.url)
    await ctx.send(embed=embed)

@bot.command()
async def lembrar(ctx, minutos: int, *, mensagem: str):
    if minutos < 1 or minutos > 1440:
        await ctx.reply('Escolha um tempo entre 1 minuto e 24 horas.')
        return
    await ctx.send(f'⏰ Beleza, vou te lembrar em {minutos} minuto(s).')
    await asyncio.sleep(minutos * 60)
    await ctx.send(f'{ctx.author.mention}, lembrete: **{mensagem}**')

@bot.command()
@commands.guild_only()
@commands.has_guild_permissions(manage_messages=True)
async def anunciar(ctx, *, texto: str):
    embed = discord.Embed(title='📢 Aviso da moderação', description=texto, color=discord.Color.gold())
    embed.set_footer(text=f'Enviado por {ctx.author.display_name}')
    await ctx.send(embed=embed)

@bot.command()
async def bola8(ctx, *, pergunta: str):
    respostas = ['Com certeza!', 'É bem provável.', 'As chances são boas.', 'Melhor perguntar de novo.', 'Não conte com isso.', 'Provavelmente não.', 'Com certeza não!']
    resposta = random.choice(respostas)
    await ctx.send(f'🎱 **{ctx.author.display_name} perguntou:** {pergunta}\n**Resposta:** {resposta}')

@bot.command()
async def escolher(ctx, *, texto: str):
    opcoes = [opcao.strip() for opcao in texto.split(',') if opcao.strip()]
    if len(opcoes) < 2:
        await ctx.reply('Mande pelo menos duas opções, separadas por `,`.')
        return
    escolhido = random.choice(opcoes)
    await ctx.send(f'🤔 Eu escolheria: **{escolhido}**')

@bot.command()
async def hora(ctx):
    agora = datetime.now().strftime('%H:%M:%S')
    await ctx.send(f'🕒 Agora são **{agora}**.')

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

@bot.command()
@commands.guild_only()
async def slowmode(ctx, segundos: int):
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.reply('Você precisa da permissão **Gerenciar canais**.')
        return
    permissoes_bot = ctx.channel.permissions_for(ctx.guild.me)
    if not permissoes_bot.manage_channels:
        await ctx.reply('Eu preciso da permissão **Gerenciar canais**.')
        return
    if segundos < 0 or segundos > 21600:
        await ctx.reply('Use um valor entre 0 e 21600 segundos.')
        return
    try:
        await ctx.channel.edit(slowmode_delay=segundos)
        if segundos == 0:
            await ctx.send('🔓 Modo lento desativado neste canal.')
        else:
            await ctx.send(f'🐢 Modo lento ativado: **{segundos} segundos** entre mensagens.')
    except discord.Forbidden:
        await ctx.reply('Não tenho permissão para alterar este canal.')
    except discord.HTTPException:
        await ctx.reply('O Discord não conseguiu alterar o modo lento.')
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
    if not ctx.channel.permissions_for(ctx.author).manage_roles:
        await ctx.reply('Você precisa da permissão **Gerenciar cargos** neste canal.')
        return
    if not ctx.channel.permissions_for(ctx.guild.me).manage_roles:
        await ctx.reply('Eu preciso da permissão **Gerenciar cargos** neste canal.')
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

@bot.command()
@commands.guild_only()
async def timeout(ctx, membro: discord.Member, minutos: int, *, motivo: str='Não informado'):
    if not ctx.author.guild_permissions.moderate_members:
        await ctx.reply('Você precisa da permissão **Moderar membros**.')
        return
    if not ctx.guild.me.guild_permissions.moderate_members:
        await ctx.reply('Eu preciso da permissão **Moderar membros**.')
        return
    if membro.id == ctx.author.id or membro.id == bot.user.id:
        await ctx.reply('Você não pode aplicar timeout em si mesmo ou no bot.')
        return
    if membro.id == ctx.guild.owner_id:
        await ctx.reply('Não posso aplicar timeout no dono do servidor.')
        return
    if membro.guild_permissions.administrator:
        await ctx.reply('Não posso aplicar timeout em alguém com a permissão Administrador.')
        return
    if membro.top_role >= ctx.guild.me.top_role:
        await ctx.reply('O cargo mais alto desse membro precisa estar abaixo do meu.')
        return
    if ctx.author.id != ctx.guild.owner_id and membro.top_role >= ctx.author.top_role:
        await ctx.reply('Você só pode aplicar timeout em membros com cargo abaixo do seu.')
        return
    if minutos < 1 or minutos > 40320:
        await ctx.reply('Escolha uma duração entre 1 minuto e 28 dias.')
        return
    try:
        await membro.timeout(timedelta(minutes=minutos), reason=f'Aplicado por {ctx.author}: {motivo}')
        await ctx.send(f'🔇 {membro.mention} recebeu timeout por **{minutos} minuto(s)**. Motivo: {motivo}')
    except discord.Forbidden:
        await ctx.reply('Não consegui aplicar o timeout. Confira as permissões e a posição dos cargos.')
    except discord.HTTPException:
        await ctx.reply('O Discord não conseguiu aplicar o timeout.')
NOMES_PERMISSOES = {'manage_messages': 'Gerenciar mensagens', 'manage_roles': 'Gerenciar cargos', 'manage_channels': 'Gerenciar canais', 'moderate_members': 'Moderar membros', 'send_messages': 'Enviar mensagens', 'view_channel': 'Ver canal', 'read_message_history': 'Ler histórico de mensagens', 'embed_links': 'Inserir links'}

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
if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise RuntimeError('Não encontrei o token no arquivo .env')
    bot.run(token)
