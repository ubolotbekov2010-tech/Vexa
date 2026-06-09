import discord
from discord.ext import commands
from discord import app_commands
from discord.ext import tasks
import asyncio
import datetime
import json
import os
import random
import time
from dotenv import load_dotenv

load_dotenv()


GUILD_ID = 1488295467619061922

BUSINESS_LEVELS = {
    1: {"cost": 100000, "profit": 500},
    2: {"cost": 250000, "profit": 750},
    3: {"cost": 750000, "profit": 1000}
}

BUSINESS_PRICES = {
    1: 100000,
    2: 250000,
    3: 750000
}

PROFIT_PER_HOUR = {
    1: 5000,
    2: 15000,
    3: 50000
}

class Client(commands.Bot):
    async def on_message(self, message):
        if message.author == self.user:
            return
            
        if message.content.startswith('hello'):
            await message.channel.send(f'Hi there {message.author}')


    async def on_reaction_add(self, reaction, user):
        await reaction.message.channel.send('Да')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)

from discord.ext import tasks

@tasks.loop(hours=24)
async def payout_loop():
    print("Выплата запущена!")


GUILD_ID = discord.Object(id=1488295467619061922)




@client.tree.command(name="hello", description="Скажи здарова")
async def sayhello(interaction: discord.Interaction):
    await interaction.response.send_message("Здарова лохи")
    
@client.tree.command(name="printer", description="пишу")
async def printer(interaction: discord.Interaction, printer: str):
    await interaction.response.send_message(printer)
    
@client.tree.command(name="mute", description="Выдать мут пользователю")
@app_commands.default_permissions(moderate_members=True)
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.choices(unit=[
    app_commands.Choice(name="Секунды (с)", value="s"),
    app_commands.Choice(name="Минуты (м)", value="m"),
    app_commands.Choice(name="Часы (ч)", value="h"),
    app_commands.Choice(name="Дни (д)", value="d")
])
async def mute(interaction: discord.Interaction, member: discord.Member, time: int, unit: str, reason: str):
    try:
        
        if interaction.user.top_role <= member.top_role and interaction.guild.owner_id != interaction.user.id:
            await interaction.response.send_message("❌ Вы не можете замутить участника с ролью выше или равной вашей!", ephemeral=True)
            return

        
        seconds = 0
        unit_text = ""
        if unit == "s":
            seconds = time
            unit_text = "сек."
        elif unit == "m":
            seconds = time * 60
            unit_text = "мин."
        elif unit == "h":
            seconds = time * 3600
            unit_text = "час."
        elif unit == "d":
            seconds = time * 86400
            unit_text = "дн."

        import datetime
        duration = datetime.timedelta(seconds=seconds)
        
         
        await member.timeout(duration, reason=reason)

         
        emb = discord.Embed(title=f"⏳ Участнику выдан мут на {time} {unit_text}", color=discord.Color.orange())
        emb.add_field(name="Модератор", value=interaction.user.mention)
        emb.add_field(name="Нарушитель", value=member.mention)
        emb.add_field(name="Причина", value=reason, inline=False)
        
        await interaction.response.send_message(embed=emb)

    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка при выдаче мута: {e}", ephemeral=True)
  
@client.tree.command(name="ban", description="Забанить пользователя")
@app_commands.default_permissions(ban_members=True)
@app_commands.checks.has_permissions(ban_members=True)
@app_commands.choices(unit=[
    app_commands.Choice(name="Минуты", value="m"),
    app_commands.Choice(name="Часы", value="h"),
    app_commands.Choice(name="Дни", value="d")
])
async def ban(it: discord.Interaction, m: discord.Member, time: int = None, unit: str = None, r: str = "Не указана"):
    try:
        if it.user.top_role <= m.top_role and it.guild.owner_id != it.user.id:
            await it.response.send_message("❌ У игрока роль выше или равна вашей!", ephemeral=True)
            return
        u = await client.fetch_user(m.id)
        sec, txt = 0, ""
        if time and unit:
            if unit == "m": sec, txt = time * 60, "мин."
            elif unit == "h": sec, txt = time * 3600, "час."
            elif unit == "d": sec, txt = time * 86400, "дн."
            await m.ban(reason=f"Бан на {time} {txt}. Причина: {r}")
            tit = f"⏳ Выдан временный бан на {time} {txt}"
        else:
            await m.ban(reason=f"Бан навсегда. Причина: {r}")
            tit = "🔨 Участник забанен навсегда"
        emb = discord.Embed(title=tit, color=discord.Color.red())
        emb.add_field(name="Модератор", value=it.user.mention)
        emb.add_field(name="Нарушитель", value=u.mention)
        emb.add_field(name="Причина", value=r, inline=False)
        emb.timestamp = datetime.datetime.now()
        await it.response.send_message(embed=emb)
        if sec > 0:
            await asyncio.sleep(sec)
            try:
                await it.guild.unban(u, reason="Время бана истекло")
                un = discord.Embed(title="🕊️ Время бана истекло", description=f"{u.mention} разбанен.", color=discord.Color.green())
                await it.channel.send(embed=un)
            except discord.NotFound: pass
    except Exception as e:
        await it.response.send_message(f"❌ Ошибка: {e}", ephemeral=True)
        
@client.tree.command(name="kick", description="Кикнуть пользователя с сервера")
@app_commands.default_permissions(kick_members=True)
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str):
    try:
        if interaction.user.top_role <= member.top_role and interaction.guild.owner_id != interaction.user.id:
            await interaction.response.send_message("❌ Вы не можете кикнуть участника с ролью выше или равной вашей!", ephemeral=True)
            return

        await member.kick(reason=reason)

        emb = discord.Embed(title="👢 Участник кикнут с сервера", color=discord.Color.red())
        emb.add_field(name="Модератор", value=interaction.user.mention)
        emb.add_field(name="Нарушитель", value=member.mention)
        emb.add_field(name="Причина", value=reason, inline=False)
        
        await interaction.response.send_message(embed=emb)
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка при кике: {e}", ephemeral=True)

@client.tree.command(name="clear", description="Очистить чат")
@app_commands.checks.has_any_role("Project Leaders", "Staff Manager", "Curator", "Main Administrator", "Administrator", "Moderator")
async def clear(interaction: discord.Interaction, amount: int):
    if amount < 1:
        await interaction.response.send_message("Укажите число больше 0", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    
    deleted = await interaction.channel.purge(limit=amount)
    
    await interaction.followup.send(f"Успешно удалено {len(deleted)} сообщений", ephemeral=True)

@clear.error
async def clear_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message("У вас нет прав для использования этой команды", ephemeral=True)
    elif isinstance(error, app_commands.CommandInvokeError):
        await interaction.response.send_message("У меня нет прав на управление сообщениями. Проверьте настройки канала/бота", ephemeral=True)

@client.tree.command(name="unban", description="Разбанить пользователя по ID")
@app_commands.default_permissions(ban_members=True)
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user: discord.User, reason: str):
    try:
        await interaction.guild.unban(user, reason=reason)

        emb = discord.Embed(title="🤝 Пользователь успешно разбанен", color=discord.Color.green())
        emb.add_field(name="Модератор", value=interaction.user.mention)
        emb.add_field(name="Пользователь", value=user.mention)
        emb.add_field(name="Причина разбана", value=reason, inline=False)
        
        await interaction.response.send_message(embed=emb)
    except discord.NotFound:
        await interaction.response.send_message("❌ Этот пользователь не найден в списке банов сервера!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка при разбане: {e}", ephemeral=True)

@client.tree.command(name="unmute", description="Снять мут (тайм-аут) с пользователя")
@app_commands.default_permissions(moderate_members=True)
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member, reason: str):
    try:
        await member.timeout(None, reason=reason)

        emb = discord.Embed(title="🔊 С участника снят мут", color=discord.Color.green())
        emb.add_field(name="Модератор", value=interaction.user.mention)
        emb.add_field(name="Участник", value=member.mention)
        emb.add_field(name="Причина снятия", value=reason, inline=False)
        
        await interaction.response.send_message(embed=emb)
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка при размуте: {e}", ephemeral=True)

@client.tree.command(name="warn", description="Выдать предупреждение пользователю")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    allowed = ["Owner", "Co-Owner", "Curator"]
    if not any(r.name in allowed for r in interaction.user.roles):
        await interaction.response.send_message("❌ Эту команду может использовать только высшая администрация!", ephemeral=True)
        return

    warns_data = {}
    if os.path.exists("warns.json"):
        with open("warns.json", "r") as f:
            warns_data = json.load(f)

    guild_id = str(interaction.guild.id)
    user_id = str(member.id)

    if guild_id not in warns_data:
        warns_data[guild_id] = {}

    current_warns = warns_data[guild_id].get(user_id, 0) + 1
    warns_data[guild_id][user_id] = current_warns

    with open("warns.json", "w") as f:
        json.dump(warns_data, f, indent=4)

    if current_warns >= 3:
        warns_data[guild_id][user_id] = 0
        with open("warns.json", "w") as f:
            json.dump(warns_data, f, indent=4)

        staff_names = ["Main Administrator", "Administrator", "Moderator", "Main Support", "Advanced Support", "Support"]
        roles_to_remove = [r for r in member.roles if r.name in staff_names]

        if roles_to_remove:
            try:
                await member.remove_roles(*roles_to_remove)
                emb = discord.Embed(title="📉 Снятие с должности", color=discord.Color.orange())
                emb.add_field(name="Администратор", value=interaction.user.mention)
                emb.add_field(name="Нарушитель", value=member.mention)
                emb.add_field(name="Решение", value="Снят со всех должностей за 3/3 варна")
                emb.add_field(name="Последняя причина", value=reason, inline=False)
                await interaction.response.send_message(embed=emb)
            except Exception as e:
                await interaction.response.send_message(f"❌ Не удалось снять роли: {e}", ephemeral=True)
        else:
            try:
                await interaction.guild.ban(member, reason="3/3 предупреждений")
                emb = discord.Embed(title="🔨 Автоматический бан", color=discord.Color.red())
                emb.add_field(name="Администратор", value=interaction.user.mention)
                emb.add_field(name="Нарушитель", value=member.mention)
                emb.add_field(name="Причина", value="Получение 3/3 предупреждений")
                emb.add_field(name="Последняя причина", value=reason, inline=False)
                await interaction.response.send_message(embed=emb)
            except Exception as e:
                await interaction.response.send_message(f"❌ Не удалось забанить пользователя: {e}", ephemeral=True)
    else:
        emb = discord.Embed(title="⚠️ Выдано предупреждение", color=discord.Color.yellow())
        emb.add_field(name="Администратор", value=interaction.user.mention)
        emb.add_field(name="Нарушитель", value=member.mention)
        emb.add_field(name="Причина", value=reason)
        emb.add_field(name="Предупреждения", value=f"`{current_warns}/3`", inline=False)
        await interaction.response.send_message(embed=emb)

@client.tree.command(name="unwarn", description="Снять одно предупреждение с пользователя")
async def unwarn(interaction: discord.Interaction, member: discord.Member, reason: str):
    allowed = ["Owner", "Co-Owner", "Curator"]
    if not any(r.name in allowed for r in interaction.user.roles):
        await interaction.response.send_message("❌ Эту команду может использовать только высшая администрация!", ephemeral=True)
        return

    warns_data = {}
    if os.path.exists("warns.json"):
        with open("warns.json", "r") as f:
            warns_data = json.load(f)

    guild_id = str(interaction.guild.id)
    user_id = str(member.id)

    current_warns = warns_data.get(guild_id, {}).get(user_id, 0)

    if current_warns == 0:
        await interaction.response.send_message(f"❌ У пользователя {member.mention} нет активных предупреждений!", ephemeral=True)
        return

    new_warns = current_warns - 1
    warns_data[guild_id][user_id] = new_warns

    with open("warns.json", "w") as f:
        json.dump(warns_data, f, indent=4)

    emb = discord.Embed(title="✅ Снято предупреждение", color=discord.Color.green())
    emb.add_field(name="Администратор", value=interaction.user.mention)
    emb.add_field(name="Нарушитель", value=member.mention)
    emb.add_field(name="Причина снятия", value=reason)
    emb.add_field(name="Предупреждения", value=f"`{new_warns}/3`", inline=False)
    await interaction.response.send_message(embed=emb)
    
@client.tree.command(name="warn_list", description="Показать список всех варнов")
@app_commands.checks.has_permissions(administrator=True)
async def warn_list(interaction: discord.Interaction):
    gid = str(interaction.guild_id)
    
    with open("warns.json", "r") as f:
        data = json.load(f)
    
    if gid not in data or not data[gid]:
        await interaction.response.send_message("Варнов пока нет.", ephemeral=True)
        return

    embed = discord.Embed(title="Список предупреждений", color=discord.Color.red())
    
    found = False
    for uid, count in data[gid].items():
        if count > 0:
            member = interaction.guild.get_member(int(uid))
            name = member.display_name if member else f"Пользователь {uid}"
            embed.add_field(name=name, value=f"Предупреждений: {count}", inline=False)
            found = True
    
    if not found:
        await interaction.response.send_message("Варнов пока нет.", ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed)

@warn_list.error
async def warn_list_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("У вас нет прав администратора для использования этой команды!", ephemeral=True)

@client.tree.command(name="balance", description="Ваш баланс")
async def balance(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)

    if not os.path.exists("economy.json"):
        await interaction.response.send_message("База данных пуста", ephemeral=True)
        return

    with open("economy.json", "r") as f:
        data = json.load(f)

    user_data = data.get(guild_id, {}).get(user_id, {})
    
    cash = user_data.get("balance", 0)
    bank = user_data.get("bank", 0)
    total = cash + bank

    embed = discord.Embed(title=f"Баланс {interaction.user.display_name}", color=discord.Color.green())
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    embed.add_field(name="Кошелек", value=f"{cash:,}$", inline=False)
    embed.add_field(name="Банковский счет", value=f"{bank:,}$", inline=False)
    embed.add_field(name="Итого", value=f"{total:,}$", inline=False)

    await interaction.response.send_message(embed=embed)
    
@client.tree.command(name="deposit", description="Положить деньги в банк")
async def deposit(interaction: discord.Interaction, amount: str):
    guild_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)
    with open("economy.json", "r") as f:
        data = json.load(f)
    if guild_id not in data or user_id not in data[guild_id]:
        await interaction.response.send_message("У вас нет аккаунта")
        return
    cash = data[guild_id][user_id].get("balance", 0)
    bank = data[guild_id][user_id].get("bank", 0)
    if amount.lower() == "all":
        to_deposit = cash
    else:
        try:
            to_deposit = int(amount)
        except:
            await interaction.response.send_message("Введите число или all")
            return
    if to_deposit > cash:
        await interaction.response.send_message("Недостаточно денег")
        return
    if to_deposit <= 0:
        await interaction.response.send_message("Сумма должна быть больше 0")
        return
    data[guild_id][user_id]["balance"] = cash - to_deposit
    data[guild_id][user_id]["bank"] = bank + to_deposit
    with open("economy.json", "w") as f:
        json.dump(data, f, indent=4)
    cash = data[guild_id][user_id]["balance"]
    bank = data[guild_id][user_id]["bank"]
    total = cash + bank
    embed = discord.Embed(title=f"Баланс {interaction.user.display_name}", color=discord.Color.green())
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="Кошелек", value=f"{cash:,}$", inline=False)
    embed.add_field(name="Банковский счет", value=f"{bank:,}$", inline=False)
    embed.add_field(name="Итого", value=f"{total:,}$", inline=False)
    await interaction.response.send_message(content=f"Вы внесли {to_deposit:,}$", embed=embed)

@client.tree.command(name="withdraw", description="Снять деньги с банка (Сумма или all)")
async def withdraw(interaction: discord.Interaction, amount: str):
    guild_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)
    with open("economy.json", "r") as f:
        data = json.load(f)
    if guild_id not in data or user_id not in data[guild_id]:
        await interaction.response.send_message("У вас нет аккаунта")
        return
    cash = data[guild_id][user_id].get("balance", 0)
    bank = data[guild_id][user_id].get("bank", 0)
    if amount.lower() == "all":
        to_withdraw = bank
    else:
        try:
            to_withdraw = int(amount)
        except:
            await interaction.response.send_message("Введите число или all")
            return
    if to_withdraw > bank:
        await interaction.response.send_message("Недостаточно денег в банке")
        return
    if to_withdraw <= 0:
        await interaction.response.send_message("Сумма должна быть больше 0")
        return
    data[guild_id][user_id]["bank"] = bank - to_withdraw
    data[guild_id][user_id]["balance"] = cash + to_withdraw
    with open("economy.json", "w") as f:
        json.dump(data, f, indent=4)
    cash = data[guild_id][user_id]["balance"]
    bank = data[guild_id][user_id]["bank"]
    total = cash + bank
    embed = discord.Embed(title=f"Баланс {interaction.user.display_name}", color=discord.Color.green())
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="Кошелек", value=f"{cash:,}$", inline=False)
    embed.add_field(name="Банковский счет", value=f"{bank:,}$", inline=False)
    embed.add_field(name="Итого", value=f"{total:,}$", inline=False)
    await interaction.response.send_message(content=f"Вы сняли {to_withdraw:,}$", embed=embed)

@client.tree.command(name="leaderboard", description="Показать лидеров сервера по кристаликсам")
async def leaderboard(interaction: discord.Interaction):
    economy_data = {}
    if os.path.exists("economy.json"):
        with open("economy.json", "r") as f:
            economy_data = json.load(f)

    guild_id = str(interaction.guild.id)
    server_data = economy_data.get(guild_id, {})

    sorted_users = sorted(server_data.items(), key=lambda item: item[1].get("balance", 0), reverse=True)[:10]

    if not sorted_users:
        await interaction.response.send_message("❌ Таблица лидеров пуста!", ephemeral=True)
        return

    def format_money(amount):
        if amount >= 1000000000:
            return f"{amount / 1000000000:.2f}B"
        elif amount >= 1000000:
            return f"{amount / 1000000:.2f}M"
        elif amount >= 1000:
            return f"{amount / 1000:.2f}K"
        return str(amount)

    user_lines = []
    for index, (user_id, data) in enumerate(sorted_users, start=1):
        member = interaction.guild.get_member(int(user_id))
        name = member.mention if member else f"<@{user_id}>"
        bal = data.get("balance", 0)
        user_lines.append(f"🏅 **{index}.** {name}\n💵 **{format_money(bal)} :red_crystal:**")

    emb = discord.Embed(
        title="🧳 Лидеры: Общий Капитал | Страница 1",
        description="\n\n".join(user_lines),
        color=discord.Color.blue()
    )

    if interaction.guild.icon:
        emb.set_thumbnail(url=interaction.guild.icon.url)

    await interaction.response.send_message(embed=emb)

@client.tree.command(name="weekly", description="Получить еженедельную награду")
async def weekly(interaction: discord.Interaction):
    economy_data = {}
    if os.path.exists("economy.json"):
        with open("economy.json", "r") as f:
            economy_data = json.load(f)

    guild_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)

    if guild_id not in economy_data:
        economy_data[guild_id] = {}
    if user_id not in economy_data[guild_id]:
        economy_data[guild_id][user_id] = {"balance": 0, "last_daily": 0, "last_weekly": 0, "last_work": 0, "last_training": 0, "streak": 0}

    user_data = economy_data[guild_id][user_id]
    current_time = int(time.time())
    cooldown = 604800

    if current_time - user_data.get("last_weekly", 0) < cooldown:
        remains = cooldown - (current_time - user_data.get("last_weekly", 0))
        days = remains // 86400
        hours = (remains % 86400) // 3600
        await interaction.response.send_message(f"❌ Награда будет доступна через `{days}д {hours}ч`", ephemeral=True)
        return

    user_data["balance"] += 25000
    user_data["last_weekly"] = current_time

    with open("economy.json", "w") as f:
        json.dump(economy_data, f, indent=4)

    emb = discord.Embed(
        title="🎁 Еженедельный бонус",
        description=(
            f"Поздравляем! **{interaction.user.display_name}** получил(а) бонус в размере **25,000**!\n\n"
            f"**Следующий еженедельный бонус будет доступен:**\n`через неделю`"
        ),
        color=discord.Color.blue(),
        timestamp=interaction.created_at
    )
    
    if interaction.user.avatar:
        emb.set_thumbnail(url=interaction.user.avatar.url)
        
    guild_icon = interaction.guild.icon.url if interaction.guild.icon else None
    emb.set_footer(text=interaction.guild.name, icon_url=guild_icon)

    await interaction.response.send_message(embed=emb)

@client.tree.command(name="daily", description="Получить ежедневную награду")
async def daily(interaction: discord.Interaction):
    economy_data = {}
    if os.path.exists("economy.json"):
        with open("economy.json", "r") as f:
            economy_data = json.load(f)

    guild_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)

    if guild_id not in economy_data:
        economy_data[guild_id] = {}
    if user_id not in economy_data[guild_id]:
        economy_data[guild_id][user_id] = {"balance": 0, "last_daily": 0, "last_weekly": 0, "last_work": 0, "last_training": 0, "streak": 0}

    user_data = economy_data[guild_id][user_id]
    current_time = int(time.time())
    cooldown = 86400
    last_daily = user_data.get("last_daily", 0)

    if current_time - last_daily < cooldown:
        remains = cooldown - (current_time - last_daily)
        hours = remains // 3600
        minutes = (remains % 3600) // 60
        await interaction.response.send_message(f"❌ Награда будет доступна через `{hours}ч {minutes}м`", ephemeral=True)
        return

    streak = user_data.get("streak", 0)
    if current_time - last_daily < 172800:
        streak += 1
    else:
        streak = 1

    user_data["balance"] += 5000
    user_data["last_daily"] = current_time
    user_data["streak"] = streak

    with open("economy.json", "w") as f:
        json.dump(economy_data, f, indent=4)

    emb = discord.Embed(
        title="🎁 Ежедневный бонус",
        description=(
            f"Поздравляем! **{interaction.user.display_name}** получил(а) бонус в размере **5,000**!\n\n"
            f"**Текущий стрик: {streak} 🔥**\n\n"
            f"**Следующий ежедневный бонус будет доступен:**\n`через день`"
        ),
        color=discord.Color.green(),
        timestamp=interaction.created_at
    )
    
    if interaction.user.avatar:
        emb.set_thumbnail(url=interaction.user.avatar.url)
    guild_icon = interaction.guild.icon.url if interaction.guild.icon else None
    emb.set_footer(text=interaction.guild.name, icon_url=guild_icon)

    await interaction.response.send_message(embed=emb)

@client.tree.command(name="work", description="Устроиться на подработку")
async def work(interaction: discord.Interaction):
    economy_data = {}
    if os.path.exists("economy.json"):
        with open("economy.json", "r") as f:
            economy_data = json.load(f)

    guild_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)

    if guild_id not in economy_data:
        economy_data[guild_id] = {}
    if user_id not in economy_data[guild_id]:
        economy_data[guild_id][user_id] = {"balance": 0, "last_daily": 0, "last_weekly": 0, "last_work": 0, "last_training": 0}

    user_data = economy_data[guild_id][user_id]
    current_time = int(time.time())
    cooldown = 1800

    if current_time - user_data.get("last_work", 0) < cooldown:
        remains = cooldown - (current_time - user_data.get("last_work", 0))
        minutes = remains // 60
        seconds = remains % 60
        await interaction.response.send_message(f"❌ Вы устали! Отдохните ещё `{minutes}м {seconds}с`", ephemeral=True)
        return

    earned = random.randint(50, 100)
    user_data["balance"] += earned
    user_data["last_work"] = current_time

    with open("economy.json", "w") as f:
        json.dump(economy_data, f, indent=4)

    emb = discord.Embed(title="💼 Работа", description=f"Вы успешно поработали и получили `{earned}` 💎 кристаликсов!", color=discord.Color.blue())
    await interaction.response.send_message(embed=emb)

@client.tree.command(name="pay", description="Перевести кристаликсы другому пользователю")
async def pay(interaction: discord.Interaction, member: discord.Member, amount: int):
    if member == interaction.user:
        await interaction.response.send_message("❌ Нельзя перевести кристаликсы самому себе!", ephemeral=True)
        return

    if amount <= 0:
        await interaction.response.send_message("❌ Сумма должна быть больше 0!", ephemeral=True)
        return

    if amount > 1000000000:
        await interaction.response.send_message("❌ Максимальная сумма перевода — 1,000,000,000 кристаликсов!", ephemeral=True)
        return

    economy_data = {}
    if os.path.exists("economy.json"):
        with open("economy.json", "r") as f:
            economy_data = json.load(f)

    guild_id = str(interaction.guild.id)
    sender_id = str(interaction.user.id)
    receiver_id = str(member.id)

    if guild_id not in economy_data:
        economy_data[guild_id] = {}
    
    if sender_id not in economy_data[guild_id]:
        economy_data[guild_id][sender_id] = {"balance": 0, "last_daily": 0, "last_weekly": 0, "last_work": 0, "last_training": 0, "streak": 0}
    
    if receiver_id not in economy_data[guild_id]:
        economy_data[guild_id][receiver_id] = {"balance": 0, "last_daily": 0, "last_weekly": 0, "last_work": 0, "last_training": 0, "streak": 0}

    if economy_data[guild_id][sender_id]["balance"] < amount:
        await interaction.response.send_message("❌ У вас недостаточно кристаликсов для этого перевода!", ephemeral=True)
        return

    economy_data[guild_id][sender_id]["balance"] -= amount
    economy_data[guild_id][receiver_id]["balance"] += amount

    with open("economy.json", "w") as f:
        json.dump(economy_data, f, indent=4)
    
    emb = discord.Embed(
        title="💸 Перевод средств",
        description=f"**{interaction.user.mention}** перевел(а) **{amount:,} :red_crystal:** пользователю **{member.mention}**!",
        color=discord.Color.green()
    )
    
    await interaction.response.send_message(embed=emb)
    
user_cooldowns = {}

multipliers = {
    "🍒": 2,
    "🍋": 3,
    "🍊": 4,
    "🍇": 5,
    "🔔": 10
}

@client.command(name="slots")
async def slots(ctx, bet: int):
    await ctx.send(f"{ctx.author.mention} поставил {bet}")

    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    current_time = time.time()
    last_use = user_cooldowns.get(user_id, 0)

    if current_time - last_use < 20:
        await ctx.send(f"Подождите {int(20 - (current_time - last_use))} сек.")
        return

    if bet < 1000 or bet > 1000000000:
        await ctx.send("Ставка от 1000 до 1 000 000 000")
        return

    with open("economy.json", "r") as f:
        data = json.load(f)

    if guild_id not in data:
        data[guild_id] = {}
    if user_id not in data[guild_id]:
        data[guild_id][user_id] = {"balance": 0}

    cash = data[guild_id][user_id].get("balance", 0)

    if bet > cash:
        await ctx.send("Недостаточно средств")
        return

    user_cooldowns[user_id] = current_time

    outcome = random.choices(["lose", "partial", "jackpot"], weights=[56, 35, 9], k=1)[0]
    items = ["🍒", "🍋", "🍊", "🍇", "🔔"]
    multipliers = {"🍒": 2, "🍋": 3, "🍊": 4, "🍇": 5, "🔔": 10}
    
    if outcome == "lose":
        result = random.sample(items, 3)
        while result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
            result = random.sample(items, 3)
        win_delta = -bet
        msg = f"Проигрыш. Вы потеряли {bet:,}$"
    elif outcome == "partial":
        pair = random.choice(items)
        result = [pair, pair, random.choice([x for x in items if x != pair])]
        random.shuffle(result)
        win_delta = int(bet * 0.5)
        msg = f"Хорошо! Два совпадения, вы выиграли {int(bet * 1.5):,}$"
    else:
        sym = random.choice(items)
        result = [sym, sym, sym]
        mult = multipliers[sym]
        win_delta = bet * (mult - 1)
        msg = f"Джекпот! Вы выиграли {bet * mult:,}$ (x{mult})"
        
        role = discord.utils.get(ctx.guild.roles, name="Азартный Мастер")
        if role and role not in ctx.author.roles:
            if random.random() < random.uniform(0.005, 0.01):
                await ctx.author.add_roles(role)
                try:
                    await ctx.author.send(f"🎉 Поздравляю! Ты получил роль **Азартный Мастер** на сервере {ctx.guild.name}!")
                    msg += "\n🎲 Ты получил секретную роль Азартный Мастер! (проверь ЛС)"
                except:
                    msg += "\n🎲 Ты получил секретную роль Азартный Мастер!"

    data[guild_id][user_id]["balance"] = cash + win_delta

    with open("economy.json", "w") as f:
        json.dump(data, f, indent=4)

    embed = discord.Embed(title="Казино Слоты", color=discord.Color.gold())
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.add_field(name="Результат", value=f"{result[0]} {result[1]} {result[2]}", inline=False)
    embed.add_field(name="Итог", value=msg, inline=False)
    embed.add_field(name="Ваш баланс", value=f"{data[guild_id][user_id]['balance']:,}$", inline=False)

    await ctx.send(embed=embed)

def get_cards_str(hand):
    suits = ["♠", "♥", "♦", "♣"]
    cards = []
    for val in hand:
        suit = random.choice(suits)
        name = str(val)
        if val == 11: name = "J"
        if val == 12: name = "Q"
        if val == 13: name = "K"
        if val == 14: name = "A"
        cards.append(f"{name}{suit}")
    return " ".join(cards)

def calculate_score(hand):
    score = 0
    aces = 0
    for card in hand:
        if card > 10: val = 10
        elif card == 14: val = 11
        else: val = card
        score += val
        if card == 14: aces += 1
    while score > 21 and aces:
        score -= 10
        aces -= 1
    return score

class BlackjackView(discord.ui.View):
    def __init__(self, user, bet, gid, uid, data):
        super().__init__(timeout=60)
        self.user = user
        self.bet = bet
        self.gid = gid
        self.uid = uid
        self.data = data
        self.player_hand = [random.randint(2, 14), random.randint(2, 14)]
        self.dealer_hand = [random.randint(2, 14), random.randint(2, 14)]

async def end_game(self, interaction, result_text, win_status="loss"):
    p_score = calculate_score(self.player_hand)
    d_score = calculate_score(self.dealer_hand)
        
    embed = discord.Embed(title="БлекДжек", color=0x2f3136)
    embed.add_field(name="Ваши карты:", value=f"{get_cards_str(self.player_hand)} ({p_score})", inline=False)
    embed.add_field(name="Карты дилера:", value=f"{get_cards_str(self.dealer_hand)} ({d_score})", inline=False)
    embed.add_field(name="Итог", value=result_text, inline=False)
        
    if win_status == "win":
        self.data[self.gid][self.uid]["balance"] += self.bet * 2
    elif win_status == "draw":
        self.data[self.gid][self.uid]["balance"] += self.bet
        
    save_data(self.data)
    await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Взять", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player_hand.append(random.randint(2, 14))
        if calculate_score(self.player_hand) > 21:
            await self.end_game(interaction, f"Перебор! Вы потеряли {self.bet:,}$", win=False)
        else:
            p_score = calculate_score(self.player_hand)
            embed = discord.Embed(title="БлекДжек", color=0x2f3136)
            embed.add_field(name="Ваши карты:", value=f"{get_cards_str(self.player_hand)} ({p_score})", inline=False)
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Хватит", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        while calculate_score(self.dealer_hand) < 17:
            self.dealer_hand.append(random.randint(2, 14))
        
        p_score = calculate_score(self.player_hand)
        d_score = calculate_score(self.dealer_hand)
        
        if d_score > 21 or p_score > d_score:
            await self.end_game(interaction, f"Вы выиграли {self.bet:,}$!", win=True)
        elif p_score < d_score:
            await self.end_game(interaction, f"Вы проиграли {self.bet:,}$", win=False)
        else:
            await self.end_game(interaction, "Ничья! Деньги возвращены.", win=None)

@client.tree.command(name="blackjack", description="Сыграть в БлэкДжек")
async def blackjack(interaction: discord.Interaction, bet: int):
    gid, uid = str(interaction.guild_id), str(interaction.user.id)
    
    with open("economy.json", "r") as f:
        data = json.load(f)
    
    if gid not in data: data[gid] = {}
    if uid not in data[gid]: data[gid][uid] = {"balance": 0}
    
    balance = data[gid][uid].get("balance", 0)

    if bet < 1000 or bet > 1000000000:
        await interaction.response.send_message("Ставка от 1000 до 1 000 000 000", ephemeral=True)
        return

    if bet > balance:
        await interaction.response.send_message("Недостаточно средств", ephemeral=True)
        return
    
    data[gid][uid]["balance"] -= bet
    with open("economy.json", "w") as f:
        json.dump(data, f, indent=4)
    
    view = BlackjackView(interaction.user, bet, gid, uid)
    await interaction.response.send_message("Игра началась!", view=view)

crime_cooldowns = {}

@client.tree.command(name="crime", description="Ограбить пользователя")
async def crime(interaction: discord.Interaction, member: discord.Member):
    uid = str(interaction.user.id)
    gid = str(interaction.guild_id)
    current_time = time.time()

    if member == interaction.user:
        await interaction.response.send_message("Нельзя грабить самого себя", ephemeral=True)
        return

    if member.bot:
        await interaction.response.send_message("Нельзя грабить бота", ephemeral=True)
        return

    if uid in crime_cooldowns and current_time - crime_cooldowns[uid] < 3600:
        wait_time = int(3600 - (current_time - crime_cooldowns[uid]))
        minutes = wait_time // 60
        seconds = wait_time % 60
        await interaction.response.send_message(f"Кулдаун! Попробуйте через {minutes} мин. {seconds} сек.", ephemeral=True)
        return

    data = load_data()
    if gid not in data: data[gid] = {}
    if uid not in data[gid]: data[gid][uid] = {"balance": 0, "businesses": []}
    
    crime_cooldowns[uid] = current_time
    success = random.random() < 0.40
    amount = random.randint(1000, 2000)

    if success:
        data[gid][uid]["balance"] += amount
        message = f"Успешное ограбление! Вы украли {amount}$ у {member.mention}"
    else:
        data[gid][uid]["balance"] -= amount
        message = f"Вас поймали! Вы потеряли {amount}$"

    save_data(data)
    await interaction.response.send_message(message)

def decl(number, forms):
    cases = [2, 0, 1, 1, 1, 2]
    if 4 < number % 100 < 20:
        return forms[2]
    return forms[cases[min(number % 10, 5)]]

class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.participants = set()

    @discord.ui.button(label="Принять участие", style=discord.ButtonStyle.green, custom_id="join_giveaway")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.participants:
            await interaction.response.send_message("Вы уже участвуете!", ephemeral=True)
            return
        self.participants.add(interaction.user.id)
        await interaction.response.send_message("Вы успешно записались на розыгрыш!", ephemeral=True)

@client.tree.command(name="gstart", description="Создать розыгрыш (1d, 1h, 30m, 60s)")
@app_commands.checks.has_any_role("Project Leaders", "Main Administrator", "Administrator", "Master Eventer", "Eventer")
async def gstart(interaction: discord.Interaction, duration: str, winners: int, prize: str):
    total_seconds = 0
    time_text = ""

    try:
        if "d" in duration:
            days = int(duration.replace("d", ""))
            if days > 28:
                await interaction.response.send_message("Максимальная длительность — 28 дней!", ephemeral=True)
                return
            total_seconds = days * 86400
            time_text = f"{days} {decl(days, ('день', 'дня', 'дней'))}"
        elif "h" in duration:
            hours = int(duration.replace("h", ""))
            total_seconds = hours * 3600
            time_text = f"{hours} {decl(hours, ('час', 'часа', 'часов'))}"
        elif "m" in duration:
            minutes = int(duration.replace("m", ""))
            total_seconds = minutes * 60
            time_text = f"{minutes} {decl(minutes, ('минута', 'минуты', 'минут'))}"
        elif "s" in duration:
            seconds = int(duration.replace("s", ""))
            total_seconds = seconds
            time_text = f"{seconds} {decl(seconds, ('секунда', 'секунды', 'секунд'))}"
        else:
            minutes = int(duration)
            total_seconds = minutes * 60
            time_text = f"{minutes} {decl(minutes, ('минута', 'минуты', 'минут'))}"
    except ValueError:
        await interaction.response.send_message("Ошибка: укажи время правильно (например: 1d, 1h, 30m, 60)", ephemeral=True)
        return

    view = GiveawayView()
    embed = discord.Embed(
        title=f"🎉 {prize}",
        description=f"Нажмите на кнопку ниже, чтобы принять участие!\n\nОрганизатор: {interaction.user.mention}\nКоличество победителей: {winners}",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Розыгрыш закончится через {time_text}")
    
    await interaction.response.send_message(embed=embed, view=view)
    msg = await interaction.original_response()
    
    await asyncio.sleep(total_seconds)
    
    participants = list(view.participants)
    if len(participants) < winners:
        await msg.reply("Недостаточно участников для определения победителей!")
        return
        
    winners_list = random.sample(participants, winners)
    winners_mentions = ", ".join([f"<@{w_id}>" for w_id in winners_list])
    
    embed.title = f"Розыгрыш завершен: {prize}"
    embed.description = f"Организатор: {interaction.user.mention}\nУчастников: {len(participants)}\nПобедители: {winners_mentions}"
    embed.color = discord.Color.gold()
    embed.set_footer(text="Розыгрыш окончен")
    
    for child in view.children:
        child.disabled = True
        
    await msg.edit(embed=embed, view=view)

    if len(winners_list) == 1:
        await msg.reply(f"Поздравляем победителя: {winners_mentions}! Ты выиграл {prize}!")
    else:
        await msg.reply(f"Поздравляем победителей: {winners_mentions}! Вы выиграли {prize}!")

@gstart.error
async def gstart_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message("У вас нет прав для запуска розыгрыша!", ephemeral=True)

user_data = {}
voice_timers = {}

DATA_FILE = "death_note_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"users": {}, "cooldowns": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

storage = load_data()
user_data = storage["users"]
cooldowns = storage["cooldowns"]

class FactionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Кира", style=discord.ButtonStyle.danger, emoji="🍎", custom_id="faction_kira_button")
    async def kira(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_data[str(interaction.user.id)] = {"side": "kira", "messages": 0, "commands": 0, "voice": 0}
        await interaction.response.send_message("Ты примкнул к Кире!", ephemeral=True)

    @discord.ui.button(label="Детектив", style=discord.ButtonStyle.primary, emoji="🕵️", custom_id="faction_detective_button")
    async def detective(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_data[str(interaction.user.id)] = {"side": "detective", "messages": 0, "commands": 0, "voice": 0}
        await interaction.response.send_message("Ты стал на сторону Детективов!", ephemeral=True)

@client.event
async def on_message(message):
    if message.author.bot: return
    uid = str(message.author.id)
    if uid in user_data and message.channel.name == "общее":
        user_data[uid]['messages'] = min(user_data[uid].get('messages', 0) + 1, 150)
        save_data({"users": user_data, "cooldowns": cooldowns})
    await client.process_commands(message)

@client.event
async def on_command_completion(ctx):
    uid = str(ctx.author.id)
    if uid in user_data:
        user_data[uid]['commands'] = min(user_data[uid].get('commands', 0) + 1, 50)

@client.event
async def on_voice_state_update(member, before, after):
    uid = str(member.id)
    if uid not in user_data: return
    if before.channel is None and after.channel is not None:
        voice_timers[uid] = time.time()
    elif before.channel is not None and after.channel is None:
        if uid in voice_timers:
            duration = (time.time() - voice_timers[uid]) / 60
            user_data[uid]['voice'] = min(user_data[uid].get('voice', 0) + int(duration), 20)
            del voice_timers[uid]

cooldowns = {}

@client.group(invoke_without_command=True)
async def event(ctx):
    uid = str(ctx.author.id)
    if uid in user_data:
        data = user_data[uid]
        now = time.time()
        
        if uid in cooldowns and now - cooldowns[uid] < 1800:
            wait_time = int((1800 - (now - cooldowns[uid])) / 60)
            await ctx.send(f"⚠️ Задания на перезарядке. Подожди еще {wait_time} мин.")
            return

        if data['messages'] >= 150 and data['commands'] >= 50 and data['voice'] >= 20:
            data['messages'] = 0
            data['commands'] = 0
            data['voice'] = 0
            cooldowns[uid] = now
            await ctx.send("✅ Задания выполнены! Таймер перезарядки (30 мин) запущен.")
            return

        m, c, v = data.get('messages', 0), data.get('commands', 0), data.get('voice', 0)
        bar_v = f"[{'▬' * (v // 4)}{'—' * (5 - (v // 4))}]"
        bar_c = f"[{'▬' * (c // 10)}{'—' * (5 - (c // 10))}]"
        bar_m = f"[{'▬' * (m // 30)}{'—' * (5 - (m // 30))}]"

        if data['side'] == 'kira':
            tasks = ("Охота (Войс)", "Использование Тетради (Команды)", "Распространение слухов (Сообщения)")
        else:
            tasks = ("Допросы (Войс)", "Сбор улик (Команды)", "Поиск следов Киры (Сообщения)")

        embed = discord.Embed(title=f"🍎 Фракция: {data['side'].upper()}", color=0xff0000 if data['side'] == 'kira' else 0x0000ff)
        embed.description = (
            f"📋 Оперативные задачи\n\n"
            f"⏳ Голод/Расследование\n🎙️ {tasks[0]}\n{bar_v} {v}/20 мин\n\n"
            f"⏳ Мутация/Анализ\n🔮 {tasks[1]}\n{bar_c} {c}/50\n\n"
            f"⏳ Трагедия/Правосудие\n🩸 {tasks[2]}\n{bar_m} {m}/150"
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="📓 DEATH NOTE: ВОЙНА ФРАКЦИЙ", color=0xffff00)
        embed.description = "ВЫБЕРИ СВОЮ СТОРОНУ. ПУТИ НАЗАД НЕ БУДЕТ."
        await ctx.send(embed=embed, view=FactionView())

@client.command()
async def event(ctx, sub_command=None):
    if sub_command == "leaderboard":
        await ctx.guild.chunk()
        kira_list = []
        det_list = []
        
        for uid, data in user_data.items():
            score = data.get('messages', 0) + data.get('commands', 0) + data.get('voice', 0)
            member = ctx.guild.get_member(int(uid))
            name = member.display_name if member else f"ID {uid}"
            
            if data.get('side') == 'kira':
                kira_list.append((name, score))
            else:
                det_list.append((name, score))
                
        kira_list.sort(key=lambda x: x[1], reverse=True)
        det_list.sort(key=lambda x: x[1], reverse=True)
        
        k_text = "\n".join([f"{i+1}. {n} — {s}" for i, (n, s) in enumerate(kira_list[:5])]) or "Пусто."
        d_text = "\n".join([f"{i+1}. {n} — {s}" for i, (n, s) in enumerate(det_list[:5])]) or "Пусто."
        
        embed = discord.Embed(title="🏆 ТАБЛИЦА ЛИДЕРОВ", color=0xffff00)
        embed.add_field(name="🍎 Фракция Киры", value=k_text, inline=True)
        embed.add_field(name="🕵️ Фракция Детективов", value=d_text, inline=True)
        
        await ctx.send(embed=embed)
        
    else:
        user_id = str(ctx.author.id)
        if user_id in user_data:
            data = user_data[user_id]
            side_name = "Кира" if data['side'] == 'kira' else "Детективы"
            embed = discord.Embed(title=f"🍎 Фракция: {side_name.upper()}", color=discord.Color.blue())
            embed.add_field(name="📝 Оперативные задачи", value=f"Голод/Расследование: {data.get('voice', 0)}/20\nМутация/Анализ: {data.get('commands', 0)}/50\nТрагедия/Правосудие: {data.get('messages', 0)}/150", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Вы еще не участвуете в ивенте.")

@client.event
async def on_ready():
    client.add_view(FactionView())

business = app_commands.Group(name="business", description="Управление бизнесом")

client.tree.add_command(business)

def load_data():
    if not os.path.exists("economy.json"): return {}
    with open("economy.json", "r") as f: return json.load(f)

def save_data(data):
    with open("economy.json", "w") as f: json.dump(data, f, indent=4)

BUSINESS_PRICES = {
    1: 100000,
    2: 250000,
    3: 750000
}

def check_user(data, gid, uid):
    if gid not in data:
        data[gid] = {}
    if uid not in data[gid]:
        data[gid][uid] = {"balance": 0, "businesses": []}
    if "businesses" not in data[gid][uid]:
        data[gid][uid]["businesses"] = []
    if "balance" not in data[gid][uid]:
        data[gid][uid]["balance"] = 0

@business.command(name="create", description="Создать свой бизнес")
@app_commands.choices(level=[
    app_commands.Choice(name="Уровень 1 (100к)", value=1),
    app_commands.Choice(name="Уровень 2 (250к)", value=2),
    app_commands.Choice(name="Уровень 3 (750к)", value=3),
])
async def create(interaction: discord.Interaction, name: str, level: int):
    cost = BUSINESS_PRICES.get(level)
    gid, uid = str(interaction.guild_id), str(interaction.user.id)
    data = load_data()
    
    check_user(data, gid, uid)
    
    if len(data[gid][uid]["businesses"]) >= 3:
        await interaction.response.send_message("У вас уже максимум (3) бизнесов!", ephemeral=True)
        return

    balance = data[gid][uid].get("balance", 0)
    
    if balance < cost:
        await interaction.response.send_message("Недостаточно средств!", ephemeral=True)
        return

    data[gid][uid]["balance"] -= cost
    data[gid][uid]["businesses"].append({
        "name": name, 
        "level": level, 
        "last_collect": time.time()
    })
    
    save_data(data)
    await interaction.response.send_message(f"Бизнес '{name}' создан!")

@business.command(name="delete_player", description="Удалить бизнес игрока")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(choice=[
    app_commands.Choice(name="1", value="1"),
    app_commands.Choice(name="2", value="2"),
    app_commands.Choice(name="3", value="3"),
    app_commands.Choice(name="All", value="all"),
])
async def delete_player(interaction: discord.Interaction, user: discord.Member, choice: str):
    data = load_data()
    gid, uid = str(interaction.guild_id), str(user.id)
    if gid not in data or uid not in data[gid] or not data[gid][uid].get("businesses"):
        await interaction.response.send_message("У игрока нет бизнесов.", ephemeral=True)
        return
    businesses = data[gid][uid]["businesses"]
    if choice == "all":
        data[gid][uid]["businesses"] = []
        msg = f"Все бизнесы игрока {user.name} удалены."
    else:
        index = int(choice) - 1
        if 0 <= index < len(businesses):
            removed_biz = businesses.pop(index)
            msg = f"Бизнес '{removed_biz['name']}' игрока {user.name} удален."
        else:
            await interaction.response.send_message(f"У игрока нет бизнеса №{choice}.", ephemeral=True)
            return
    save_data(data)
    await interaction.response.send_message(msg)

@delete_player.error
async def delete_player_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("У вас нет прав администратора!", ephemeral=True)

@business.command(name="collect", description="Собрать прибыль")
async def collect_biz(interaction: discord.Interaction):
    await interaction.response.defer()
    
    guild_id, user_id = str(interaction.guild_id), str(interaction.user.id)
    
    if not os.path.exists("economy.json"):
        await interaction.followup.send("Файл экономики не найден.", ephemeral=True)
        return

    with open("economy.json", "r") as f:
        data = json.load(f)
    
    user_data = data.get(guild_id, {}).get(user_id)
    if not user_data or not user_data.get("businesses"):
        await interaction.followup.send("У вас нет бизнесов для сбора прибыли.", ephemeral=True)
        return

    now = datetime.datetime.now()
    total_profit = 0
    updated = False
    
    for biz in user_data["businesses"]:
        profit = BUSINESS_LEVELS[biz.get("level", 1)]["profit"]
        raw_last_collect = biz.get("last_collect") or biz.get("created_at")
        
        if isinstance(raw_last_collect, str):
            try:
                last_collect = datetime.datetime.fromisoformat(raw_last_collect)
            except ValueError:
                last_collect = now
                biz["last_collect"] = now.isoformat()
                updated = True
        else:
            last_collect = now
            biz["last_collect"] = now.isoformat()
            updated = True
        
        minutes_passed = (now - last_collect).total_seconds() / 60
        intervals = int(minutes_passed // 5)
        
        if intervals > 0:
            total_profit += intervals * profit
            biz["last_collect"] = (last_collect + datetime.timedelta(minutes=intervals * 5)).isoformat()
            updated = True
    
    if total_profit <= 0:
        await interaction.followup.send("Прибыль еще не накопилась!", ephemeral=True)
        return
        
    user_data["balance"] = user_data.get("balance", 0) + total_profit
    
    with open("economy.json", "w") as f:
        json.dump(data, f, indent=4)
        
    await interaction.followup.send(f"Вы успешно собрали {total_profit:,}$!")

@business.command(name="list", description="Список ваших бизнесов")
async def list_biz(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)
    
    if not os.path.exists("economy.json"):
        await interaction.response.send_message("База данных экономики пуста.", ephemeral=True)
        return
        
    with open("economy.json", "r") as f:
        data = json.load(f)
        
    user_data = data.get(guild_id, {}).get(user_id, {})
    businesses = user_data.get("businesses", [])
    
    if not businesses:
        await interaction.response.send_message("У вас пока нет ни одного бизнеса.")
        return
        
    embed = discord.Embed(title=f"Список бизнесов {interaction.user.display_name}", color=discord.Color.blue())
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    now = datetime.datetime.now()
    
    for i, biz in enumerate(businesses, 1):
        profit = BUSINESS_LEVELS[biz.get("level", 1)]["profit"]
        
        date_str = biz.get("last_collect") or biz.get("created_at")
        
        if isinstance(date_str, str):
            try:
                last_collect = datetime.datetime.fromisoformat(date_str)
            except:
                last_collect = now
        else:
            last_collect = now
            
        minutes_passed = (now - last_collect).total_seconds() / 60
        intervals = int(minutes_passed // 5)
        saved = intervals * profit
            
        embed.add_field(
            name=f"{i}. {biz['name']}",
            value=(
                f"Доход: {profit:,}$/5 мин\n"
                f"Накоплено: {saved:,}$\n"
                f"Создан: {last_collect.strftime('%d.%m.%Y %H:%M')}"
            ),
            inline=False
        )
        
    await interaction.response.send_message(embed=embed)

@business.command(name="delete", description="Удалить бизнес по номеру (из списка /business list)")
async def delete_biz(interaction: discord.Interaction, number: int):
    guild_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)
    
    with open("economy.json", "r") as f:
        data = json.load(f)
        
    user_data = data.get(guild_id, {}).get(user_id, {})
    businesses = user_data.get("businesses", [])
    
    if number < 1 or number > len(businesses):
        await interaction.response.send_message(f"❌ Бизнеса с номером {number} не существует. Проверьте список через `/business list`.", ephemeral=True)
        return
        
    removed_biz = businesses.pop(number - 1)
    
    with open("economy.json", "w") as f:
        json.dump(data, f, indent=4)
        
    await interaction.response.send_message(f"🗑️ Бизнес **«{removed_biz['name']}»** успешно удален!")



@business.command(name="rename", description="Переименовать бизнес")
async def rename_biz(interaction: discord.Interaction, number: int, new_name: str):
    guild_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)
    
    with open("economy.json", "r") as f:
        data = json.load(f)
        
    user_data = data.get(guild_id, {}).get(user_id, {})
    businesses = user_data.get("businesses", [])
    
    if number < 1 or number > len(businesses):
        await interaction.response.send_message(f"❌ Бизнеса с номером {number} не существует.", ephemeral=True)
        return
        
    old_name = businesses[number - 1]["name"]
    businesses[number - 1]["name"] = new_name
    
    with open("economy.json", "w") as f:
        json.dump(data, f, indent=4)
        
    await interaction.response.send_message(f"✏️ Бизнес «{old_name}» переименован в **«{new_name}»**!")

@business.command(name="help", description="Показать список доступных команд")
async def help_biz(interaction: discord.Interaction):
    embed = discord.Embed(
        title="ℹ️ Помощь по системе бизнеса", 
        description="Здесь список всех доступных команд:", 
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🛠 Основные команды:",
        value=(
            "**/business create** — Купить новый бизнес\n"
            "**/business list** — Посмотреть ваши бизнесы\n"
            "**/business delete <номер>** — Удалить бизнес\n"
            "**/business rename <номер> \"новое имя\"** — Переименовать"
        ),
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

if client.tree.get_command("business") is None:
    client.tree.add_command(business)

admin_group = app_commands.Group(name="a", description="Административные команды")

@admin_group.command(name="i", description="Выдать деньги пользователю (до 10 млрд)")
async def give_money(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ У вас недостаточно прав, чтобы использовать эту команду!", ephemeral=True)
        return

    if amount > 10000000000:
        await interaction.response.send_message("❌ Нельзя выдать больше 10 000 000 000 монет за раз!", ephemeral=True)
        return

    guild_id = str(interaction.guild_id)
    target_id = str(member.id)
    
    if not os.path.exists("economy.json"):
        with open("economy.json", "w") as f:
            json.dump({}, f)
            
    with open("economy.json", "r") as f:
        data = json.load(f)
        
    if guild_id not in data:
        data[guild_id] = {}
    if target_id not in data[guild_id]:
        data[guild_id][target_id] = {"balance": 0, "businesses": []}
        
    data[guild_id][target_id]["balance"] += amount
    
    with open("economy.json", "w") as f:
        json.dump(data, f, indent=4)
        
    await interaction.response.send_message(f"✅ Успешно выдано **{amount:,}** монет пользователю {member.mention}.")

client.tree.add_command(admin_group)

class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Экономика", value="eco", description="Бизнесы, работа, награды"),
            discord.SelectOption(label="Администрация", value="admin", description="Управление сервером"),
            discord.SelectOption(label="Модерация", value="mod", description="Наказания и очистка")
        ]
        super().__init__(placeholder="Выберите раздел...", options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=discord.Color.blue())
        
        if self.values[0] == "eco":
            embed.title = "💰 Экономика"
            embed.description = (
                "/business create — Купить бизнес\n"
                "/business list — Список ваших бизнесов\n"
                "/business delete — Удалить бизнес\n"
                "/business rename — Переименовать\n"
                "/business collect — Собрать накопленное\n"
                "/work — Поработать\n"
                "/daily — Ежедневная награда\n"
                "/weekly — Еженедельная награда"
                "/deposit — Положить в банк\n"
                "/withdraw — Снять с банка\n"
                "/slots — Казино слоты\n"
                "/blacklack — Казино блекджек\n"
            )
        elif self.values[0] == "admin":
            embed.title = "🛠 Администрация"
            embed.description = (
                "/a i — Выдать деньги пользователю\n"
                "/warn — Выдать предупреждение\n"
                "/unwarn — Сняь предупреждение\n"
                "/warn_list — Список выданых предупреждений\n"
                "/business delete_player — Удаляет бизнесы игрока\n"
            )
        elif self.values[0] == "mod":
            embed.title = "🛡 Модерация"
            embed.description = (
                "/ban — Забанить участника\n"
                "/kick — Кикнуть участника\n"
                "/mute — Заглушить участника\n"
                "/unmute — Снять мут\n"
                "/unban — Разбаниь учасника\n"
            )
            
        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpSelect())

@client.event
async def on_ready():
    client.add_view(FactionView())
    print(f"Bot {client.user} is ready!")
    
    if not payout_loop.is_running():
        payout_loop.start()
        
    print("Бот готов к работе с текстовыми командами!")

client.run(os.getenv('BOT_TOKEN'))
