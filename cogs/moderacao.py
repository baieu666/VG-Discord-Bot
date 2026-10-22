#region Imports

import discord
from datetime import timedelta
from urllib.parse import quote
from discord.ext import commands
from utils.validacoes import validar_texto
from config import LOGS_CHANNEL_ID

#endregion

class Moderacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def anunciar(self, ctx, *, texto: str):
        if not await validar_texto(ctx, texto, 4096, 'O anúncio'):
            return

        embed = discord.Embed(
            title='📢 Aviso da moderação',
            description=texto,
            color=discord.Color.gold()
        )
        embed.set_footer(
            text=f'Enviado por {ctx.author.display_name}'
        )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(
        manage_messages=True,
        read_message_history=True
    )
    async def limpar(self, ctx, quantidade: int):
        if quantidade < 1 or quantidade > 100:
            await ctx.reply(
                'Escolha um número entre 1 e 100 para limpar as mensagens.'
            )
            return

        await ctx.message.delete()
        apagadas = await ctx.channel.purge(limit=quantidade)

        unidade = 'mensagem' if len(apagadas) == 1 else 'mensagens'
        await ctx.send(
            f'Apaguei {len(apagadas)} {unidade}.',
            delete_after=5
        )

    @commands.command()
    @commands.guild_only()
    async def slowmode(self, ctx, segundos: int):
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
        except discord.Forbidden:
            await ctx.reply('Não tenho permissão para alterar este canal.')
            return
        except discord.HTTPException:
            await ctx.reply('O Discord não conseguiu alterar o modo lento.')
            return
    
        if segundos == 0:
            mensagem = '🔓 Modo lento desativado neste canal.'
        else:
            mensagem = (
                f'🐢 Modo lento ativado: **{segundos} segundos** entre mensagens.'
            )
    
        try:
            await ctx.send(mensagem)
        except discord.HTTPException as erro:
            print(
                f'[Slowmode] Canal {ctx.channel.id} alterado para {segundos}s, '
                f'mas não consegui enviar a confirmação: {erro}'
            )

    @commands.command()
    @commands.guild_only()
    async def timeout(
            self, ctx, membro: discord.Member, minutos: int,
            *, motivo: str = 'Não informado'
        ):
        if not ctx.author.guild_permissions.moderate_members:
            await ctx.reply('Você precisa da permissão **Moderar membros**.')
            return
        if not ctx.guild.me.guild_permissions.moderate_members:
            await ctx.reply('Eu preciso da permissão **Moderar membros**.')
            return
        if membro.id == ctx.author.id or membro.id == self.bot.user.id:
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
        prefixo_auditoria = f'Aplicado por ID {ctx.author.id}: '
        limite_motivo = 512 - len(quote(prefixo_auditoria, safe='/ '))
    
        if not await validar_texto(ctx, motivo, limite_motivo, 'O motivo'):
            return
    
        motivo_auditoria = f'{prefixo_auditoria}{motivo}'
    
        if len(quote(motivo_auditoria, safe='/ ')) > 512:
            await ctx.reply(
                'O motivo é longo demais para o registro do Discord. '
                'Encurte o texto; acentos e emojis ocupam mais espaço nesse registro.'
            )
            return
        try:
            await membro.timeout(
                timedelta(minutes=minutos),
                reason=motivo_auditoria
            )
        except discord.Forbidden:
            await ctx.reply(
                'Não consegui aplicar o timeout. '
                'Confira as permissões e a posição dos cargos.'
            )
            return
        except discord.HTTPException:
            await ctx.reply('O Discord não conseguiu aplicar o timeout.')
            return
    
        mensagem = (
            f'🔇 {membro.mention} recebeu timeout por '
            f'**{minutos} minuto(s)**. Motivo: {motivo}'
        )
    
        try:
            await ctx.send(mensagem)
        except discord.HTTPException as erro:
            print(
                f'[Timeout] Timeout aplicado ao membro {membro.id}, '
                f'mas não consegui enviar a confirmação: {erro}'
            )

    @commands.command(cooldown_after_parsing=True)
    @commands.cooldown(1, 60, commands.BucketType.member)
    @commands.guild_only()
    async def denunciar(self, ctx, membro: discord.Member, *, motivo: str):
        if not await validar_texto(ctx, motivo, 1024, 'O motivo'):
            return

        canal_logs = ctx.guild.get_channel(LOGS_CHANNEL_ID)

        if not isinstance(canal_logs, discord.TextChannel):
            await ctx.send(
            'Não encontrei um canal de texto válido para os logs neste servidor.'
        )
            return

        embed = discord.Embed(
        title='Denúncia recebida',
        color=discord.Color.orange()
    )
        embed.add_field(
        name='Pessoa denunciada',
        value=membro.mention
    )
        embed.add_field(
        name='Quem denunciou',
        value=ctx.author.mention
    )
        embed.add_field(
        name='Motivo',
        value=motivo,
        inline=False
    )

        await canal_logs.send(
        embed=embed,
        allowed_mentions=discord.AllowedMentions.none()
    )

        await ctx.send('Denúncia enviada para a equipe do servidor.')

async def setup(bot):
    await bot.add_cog(Moderacao(bot))