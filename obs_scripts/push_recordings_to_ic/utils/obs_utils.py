def is_obs_ctx():
    try:
        return callable(script_path) == True
    except:
        return False


async def setup_simpleobsws(ctx):
    await ctx.connect()
    await ctx.wait_until_identified()

    # return ctx