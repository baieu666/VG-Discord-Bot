import discord
from discord.ext import commands
from utils.validacoes import validar_texto

class Normais(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong!')

    @commands.command()
    async def oi(self, ctx):
        await ctx.send(f'Salve, {ctx.author.mention}!')

    @commands.command()
    async def eco(self, ctx, *, mensagem):
        if not await validar_texto(ctx, mensagem, 2000, 'A mensagem'):
            return

        await ctx.send(mensagem)

    @commands.command()
    async def info(self, ctx):
        await ctx.send(
        'Eu sou um bot que tem o intuito de auxiliar o Esgoto do Ratão.\n'
        'Developed by: baieu666\n'
        'Versão: 1.0.0'
        )

    @commands.command()
    async def avatar(self, ctx, membro: discord.Member = None):
        membro = membro or ctx.author
        await ctx.send(membro.display_avatar.url)

    @commands.command()
    @commands.guild_only()
    async def perfil(self, ctx, membro: discord.Member | None = None):
        membro = membro or ctx.author
        entrou = discord.utils.format_dt(membro.joined_at, style='D') if membro.joined_at else 'Data indisponível'
        embed = discord.Embed(title=f'Perfil de {membro.display_name}', color=discord.Color.blurple())
        embed.add_field(name='ID', value=membro.id, inline=False)
        embed.add_field(name='Conta criada', value=discord.utils.format_dt(membro.created_at, style='D'))
        embed.add_field(name='Entrou no servidor', value=entrou)
        embed.set_thumbnail(url=membro.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def servidor(self, ctx):
        servidor = ctx.guild
        embed = discord.Embed(title=f'Sobre {servidor.name}', color=discord.Color.blurple())
        embed.add_field(name='Membros', value=servidor.member_count or 'Indisponível', inline=True)
        embed.add_field(name='Criado em', value=discord.utils.format_dt(servidor.created_at, style='D'), inline=True)
        if servidor.icon:
            embed.set_thumbnail(url=servidor.icon.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Normais(bot))