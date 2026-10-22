import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.validacoes import validar_texto
from discord.ext import commands

class Utilitarios(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hora(self, ctx):
        agora = datetime.now(ZoneInfo('America/Sao_Paulo'))
        await ctx.send(
            f'Agora são {agora:%H:%M:%S} — horário de São Paulo.'
    )

    @commands.command()
    async def lembrar(self, ctx, minutos: int, *, mensagem: str):
        if minutos < 1 or minutos > 1440:
            await ctx.reply('Escolha um tempo entre 1 minuto e 24 horas.')
            return

        prefixo = f'{ctx.author.mention}, lembrete: **'
        sufixo = '**'
        limite = 2000 - len(prefixo) - len(sufixo)

        if not await validar_texto(ctx, mensagem, limite, 'O lembrete'):
            return

        resposta = f'{prefixo}{mensagem}{sufixo}'

        await ctx.send(
            f'⏰ Beleza, vou te lembrar em {minutos} minuto(s).'
        )

        await asyncio.sleep(minutos * 60)
        await ctx.send(resposta)

    @commands.command(cooldown_after_parsing=True)
    @commands.cooldown(1, 30, commands.BucketType.channel)
    async def enquete(self, ctx, *, pergunta: str):
        prefixo = '📊 **Enquete:** '
        limite = 2000 - len(prefixo)

        if not await validar_texto(ctx, pergunta, limite, 'A pergunta'):
            return

        mensagem = await ctx.send(f'{prefixo}{pergunta}')

        await mensagem.add_reaction('👍')
        await mensagem.add_reaction('👎')

async def setup(bot):
    await bot.add_cog(Utilitarios(bot))