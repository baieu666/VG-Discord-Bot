#region Imports

import random
import re
import discord
from discord.ext import commands
from utils.validacoes import validar_texto

#endregion

class RPG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dadorpg(self, ctx, notacao: str = '1d6'):
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

    @commands.command()
    async def atributos(self, ctx):
        nomes = ['Força', 'Destreza', 'Constituição', 'Inteligência', 'Sabedoria', 'Carisma']
        embed = discord.Embed(title=f'Atributos de {ctx.author.display_name}', color=discord.Color.purple())
        for nome in nomes:
            dados = sorted([random.randint(1, 6) for _ in range(4)])
            total = sum(dados[1:])
            embed.add_field(
                name=nome,
                value=f'**{total}** — dados: {dados}',
                inline=True
            )

        await ctx.send(embed=embed)

    @commands.command()
    async def modificador(self, ctx, pontuacao: int):
        if pontuacao < 1 or pontuacao > 30:
            await ctx.reply('Use uma pontuação de 1 a 30.')
            return

        valor = (pontuacao - 10) // 2
        await ctx.send(
            f'🎲 Atributo **{pontuacao}** dá modificador **{valor:+}**.'
        )

    @commands.command()
    async def dano(self, ctx, notacao: str):
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

    @commands.command()
    async def vantagem(self, ctx):
        dado1 = random.randint(1, 20)
        dado2 = random.randint(1, 20)
        resultado = max(dado1, dado2)
        await ctx.send(f'🎲 Vantagem: tirei **{dado1}** e **{dado2}**. Fico com **{resultado}**!')

    @commands.command()
    async def desvantagem(self, ctx):
        dado1 = random.randint(1, 20)
        dado2 = random.randint(1, 20)
        resultado = min(dado1, dado2)
        await ctx.send(f'🎲 Desvantagem: tirei **{dado1}** e **{dado2}**. Fico com **{resultado}**!')

    @commands.command()
    async def cura(self, ctx, notacao):
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

    @commands.command()
    async def resistencia(self, ctx, bonus: int = 0):
        dado = random.randint(1, 20)
        total = dado + bonus
        await ctx.send(f'🛡️ Resistência: tirei **{dado}** no d20 e somei **{bonus:+}**. Total: **{total}**.')

    @commands.command()
    async def npc(self, ctx):
        nomes = ['Aldric', 'Mira', 'Thoren', 'Lys', 'Borin', 'Nara']
        racas = ['Humano', 'Elfo', 'Anão', 'Halfling', 'Meio-orc', 'Tiefling']
        ocupacoes = ['ferreiro', 'mercador', 'guarda', 'curandeiro', 'bardo', 'viajante']
        tracos = ['desconfiado', 'bem-humorado', 'misterioso', 'corajoso', 'distraído']
        nome = random.choice(nomes)
        raca = random.choice(racas)
        ocupacao = random.choice(ocupacoes)
        traco = random.choice(tracos)
        await ctx.send(f'🧙 **NPC: {nome}**\nRaça: {raca}\nProfissão: {ocupacao}\nPersonalidade: {traco}')

    @commands.command()
    async def tesouro(self, ctx):
        itens = ['uma poção de cura', 'uma adaga enferrujada', 'um mapa misterioso', 'um anel antigo', 'uma pedra brilhante', 'uma bolsa vazia']
        item = random.choice(itens)
        moedas = random.randint(5, 100)
        await ctx.send(f'🎁 **Tesouro encontrado!**\nItem: {item}\nMoedas de ouro: {moedas}')

    @commands.command()
    async def missao(self, ctx):
        objetivos = ['encontrar uma pessoa desaparecida', 'recuperar um objeto roubado', 'proteger uma caravana', 'investigar uma criatura misteriosa', 'entregar uma mensagem secreta']
        lugares = ['numa floresta antiga', 'numa vila abandonada', 'numa caverna perto da montanha', 'num castelo em ruínas', 'numa cidade movimentada']
        complicacoes = ['mas alguém do grupo está escondendo algo', 'mas o tempo está acabando', 'mas o caminho está cheio de armadilhas', 'mas a missão não é o que parece', 'mas outra equipe chegou primeiro']
        await ctx.send(f'📜 **Nova missão!**\nO grupo precisa {random.choice(objetivos)} {random.choice(lugares)}, {random.choice(complicacoes)}.')

    @commands.command()
    async def monstro(self, ctx):
        monstros = ['Goblin', 'Esqueleto', 'Lobo sombrio', 'Slime', 'Orc', 'Aranha gigante']
        nome = random.choice(monstros)
        vida = random.randint(10, 40)
        defesa = random.randint(10, 18)
        dano = random.randint(1, 8)
        await ctx.send(f'👹 **{nome} apareceu!**\n❤️ Vida: **{vida}**\n🛡️ Defesa: **{defesa}**\n⚔️ Dano do ataque: **1d{dano}**')

    @commands.command()
    async def evento(self, ctx):
        eventos = ['o grupo encontra pegadas recentes no caminho', 'uma tempestade começa de repente', 'um viajante pede ajuda', 'um objeto estranho começa a brilhar', 'o grupo ouve um barulho vindo de perto', 'uma ponte bloqueia o caminho']
        await ctx.send(f'🎲 **Evento da aventura:** {random.choice(eventos)}.')

    @commands.command()
    async def iniciativa(self, ctx, bonus: int = 0):
        d20 = random.randint(1, 20)
        total = d20 + bonus
        await ctx.send(
            f'⚔️ **{ctx.author.display_name}** rolou iniciativa: '
            f'd20 ({d20}) {bonus:+} = **{total}**'
        )

    @commands.command()
    async def teste(self, ctx, cd: int, bonus: int = 0):
        d20 = random.randint(1, 20)
        total = d20 + bonus
        resultado = '✅ Sucesso!' if total >= cd else '❌ Falha!'
        await ctx.send(
            f'🎲 CD {cd}: d20 ({d20}) {bonus:+} = **{total}** '
            f'{resultado}'
        )   

async def setup(bot):
    await bot.add_cog(RPG(bot))