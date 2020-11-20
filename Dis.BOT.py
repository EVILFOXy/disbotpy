import discord
from discord.ext import commands, tasks
import datetime
from discord import utils
import asyncio
from Data import def_random, config, Gifs
from itertools import cycle
import os

TOKEN = os.environ.get('TOKEN')
prefix = '`'
client = commands.Bot(command_prefix=prefix)
client.remove_command('help')


# --------------------------------------------------------------------------------------------------------------------
# состояние бота
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    # изменяет статус бота в ActivityType(playing, streaming(с указанием на url), listening, watching, custom)
    activ = discord.Activity(name="Хентай", type=discord.ActivityType.watching)
    await client.change_presence(status=discord.Status.online, activity=activ)


# --------------------------------------------------------------------------------------------------------------------

# Выдоча роли при добавлении реакции
@client.event
async def on_raw_reaction_add(payload):
    global emoji
    channel = client.get_channel(config.TC_ID)
    message = await channel.fetch_message(payload.message_id)
    member = utils.get(message.guild.members, id=payload.user_id)

    try:
        emoji = str(payload.emoji)  # эмоджик который выбрал юзер
        role = utils.get(message.guild.roles, id=config.ROLES[emoji])  # объект выбранной роли (если есть)

        if emoji in config.Colors_emoji:

            if len([i for i in member.roles if i.id not in config.EXCROLES_for_color]) <= config.MAX_ROLES_PER_USER:
                await member.add_roles(role)
                print('[SUCCESS] User {0.display_name} has been granted with role {1.name}'.format(member, role))
            else:
                await message.remove_reaction(payload.emoji, member)
                print('[ERROR] Too many roles for user {0.display_name}'.format(member) + '1')

        if emoji in config.alliance_emoji:

            if len([i for i in member.roles if i.id not in config.EXCROLES_for_alliance]) <= config.MAX_ROLES_PER_USER:
                await member.add_roles(role)
                print('[SUCCESS] User {0.display_name} has been granted with role {1.name}'.format(member, role))
            else:
                await message.remove_reaction(payload.emoji, member)
                print('[ERROR] Too many roles for user {0.display_name}'.format(member)+ '2')

    except KeyError:
        print('[ERROR] KeyError, no role found for ' + emoji)
    except Exception as e:
        print(repr(e))


# Снятие роли при удалении реакции
@client.event
async def on_raw_reaction_remove(payload):
    global emoji
    channel = client.get_channel(config.TC_ID)
    message = await channel.fetch_message(payload.message_id)
    member = utils.get(message.guild.members, id=payload.user_id)

    try:
        emoji = str(payload.emoji)  # эмоджик который выбрал юзер
        role = utils.get(message.guild.roles, id=config.ROLES[emoji])  # объект выбранной роли (если есть)

        await member.remove_roles(role)
        print('[SUCCESS] Role {1.name} has been remove for user {0.display_name}'.format(member, role))

    except KeyError:
        print('[ERROR] KeyError, no role found for ' + emoji)
    except Exception as e:
        print(repr(e))


# --------------------------------------------------------------------------------------------------------------------

# Комманды бота:
# Выводит список доступных комманд [`help]
@client.command()
async def help(ctx):
    emb = discord.Embed(title='Список доступных команд:')

    emb.add_field(name='{}help'.format(prefix), value='Выводит текущее окно', inline=False)
    emb.add_field(name='{}clear [кол-во сообщений]'.format(prefix), value='Очистка чата', inline=False)
    emb.add_field(name='{}kick [@пользователь] [причина]'.format(prefix), value='Кик пользователя с сервера',
                  inline=False)
    emb.add_field(name='{}ban [@пользователь] [срок(в минутах) или perm] [причина]'.format(prefix),
                  value='бан пользователя на сервере', inline=False)
    emb.add_field(name='{}unban [@пользователь]'.format(prefix), value='Разбан пользователя на сервере', inline=False)
    emb.add_field(name='{}mute [@пользователь] [срок(в минутах) или perm] [причина]'.format(prefix),
                  value='Запретить писать в чат', inline=False)
    emb.add_field(name='{}unmute [@пользователь]'.format(prefix), value='Разрешить писать в чат', inline=False)
    emb.add_field(name='{}g_role [@пользователь] [название роли]'.format(prefix), value='Выдать роль', inline=False)
    emb.add_field(name='{}r_role [@пользователь] [название роли]'.format(prefix), value='Удалить роль', inline=False)

    await ctx.send(embed=emb)


# Очистка чата [`clear]{<= удалит последнии 10 }
#              [`clear N]{<= удалит последнии N }
@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def clear(ctx, amount=10):
    await ctx.channel.purge(limit=1)
    await ctx.channel.purge(limit=amount)


# Кик пользователя с сервера [`kick {пользователь}]
@client.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await ctx.channel.purge(limit=1)

    # сообщение которое будет отправлено в случае кика:

    # на сервер(в чат где была написана комманда)
    emb_s = discord.Embed(title='Выгнан с сервера', color=discord.Color.red())
    emb_s.set_author(name=member.name, icon_url=member.avatar_url)
    emb_s.set_footer(text='Администратором: {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)

    # пользователю в лс
    emb_m = discord.Embed(title='Вы были заблокированы на сервере: {}'.format(ctx.guild), color=discord.Color.red())
    emb_m.add_field(name='Дата блокировки: {}'.format(datetime.datetime.now()),
                    value='Причина блокировки: {}.'.format(reason))
    emb_m.set_footer(text='Администратор: {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)

    # сообщение которое будет отправлено при попытке выгнать самого себя
    emb_self_kick = discord.Embed(title='Невозможно выгнать самого себя', color=discord.Color.purple())
    emb_self_kick.set_author(name=member.name, icon_url=member.avatar_url)

    if ctx.author != member:
        await member.kick(reason=reason)
        await ctx.send(embed=emb_s)
        await member.send(embed=emb_m)
        print('[SUCCESS] User {} has been kicked by {}'.format(member, ctx.author))
    else:
        await ctx.send(embed=emb_self_kick)
        print('[ERROR] {} try kick himself'.format(ctx.author))


# бан пользователя на сервере [`ban {пользователь} {причина}]
@client.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, arg, *, reason):
    await ctx.channel.purge(limit=1)

    emb_t = discord.Embed(title='Функция "ban" временно недоступна!', color=discord.Color.red())
    await ctx.send(embed=emb_t)


"""
    # сообщение которое будет отправлено в случае бана:
    # на сервер(в чат где была написана комманда)
    emb_s = discord.Embed(title='Был(а) заблокирован(a) на сервере', color=discord.Color.red())
    emb_s.set_author(name=member.name, icon_url=member.avatar_url)
    emb_s.add_field(name='Дата блокировки: {}'.format(datetime.datetime.now()),
                    value='Причина блокировки: {}.'.format(reason))
    emb_s.set_footer(text='Администратор: {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)

    # пользователю в лс
    emb_m = discord.Embed(title='Вы были заблокированы на сервере: {}'.format(ctx.guild), color=discord.Color.red())
    emb_m.add_field(name='Дата блокировки: {}'.format(datetime.datetime.now()),
                    value='Причина блокировки: {}.'.format(reason))
    emb_m.set_footer(text='Администратор: {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)

    # сообщение которое будет отправлено при попытке самобана
    emb_self_ban = discord.Embed(title='Невозможно заблокировать самого себя', color=discord.Color.purple())
    emb_self_ban.set_author(name=member.name, icon_url=member.avatar_url)

    if ctx.author != member:

        if arg == 'perm':
            print('[SUCCESS] User1 {} has been baned by {}'.format(member, ctx.author))
            await member.ban(reason=reason)
            await ctx.send(embed=emb_s)
            await member.send(embed=emb_m)
            print('[SUCCESS] User {} has been baned by {}'.format(member, ctx.author))
        else:
            emb_m = discord.Embed(title='Вы были временно заблокированы на сервере {},\
            срок блокировки {} мин'.format(ctx.guild, arg), color=discord.Color.red())
            emb_m.add_field(name='Дата блокировки: {}'.format(datetime.datetime.now()),
                            value='Причина блокировкии =>: {}.'.format(reason))
            emb_m.set_footer(text='Администратор: {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)

            await member.ban(reason=reason)
            await ctx.send(embed=emb_s)
            await member.send(embed=emb_m)
            isban = True
            print('[SUCCESS] User {} has been baned by {}, term: {} min'.format(member, ctx.author, arg))
            
            if isban == True:
                for i in range(int(arg), 0, -1):
                    await asyncio.sleep(1)
                    await ctx.send('sleep')
                isban = False
                
            if isban == False:

                # сообщение отправляемое на сервер
                emb_s = discord.Embed(title='Был(а) разблокирован(a) на сервере', color=discord.Color.green())
                emb_s.set_author(name=member.name, icon_url=member.avatar_url)

                # сообщение отправляемое пользователю
                emb_m = discord.Embed(title='Вы были разблокированны на сервере {}'.format(ctx.guild),
                                      color=discord.Color.green())

                await ctx.guild.unban(member)
                await ctx.send(embed=emb_s)
                await member.send(embed=emb_m)

                print('[SUCCESS] User {} has been unbaned'.format(member))

    else:
        await ctx.send(embed=emb_self_ban)
        print('[ERROR] {} try ban himself'.format(ctx.author))
"""


# Разбан пользователя на сервере [`unban {пользователь}]
@client.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
    await ctx.channel.purge(limit=1)
    banned_users = await ctx.guild.bans()
    for ban_entry in banned_users:
        user = ban_entry.user

        # сообщение отправляемое на сервер (в чат где была написана комманда)
        emb_s = discord.Embed(title='Был(а) разблокирован(a) на сервере', color=discord.Color.green())
        emb_s.set_author(name=user.name, icon_url=user.avatar_url)
        emb_s.set_footer(text='Администратором: {}'.format(ctx.author.name),
                         icon_url=ctx.author.avatar_url)

        # сообщение отправляемое пользователю
        emb_m = discord.Embed(title='Вы были разблокированны на сервере {}'.format(ctx.guild),
                              color=discord.Color.green())
        emb_m.set_footer(text='Администратором: {}'.format(ctx.author.name),
                         icon_url=ctx.author.avatar_url)

        await ctx.guild.unban(user)
        await ctx.send(embed=emb_s)
        await user.send(embed=emb_m)
        print('[SUCCESS] User {} has been unbaned by {}'.format(member, ctx.author))
        return


# Запрещает пользователю писать в чат [`mute {пользователь} {причина}]
@client.command()
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member, arg, *, reason):
    await ctx.channel.purge(limit=1)

    emb = discord.Embed(title='Отправляется в мут', color=discord.Color.magenta())
    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.add_field(name='Начало мута: {}'.format(datetime.datetime.now()),
                  value='Причина мута: {}.'.format(reason))
    emb.set_footer(text='Администратор: {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)

    mute_role = discord.utils.get(ctx.message.guild.roles, name='Mute')

    emb_unmute = discord.Embed(title='Убран из мута', color=discord.Color.green())
    emb_unmute.set_author(name=member.name, icon_url=member.avatar_url)
    emb_unmute.set_footer(text='Время вышло!', icon_url=ctx.author.avatar_url)

    if arg == 'perm':
        await member.add_roles(mute_role)
        await ctx.send(embed=emb)

    else:
        await member.add_roles(mute_role)
        await ctx.send(embed=emb)

        for i in range(int(arg), 0, -1):
            await asyncio.sleep(10)
        await member.remove_roles(mute_role)
        await ctx.send(embed=emb_unmute)


# Возврщает возможность писать в чат [`unmute {пользователь}]
@client.command()
@commands.has_permissions(administrator=True)
async def unmute(ctx, member: discord.Member):
    await ctx.channel.purge(limit=1)
    emb = discord.Embed(title='Убран из мута', color=discord.Color.green())
    emb.set_author(name=member.name, icon_url=member.avatar_url)

    emb.set_footer(text='Администратор: {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)

    mute_role = discord.utils.get(ctx.message.guild.roles, name='Mute')

    await member.remove_roles(mute_role)
    await ctx.send(embed=emb)


# добавляет роль пользователю [`g_role {пользователь}]
@client.command()
@commands.has_permissions(administrator=True)
async def g_role(ctx, member: discord.Member, *, reason=None):
    await ctx.channel.purge(limit=1)

    emb = discord.Embed(title='Дана роль: {}'.format(reason), color=discord.Color.magenta())
    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.set_footer(text='Администратор: {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)

    role_id = discord.utils.get(ctx.message.guild.roles, name=reason)
    await member.add_roles(role_id)
    await ctx.send(embed=emb)
    print('[SUCCESS] User {} has been got role: {}'.format(member, reason))


# снимает роль у пользователя [`g_role {пользователь}]
@client.command()
@commands.has_permissions(administrator=True)
async def r_role(ctx, member: discord.Member, *, reason=None):
    await ctx.channel.purge(limit=1)

    emb = discord.Embed(title='Убрана роль: {}'.format(reason), color=discord.Color.red())
    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.set_footer(text='Администратор: {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)

    role_id = discord.utils.get(ctx.message.guild.roles, name=reason)
    await member.remove_roles(role_id)
    await ctx.send(embed=emb)


@client.command()
@commands.has_permissions(administrator=True)
async def BAN(ctx, member: discord.Member):
    await ctx.channel.purge(limit=1)

    emb_s = discord.Embed(title='Не ну это БАН!!!!', color=discord.Color.red())
    emb_s.set_author(name=member.name, icon_url=member.avatar_url)

    await ctx.send(embed=emb_s)


@client.command()
async def mmm(ctx):
    sexy_gif = Gifs.r_gif()
    emb = discord.Embed(title=None, color=discord.Color.magenta())
    emb.set_image(url=sexy_gif)
    await ctx.send(embed=emb)


@client.command()
async def random(ctx, arg_1, arg_2):
    choice = def_random.random_num(int(arg_1), int(arg_2))
    await ctx.send(choice)


@client.command()
async def coin(ctx):
    choice = def_random.random_num(0, 1)

    if choice == 0:
        await ctx.send('Решка')
    else:
        await ctx.send('Орел')


# --------------------------------------------------------------------------------------------------------------------
#   приветствие нового пользователя (в лс)
@client.event
async def on_member_join(member):
    guild = client.get_guild(340794764251365376)
    to_send = 'Привет {0.mention}, добро пожаловать на сервер {1.name}!\n \
Чтобы узнать мои команды пропиши `help на сервере {1.name}'.format(member, guild)
    await member.send(to_send)


@client.event
async def on_member_update(before, after):
    guild = client.get_guild(340794764251365376)
    members_count_channel_1 = client.get_channel(731381229349502976)
    new_name = 'Members: ' + str(guild.member_count)
    await members_count_channel_1.edit(name=new_name)

    Online_m = '🟢 ' + str(
        sum([0 if member.status == discord.Status.offline else 1 for member in after.guild.members]) -
        sum([1 if member.status == discord.Status.idle else 0 for member in after.guild.members]) -
        sum([1 if member.status == discord.Status.dnd else 0 for member in after.guild.members])
    )
    Idle_m = ' 🌙 ' + str(
        sum([1 if member.status == discord.Status.idle else 0 for member in after.guild.members])
    )
    Dnd_m = ' 🔴 ' + str(
        sum([1 if member.status == discord.Status.dnd else 0 for member in after.guild.members])
    )

    members_online_channel = client.get_channel(751655191232905266)
    await members_online_channel.edit(name=Online_m + Idle_m + Dnd_m)

    now = datetime.datetime.now()
    Data_channel = client.get_channel(751659231823921162)
    await Data_channel.edit(name='📅' + str(now.strftime("%d-%m-%Y")))
    
    Data_channel_2 = client.get_channel(731773383519502356)
    await Data_channel_2.edit(name='⏲️' + str(now.strftime("%H-%M-%S")))
    print('⏲️' + str(now.strftime("%H-%M-%S")))
    
    await asyncio.sleep(429)
    


# ---------------------------------------------------------------------------------------------------------------------
# Errors


@mute.error
async def mute_err(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        emb = discord.Embed(title='Ошибка при попытке мута', color=discord.Color.red())
        emb.add_field(name='Причина:', value='Невведен срок мута или причина')
        await ctx.send(embed=emb)


@ban.error
async def ban_err(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        emb = discord.Embed(title='Ошибка при попытке бана', color=discord.Color.red())
        emb.add_field(name='Причина:', value='Невведен срок или причина')
        await ctx.send(embed=emb)


@g_role.error
async def g_role_err(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        emb = discord.Embed(title='Ошибка при попытке выдачи роли', color=discord.Color.red())
        emb.add_field(name='Причина:', value='Роль не существует')
        await ctx.send(embed=emb)


@r_role.error
async def r_role_err(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        emb = discord.Embed(title='Ошибка при попытке выдачи роли', color=discord.Color.red())
        emb.add_field(name='Причина:', value='Роль не существует')
        await ctx.send(embed=emb)


# ---------------------------------------------------------------------------------------------------------------------

client.run(str(TOKEN))

