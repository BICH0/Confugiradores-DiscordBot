from dotenv import load_dotenv
from os import getenv
import datetime
import mariadb
import sys
import emojis

load_dotenv()
#conexion
try:
    conn = mariadb.connect(
        user=getenv("USERNAME"),
        password=getenv("PASSWORD"),
        host=getenv("HOST"),
        port=int(getenv("PORT")),
        database=getenv("DATABASE")
    )
except mariadb.Error as e:
    print(f'Ha ocurrido un eror mientras se conectaba a MariaDB: {e}')
    sys.exit(1)
#cursor
conn.auto_reconnect = True
cur=conn.cursor()

async def bot_rem(guild):
    server = str(guild).replace(' ', '').lower()
    try:
        cur.execute(f'DROP TABLE {server}_settings;')
        cur.execute(f'DROP TABLE {server}_reactions;')
        cur.execute(f'DROP TABLE {server}_bdays;')
        conn.ping()
    except:
        pass

# ◤━━━━━━━━━━━━━━━━━━━━━°•RECONNECT•°━━━━━━━━━━━━━━━━━━━━━◥
async def ping():
    try:
        conn.commit()
        conn.ping()
    except mariadb.DatabaseError:
        conn.reconnect()
    except:
        pass

async def reconnect():
    conn.reconnect()

# ◤━━━━━━━━━━━━━━━━━━━━━°•SETTINGS•°━━━━━━━━━━━━━━━━━━━━━◥
async def settings(guild):
    server = str(guild).replace(' ', '').lower()
    botjoin_message = 'El bot de CONFUGIRADORES® ha entrado en el servidor, ya puedes empezar a usarlo con `$help`.'
    try:
        cur.execute(f'SELECT * FROM {server}_settings;')
    except mariadb.ProgrammingError:
        cur.execute(f'CREATE TABLE {server}_settings (opt_name VARCHAR(25), opt_value VARCHAR(30));')
        file1=open('settings.txt', 'r')
        for line in file1.readlines():
            line = line.replace("""
""", '')
            cur.execute(f"SELECT * FROM {server}_settings WHERE opt_name='{line}'")
            if str(cur.fetchmany(1)) == '[]':
                cur.execute(f"INSERT INTO {server}_settings (opt_name, opt_value) VALUES ('{line}','False')")
            else:
                null=cur.fetchone()
        conn.commit()
        if guild.system_channel is None:
            await guild.owner.send(botjoin_message)
        else:
            await guild.system_channel.send(botjoin_message)

async def settings_update(guild):
    server = str(guild).replace(' ','').lower()
    file1 = open('settings.txt', 'r')
    filearr=[]
    curarr= []
    for line in file1.readlines():
        coin=False
        line=line.replace("""
""",'')
        filearr.append(line)
        cur.execute(f"SELECT opt_name FROM {server}_settings WHERE opt_name='{line}';")
        for option in cur:
            option=option[0]
            if str(line) == str(option):
                coin=True
            else:
                pass
        if coin is True:
            pass
        else:
            cur.execute(f"INSERT INTO {server}_settings (opt_name, opt_value) VALUES ('{line}','False');")
    cur.execute(f"SELECT opt_name FROM {server}_settings WHERE 1=1")
    for x in cur:
        curarr.append(x)
    for option in curarr:
        coin2 = False
        option=option[0]
        for line2 in filearr:
            if str(line2) == str(option):
                coin2=True
            else:
                pass
        if coin2 is True:
            pass
        else:
            cur.execute(f"DELETE FROM {server}_settings WHERE opt_name = '{option}';")
    file1.close()
    conn.commit()
    print(f'- [UPDATE] Se han actualizado los ajustes en {server}')

async def settings_list(ctx, guild):
    server = str(guild).replace(' ', '').lower()
    cur.execute(f"SELECT opt_name, opt_value FROM {server}_settings;")
    arr = []
    for (opt_name, opt_value) in cur:
       arr.append(f"{opt_name}:{opt_value}")
    return arr

async def settings_val(guild, opt):
    server = str(guild).replace(' ', '').lower()
    cur.execute(f"SELECT opt_value FROM {server}_settings WHERE opt_name = '{opt}';")
    opt_val = cur.fetchone()
    if opt_val is None:
        return None
    elif opt_val[0] == 'False':
        return 'Default'
    else:
        return opt_val[0]

async def settings_set(ctx, guild, opt, val, role_name):
    if opt is None:
        return None
    else:
        server = str(guild).replace(' ', '').lower()
        cur.execute(f"UPDATE {server}_settings SET opt_value = '{val}' WHERE opt_name = '{opt}';")
        if role_name is None:
            pass
        else:
            val=role_name
        conn.commit()
        return [opt, val]

async def settings_role(ctx, guild):
    server = str(guild).replace(' ', '').lower()
    cur.execute(f"SELECT opt_value FROM {server}_settings WHERE opt_name = 'helper' or opt_name = 'mod' or opt_name = 'admin';")
    arr=[]
    for opt_value in cur:
        opt_value=opt_value[0]
        arr.append(opt_value)
    return arr
####################--REACTIONS--############################

async def react_create(ctx, guild):
    server = str(guild).replace(' ','').lower()
    try:
        cur.execute(f'CREATE TABLE {server}_reactions (role_id VARCHAR(25) PRIMARY KEY, role_emoji VARCHAR(30), role_name VARCHAR(20), role_description VARCHAR(125));')
        conn.commit()
    except:
        return
    return "ok"

async def react_setup(ctx, guild, message):
    server = str(guild).replace(' ', '').lower()
    cur.execute(f'SELECT role_name, role_emoji, role_description FROM {server}_reactions;')
    if message is None:
        message = '_Reacciona con cualquiera de los emoticonos para recibir el rol asociado!!_\n'
    else:
        message = message + '\n'
    emoji_rol = []
    for (role_name, role_emoji, role_description) in cur:
        message += f'[ {role_emoji} ] {role_name}: {role_description}\n'
        emoji_rol.append(emojis.encode(str(role_emoji)))
    msg_react = await ctx.send(message)
    for reaction in emoji_rol:
        await msg_react.add_reaction(reaction)
    message_id = msg_react.id
    cur.execute(f"SELECT opt_value FROM {server}_settings WHERE opt_name = 'reactmsg'")
    old_id = cur.fetchone()
    old_id = old_id[0]
    if old_id is None or str(old_id) == 'False':
        cur.execute(f"UPDATE {server}_settings SET opt_value = '{str(message_id)}' WHERE opt_name = 'reactmsg';")
        conn.commit()
    else:
        cur.execute(f"UPDATE {server}_settings SET opt_value = '{str(message_id)}' WHERE opt_name = 'reactmsg';")
        conn.commit()
        return old_id

async def react_add(ctx, guild, role_id, role_emoji, role_name, role_description):
    server = str(guild).replace(' ', '').lower()
    #print(f'role id -> [{role_id}] role emoji -> [{role_emoji}] role_name -> [{role_name}] role_description -> [{role_description}] guild -> [{server}]')
    try:
        cur.execute(f"INSERT INTO {server}_reactions (role_id, role_emoji, role_name, role_description) VALUES ('{role_id}','{role_emoji}','{role_name}','{role_description}');")
        print(f'[+REACTION] Se ha agregado {role_name} correctamente en {guild}')
        await ctx.send(f'Se ha agregado _{role_name}_ correctamente.')
        conn.commit()
    except:
        await ctx.send('Ha ocurrido un error')

async def react_list(ctx, guild):
    server = str(guild).replace(' ', '').lower()
    cur.execute(f'SELECT role_emoji, role_name FROM {server}_reactions;')
    if cur.fetchone() is None:
        await ctx.send('No hay ningun rol configurado, para añadir uno utiliza `$reaction add <role> <emoji> <descripción> <alias>`')
    else:
        cur.execute(f'SELECT role_emoji, role_name FROM {server}_reactions;')
        for (role_emoji, role_name) in cur:
            await ctx.send(f'Rol: {role_name} --> {role_emoji}')

async def react_del(ctx, guild, role_name):
    server = str(guild).replace(' ','').lower()
    cur.execute(f"SELECT role_name FROM {server}_reactions WHERE role_name = '{role_name}';")
    check = cur.fetchone()
    if str(check[0]) == '[]':
       await ctx.send(f'No existe {role_name}, usa `$reaction list` para ver los roles que puedes borrar (usa el nombre asignado en vez de la mención).')
    else:
        try:
            cur.execute(f"DELETE FROM {server}_reactions WHERE role_name = '{role_name}';")
            print(f'[-REACTION] Se ha eliminado {role_name} correctamente de {guild}')
            await ctx.send(f'Se ha eliminado _{role_name}_ correctamente.')
            conn.commit()
        except:
            await ctx.send(f'No se ha podido eliminar _{role_name}_ porque no existe.')

async def react_update(ctx, opt, role, value):
    server = str(ctx.guild).replace(' ','').lower()
    cur.execute(f"UPDATE {server}_reactions SET role_{opt} = '{value}' WHERE role_id = '{role}';")
    await ctx.send(f'Se ha actualizado _{opt}_ a [{value}] correctamente.')
    conn.commit()

async def react_name(ctx, name):
    server = str(ctx.guild).replace(' ', '').lower()
    cur.execute(f"SELECT role_id FROM {server}_reactions WHERE role_name = '{name}';")
    role_id=cur.fetchone()
    try:
        role_id=role_id[0]
        return role_id
    except:
        return False

async def react_check(ctx, guild, emoji):
    server=str(guild).replace(' ','').lower()
    try:
        cur.execute(f"SELECT role_id FROM {server}_reactions WHERE role_emoji = '{emoji}';")
        role_id = cur.fetchone()
        if role_id is None:
            return
        else:
            return str(role_id)[2:-3]
    except:
        return None

async def react_checkmsg(guild, msg_id):
    try:
        server=str(guild).replace(' ','').lower()
        cur.execute(f"SELECT opt_value FROM {server}_settings WHERE opt_name = 'reactmsg';")
        message_id = cur.fetchone()
        message_id = message_id[0]
        if str(message_id) == str(msg_id):
            return True
        else:
            return False
    except mariadb.InterfaceError:
        conn.reconnect()
####BDAYS
async def bday(ctx, guild, userid, opt, date=None):
    server = str(guild).replace(' ', '').lower()
    if opt == 'set':
        cur.execute(f"SELECT user FROM {server}_bdays WHERE user = '{userid}';")
        coin = cur.fetchone()
        try:
            coin[0]
            return "already"
        except:
            cur.execute(f"INSERT INTO {server}_bdays (user, date) VALUES ('{userid}', '{date}');")
            conn.commit()
            return date
    elif opt == 'remove':
        try:
            cur.execute(f"SELECT * FROM {server}_bdays WHERE user = '{userid}';")
            coin = cur.fetchone()
            coin[0]
            cur.execute(f"DELETE FROM {server}_bdays WHERE user = '{userid}';")
            conn.commit()
            return "ok"
        except:
            return
    elif opt == 'check':
        try:
            cur.execute(f"SELECT date FROM {server}_bdays WHERE user = '{userid}';")
            date=cur.fetchone()
            date=date[0]
            return date
        except:
            return
    elif opt == 'edit':
        cur.execute(f"SELECT date FROM {server}_bdays WHERE user = '{userid}';")
        coin = cur.fetchone()
        try:
            coin[0]
        except:
            return
        cur.execute(f"SELECT date FROM {server}_bdays WHERE user = '{userid}';")
        old_date = cur.fetchone()
        old_date = old_date[0]
        cur.execute(f"UPDATE {server}_bdays SET date = '{date}' WHERE user = '{userid}';")
        return old_date, date

async def bday_check(guild):
    server = str(guild).replace(' ', '').lower()
    rdate = str(datetime.date.today().day) + '/' + str(datetime.date.today().month)
    cur.execute(f"SELECT opt_value FROM {server}_settings WHERE opt_name = 'bday';")
    check=cur.fetchone()
    if str(check[0]) != 'False':
        try:
            cur.execute(f"SELECT user,date FROM {server}_bdays WHERE 1=1;")
            for user,date in cur:
                if str(date) == str(rdate):
                    user = await guild.fetch_member(user)
                    channel = guild.get_channel(int(check[0]))
                    await channel.send(f'Felicidades {user.mention}!!')
                else:
                    pass
        except:
            cur.execute(f"CREATE TABLE {server}_bdays (user VARCHAR(30) PRIMARY KEY, date VARCHAR(10));")
            conn.commit()
    else:
        conn.commit()
        return
