import discord
from PIL import Image
from io import BytesIO
from discord.ext import commands

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def spank(self, ctx, user: discord.Member = None):
        try:
            spank_image = Image.open("images/spank.jpg")
            spank_author = ctx.author.avatar_url_as(size=256)
            spank_data = BytesIO(await spank_author.read())
            sauthor_image = Image.open(spank_data)
            if user is None:
                print('Spanked' + str(ctx.author))
                spank_image.paste(sauthor_image, (819, 386))
                spanker = self.bot.user.avatar_url_as(size=256)
                spanker_data = BytesIO(await spanker.read())
                spanker_image = Image.open(spanker_data)
                spank_image.paste(spanker_image, (566, 0))
                spank_image.save("images/cache/spank.jpg")
                await ctx.send(file = discord.File('images/cache/spank.jpg'))
            else:
                    print('Spanked ' + str(user) + ' by ' + str(ctx.author))
                    spank_image.paste(sauthor_image, (566, 0))
                    spanked = user.avatar_url_as(size=256)
                    spanked_data = BytesIO(await spanked.read())
                    spanked_image = Image.open(spanked_data)
                    spank_image.paste(spanked_image, (819, 386))
                    spank_image.save("images/cache/spank.jpg")
                    await ctx.send(file=discord.File('images/cache/spank.jpg'))
        except:
            em = discord.Embed(title=f'Unknown user',description=f'No se ha podido encontrar al usuario.',color=16711680)
            await ctx.send(embed=em)

    @commands.command()
    async def bonk(self, ctx, user: discord.Member = None):
        try:
            spank_image = Image.open("images/bonk.jpg")
            spank_author = ctx.author.avatar_url_as(size=128)
            spank_data = BytesIO(await spank_author.read())
            sauthor_image = Image.open(spank_data)
            if user is None:
                print('Bonked' + str(ctx.author))
                spank_image.paste(sauthor_image, (735, 505))
                spanker = self.bot.user.avatar_url_as(size=128)
                spanker_data = BytesIO(await spanker.read())
                spanker_image = Image.open(spanker_data)
                spank_image.paste(spanker_image, (203, 282))
                spank_image.save("images/cache/bonk.jpg")
                await ctx.send(file = discord.File('images/cache/bonk.jpg'))
            else:
                print('Bonked ' + str(user) + ' by ' + str(ctx.author))
                spank_image.paste(sauthor_image, (203, 282))
                spanked = user.avatar_url_as(size=128)
                spanked_data = BytesIO(await spanked.read())
                spanked_image = Image.open(spanked_data)
                spank_image.paste(spanked_image, (735, 505))
                spank_image.save("images/cache/bonk.jpg")
                await ctx.send(file=discord.File('images/cache/bonk.jpg'))
        except:
            em = discord.Embed(title=f'Unknown user',description=f'No se ha podido encontrar al usuario.',color=16711680)
            await ctx.send(embed=em)

    @commands.command()
    async def chad(self, ctx, user: discord.Member = None):
        try:
            spank_image = Image.open("images/chad.jpg")
            spank_author = ctx.author.avatar_url_as(size=128)
            spank_data = BytesIO(await spank_author.read())
            sauthor_image = Image.open(spank_data)
            if user is None:
                print('Chad' + str(ctx.author))
                spank_image.paste(sauthor_image, (172, 106))
                spanker = self.bot.user.avatar_url_as(size=128)
                spanker_data = BytesIO(await spanker.read())
                spanker_image = Image.open(spanker_data)
                spank_image.paste(spanker_image, (990, 175))
                spank_image.save("images/cache/chad.jpg")
                await ctx.send(file = discord.File('images/cache/chad.jpg'))
            else:
                print('Chad ' + str(user) + ' by ' + str(ctx.author))
                spank_image.paste(sauthor_image, (990, 175))
                spanked = user.avatar_url_as(size=128)
                spanked_data = BytesIO(await spanked.read())
                spanked_image = Image.open(spanked_data)
                spank_image.paste(spanked_image, (172, 106))
                spank_image.save("images/cache/chad.jpg")
                await ctx.send(file=discord.File('images/cache/chad.jpg'))
        except:
            em = discord.Embed(title=f'Unknown user',description=f'No se ha podido encontrar al usuario.',color=16711680)
            await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Images(bot))
