#region Imports

import asyncio
import discord
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.validacoes import validar_texto
from discord.ext import commands

#endregion

#region Menu Ajuda

class MenuAjuda(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(SeletorAjuda())

class SeletorAjuda(discord.ui.Select):

    def __init__(self):
        opcoes = [discord.SelectOption(label='Comandos Normais', value='normal'), discord.SelectOption(label='Comandos Utilitários', value='utilitarios'), discord.SelectOption(label='Comandos de Diversão', value='diversao'), discord.SelectOption(label='Comandos de RPG', value='rpg')]
        super().__init__(placeholder='Escolha uma categoria...', min_values=1, max_values=1, options=opcoes)

    async def callback(self, interaction: discord.Interaction):
        listas = {
'normal':
'**Comandos Normais**\n'
'`!ping` ➔ *Verifica se o bot está funcionando*\n'
'`!oi` ➔ *Cumprimenta o usuário*\n'
'`!eco <mensagem>` ➔ *Repete a mensagem enviada*\n'
'`!avatar [@pessoa]` ➔ *Exibe o avatar do usuário mencionado ou do autor se nenhum for mencionado*\n'
'`!perfil [@pessoa]` ➔ *Exibe informações do perfil do usuário mencionado ou do autor se nenhum for mencionado*\n'
'`!info` ➔ *Exibe informações sobre o bot*\n'
'`!servidor` ➔ *Exibe informações sobre o servidor*\n'

'', 'utilitarios': 
'**Comandos Utilitários**\n'
'`!ajuda` ➔ *Exibe esta mensagem de ajuda*\n'
'`!limpar <quantidade>` ➔ *Limpa a quantidade especificada de mensagens*\n'
'`!lembrar <minutos> <mensagem>` ➔ *Define um lembrete que será enviado após o tempo especificado*\n'
'`!anunciar <mensagem>` ➔ *Envia um anúncio no canal atual (requer permissão de gerenciar mensagens)*\n'
'`!hora` ➔ *Exibe a hora atual*\n'
'`!enquete <pergunta>` ➔ *Cria uma enquete com a pergunta especificada*\n'
'`!denunciar <@pessoa> <motivo>` ➔ *Envia uma denúncia para o canal de logs do servidor*\n'
'`!slowmode <segundos>` ➔ *Define o modo lento do canal atual (requer permissão de gerenciar canais)*\n'
'`!trancar` ➔ *Tranca o canal atual (requer permissão de gerenciar canais)*\n'
'`!destrancar` ➔ *Destranca o canal atual (requer permissão de gerenciar canais)*\n'
'`!timeout <@pessoa> <minutos> [motivo]` ➔ *Aplica timeout a um membro (requer permissão de moderar membros)*\n'

'', 'diversao': 
'**Comandos de Diversão**\n'
'`!sortear` ➔ *Sorteia um membro aleatório do servidor*\n'
'`!jokenpo <pedra/papel/tesoura>` ➔ *Joga jokenpo com o bot (como usar: Dê !jokenpo e escolha entre pedra, papel ou tesoura)*\n'
'`!bola8 <pergunta>` ➔ *Responde a uma pergunta com uma resposta aleatória*\n'
'`!dado <lados>` ➔ *Rola um dado com o número de lados especificado*\n'
'`!escolher <opções separadas por vírgula>` ➔ *Escolhe aleatoriamente entre as opções fornecidas*\n'
'`!calcular <número> <operação> <número>` ➔ *Realiza um cálculo simples*\n'

'', 'rpg': 
'**Comandos de RPG**\n'
'`!dadorpg <dados>` ➔ *Rola dados no formato de RPG (ex: 2d6+3)*\n'
'`!atributos` ➔ *Gera atributos aleatórios de RPG (Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma)*\n'
'`!modificador <pontuação>` ➔ *Calcula o modificador de atributo com base na pontuação fornecida*\n'
'`!iniciativa [bônus]` ➔ *Rola iniciativa*\n'
'`!teste <CD> [bônus]` ➔ *Faz um teste de RPG*\n'
'`!dano <dados>` ➔ *Rola dano, exemplo: `!dano 1d8+3`*\n'
'`!vantagem` ➔ *Rola dois d20 e fica com o maior*\n'
'`!desvantagem` ➔ *Rola dois d20 e fica com o menor*\n'
'`!cura <dados>` ➔ *Rola cura, exemplo: `!cura 2d8+3`*\n'
'`!resistencia [bônus]` ➔ *Rola teste de resistência, exemplo: `!resistencia 2`*\n'
'`!npc` ➔ *Gera um NPC aleatório com nome, raça, profissão e traço de personalidade*\n'
'`!tesouro` ➔ *Encontra um tesouro aleatório com itens e moedas*\n'
'`!missao` ➔ *Gera uma missão aleatória com objetivos, locais e complicações*\n'
'`!monstro` ➔ *Gera um monstro aleatório com estatísticas*\n'
'`!evento` ➔ *Gera um evento aleatório para a aventura*\n'
}
        categoria = self.values[0]
        await interaction.response.edit_message(content=listas[categoria], view=self.view)

#endregion

class Utilitarios(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ajuda(self, ctx):
        await ctx.send(
            'Escolha uma categoria para ver os comandos que o VG oferece:',
            view=MenuAjuda()
        )

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