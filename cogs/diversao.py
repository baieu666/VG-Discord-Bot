#region Imports

import random
import discord
from discord.ext import commands
from utils.validacoes import validar_texto

#endregion

class Diversao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def jokenpo(self, ctx, escolha: str):
        escolha = escolha.lower()
        opcoes = ['pedra', 'papel', 'tesoura']

        if escolha not in opcoes:
            await ctx.reply('Escolha pedra, papel ou tesoura.')
            return

        bot_escolheu = random.choice(opcoes)

        if escolha == bot_escolheu:
            resultado = 'Empate!'
        elif (
            (escolha == 'pedra' and bot_escolheu == 'tesoura')
            or (escolha == 'papel' and bot_escolheu == 'pedra')
            or (escolha == 'tesoura' and bot_escolheu == 'papel')
        ):
            resultado = 'Você ganhou!'
        else:
            resultado = 'Eu ganhei!'

        await ctx.send(
            f'Você: **{escolha}** | Eu: **{bot_escolheu}**\n{resultado}'
        )

    @commands.command()
    async def dado(self, ctx, lados: int = 6):
        if lados < 2 or lados > 100:
            await ctx.reply('Escolha um dado de 2 a 100 lados.')
            return

        resultado = random.randint(1, lados)
        await ctx.send(
            f'🎲 O dado de {lados} lados caiu em **{resultado}**!'
        )

    @commands.command()
    async def bola8(self, ctx, *, pergunta: str):
        respostas = [
            'Com certeza!',
            'É bem provável.',
            'As chances são boas.',
            'Melhor perguntar de novo.',
            'Não conte com isso.',
            'Provavelmente não.',
            'Com certeza não!'
        ]

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

    @commands.command()
    async def escolher(self, ctx, *, texto: str):
        opcoes = [
            opcao.strip()
            for opcao in texto.split(',')
            if opcao.strip()
        ]

        if len(opcoes) < 2:
            await ctx.reply(
                'Mande pelo menos duas opções, separadas por `,`.'
            )
            return

        prefixo = '🤔 Eu escolheria: **'
        sufixo = '**'
        limite = 2000 - len(prefixo) - len(sufixo)

        for opcao in opcoes:
            if not await validar_texto(ctx, opcao, limite, 'Cada opção'):
                return

        escolhido = random.choice(opcoes)
        await ctx.send(f'{prefixo}{escolhido}{sufixo}')

    @commands.command(cooldown_after_parsing=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def sortear(self, ctx):
        try:
            membros = [
                membro
                async for membro in ctx.guild.fetch_members(limit=None)
                if not membro.bot
            ]
        except discord.Forbidden:
            await ctx.reply('Não consegui acessar a lista de membros.')
            return
        except discord.ClientException:
            await ctx.reply(
                'Ative o Server Members Intent no código '
                'e no Developer Portal.'
            )
            return
        except discord.HTTPException as erro:
            await ctx.reply(f'Erro ao buscar os membros: {erro}')
            return

        if not membros:
            await ctx.reply('Não encontrei membros para sortear.')
            return

        sorteado = random.choice(membros)
        await ctx.send(f'🎉 A pessoa sorteada foi {sorteado.mention}!')

    @commands.command()
    async def calcular(self, ctx, numero1: float, operacao: str, numero2: float):
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

        await ctx.send(
            f'🧮 {numero1:g} {operacao} {numero2:g} = **{resultado:g}**'
        )

async def setup(bot):
    await bot.add_cog(Diversao(bot))