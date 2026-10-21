async def validar_texto(ctx, texto, limite, nome='O texto'):
    if not texto.strip():
        await ctx.reply(f'{nome} não pode ficar vazio.')
        return False

    if len(texto) > limite:
        await ctx.reply(
            f'{nome} pode ter no máximo **{limite} caracteres**. '
            f'Você enviou **{len(texto)}**.'
        )
        return False

    return True