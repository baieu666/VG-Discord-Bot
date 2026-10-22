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
    sinal = f'+{valor}' if valor >= 0   else str(valor)
    await ctx.send(f'🎲 Atributo **{pontuacao}** dá modificador **{sinal}**.')

    @commands.command()
    async def modificador(self, ctx, pontuacao: int):
        if pontuacao < 1 or pontuacao > 30:
            await ctx.reply('Use uma pontuação de 1 a 30.')
            return

        valor = (pontuacao - 10) // 2
        sinal = f'+{valor}' if valor >= 0 else str(valor)
        await ctx.send(
            f'🎲 Atributo **{pontuacao}** dá modificador **{sinal}**.'
        )

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

    @commands.command()
    async def modificador(self, ctx, pontuacao: int):
        d20 = random.randint(1, 20)
    total = d20 + bonus
    resultado = '✅ Sucesso!' 
    if total >= cd else '❌ Falha!'
    await ctx.send(f'🎲 CD {cd}: d20 ({d20}) {bonus:+} = **{total}** — {resultado}')

async def setup(bot):
    await bot.add_cog(RPG(bot))