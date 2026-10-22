import random
import discord
from discord.ext import commands
from flask import ctx
from utils.validacoes import validar_texto


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

async def setup(bot):
    await bot.add_cog(Diversao(bot))