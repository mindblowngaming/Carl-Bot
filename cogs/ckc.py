import datetime
import re
import statistics
import random
import sqlite3
import markovify
import string
import discord
import aiohttp

from collections import Counter
from io import BytesIO
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


def beaufort_scale(speed):
    if speed < 0:
        return "I don't fucking know"
    elif speed <= 0.3:
        return "Calm"
    elif speed <= 1.5:
        return "Light air"
    elif speed <= 3.3:
        return "Light breeze"
    elif speed <= 5.5:
        return "Gentle breeze"
    elif speed <= 7.9:
        return "Moderate breeze"
    elif speed <= 10.7:
        return "Fresh breeze"
    elif speed <= 13.8:
        return "Strong breeze"
    elif speed <= 17.1:
        return "Moderate gale"
    elif speed <= 20.7:
        return "Gale"
    elif speed <= 24.4:
        return "Strong gale"
    elif speed <= 28.4:
        return "Storm"
    elif speed <= 32.6:
        return "Violent storm"
    else:
        return "Hurricane force"


def pretty_weather(weather):  # this is literally the dumbest thing my bot has
    weather = weather.lower()
    if weather == "light rain":
        return ":cloud_rain: Light rain"
    elif weather == "snow":
        return ":cloud_snow: Snow"
    elif weather == "light intensity drizzle":
        return ":cloud_rain: Light intensity drizzle"
    elif weather == "light snow":
        return ":cloud_snow: Light snow"
    elif weather == "broken clouds":
        return ":white_sun_cloud: Broken clouds"
    elif weather == "clear sky":
        return ":large_blue_circle: Clear sky"
    elif weather == "haze":
        return ":foggy: Haze"
    elif weather == "overcast clouds":
        return ":cloud: Overcast clouds"
    elif weather == "mist":
        return ":fog: Mist"
    elif weather == "few clouds":
        return ":cloud: Few clouds"
    elif weather == "scattered clouds":
        return ":cloud: Scattered clouds"
    elif weather == "moderate rain":
        return ":cloud_rain: Moderate rain"
    elif weather == "shower rain":
        return ":cloud_rain: Shower rain"
    else:
        return weather.capitalize()


smallcaps_alphabet = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ1234567890"

uppercase_fraktur = "𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ"
lowercase_fraktur = "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷1234567890"

uppercase_boldfraktur = "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅"
lowercase_boldfraktur = "𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟1234567890"


double_uppercase = "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ"

double_lowercase = "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡𝟘"

bold_fancy_lowercase = "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃1234567890"
bold_fancy_uppercase = "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩"

fancy_lowercase = "𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫𝟢"
fancy_uppercase ="𝒜𝐵𝒞𝒟𝐸𝐹𝒢𝐻𝐼𝒥𝒦𝐿𝑀𝒩𝒪𝒫𝒬𝑅𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵"



alphabet = dict(zip("abcdefghijklmnopqrstuvwxyz1234567890", range(0, 36)))
uppercase_alphabet = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", range(0, 26)))
punctuation = dict(
    zip("§½!\"#¤%&/()=?`´@£$€{[]}\\^¨~'*<>|,.-_:", range(0, 37)))
space = " "
aesthetic_space = '\u3000'
aesthetic_punctuation = "§½！\"＃¤％＆／（）＝？`´＠£＄€｛［］｝＼＾¨~＇＊＜＞|，．－＿："
aesthetic_lowercase = "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ１２３４５６７８９０"
aesthetic_uppercase = "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"


def clean_string(string):
    string = re.sub('@', '@\u200b', string)
    string = re.sub('#', '#\u200b', string)
    return string


def aesthetics(string):
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += aesthetic_lowercase[alphabet[letter]]
            elif letter in uppercase_alphabet:
                returnthis += aesthetic_uppercase[uppercase_alphabet[letter]]
            elif letter in punctuation:
                returnthis += aesthetic_punctuation[punctuation[letter]]
            elif letter == space:
                returnthis += aesthetic_space
            else:
                returnthis += letter
    return returnthis

def double_font(string):
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += double_lowercase[alphabet[letter]]
            elif letter in uppercase_alphabet:
                returnthis += double_uppercase[uppercase_alphabet[letter]]
            elif letter == space:
                returnthis += " "
            else:
                returnthis += letter
    return returnthis

def fraktur(string):
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += lowercase_fraktur[alphabet[letter]]
            elif letter in uppercase_alphabet:
                returnthis += uppercase_fraktur[uppercase_alphabet[letter]]
            elif letter == space:
                returnthis += " "
            else:
                returnthis += letter
    return returnthis

def bold_fraktur(string):
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += lowercase_boldfraktur[alphabet[letter]]
            elif letter in uppercase_alphabet:
                returnthis += uppercase_boldfraktur[uppercase_alphabet[letter]]
            elif letter == space:
                returnthis += " "
            else:
                returnthis += letter
    return returnthis

def fancy(string):
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += fancy_lowercase[alphabet[letter]]
            elif letter in uppercase_alphabet:
                returnthis += fancy_uppercase[uppercase_alphabet[letter]]
            elif letter == space:
                returnthis += " "
            else:
                returnthis += letter
    return returnthis

def bold_fancy(string):
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += bold_fancy_lowercase[alphabet[letter]]
            elif letter in uppercase_alphabet:
                returnthis += bold_fancy_uppercase[uppercase_alphabet[letter]]
            elif letter == space:
                returnthis += " "
            else:
                returnthis += letter
    return returnthis


def smallcaps(string):
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += smallcaps_alphabet[alphabet[letter]]
            else:
                returnthis += letter
    return returnthis


eight_ball_responses = [
    "It is certain",
    "It is decidedly so",
    "Without a doubt",
    "Yes, definitely",
    "You may rely on it",
    "As I see it, yes",
    "Most likely",
    "Outlook good",
    "Yes",
    "Signs point to yes",
    "Reply hazy try again",
    "Ask again later",
    "Better not tell you now",
    "Cannot predict now",
    "Concentrate and ask again",
    "Don't count on it",
    "My reply is no",
    "My sources say no",
    "Outlook not so good",
    "Very doubtful"
]


class CoolKidsClub(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()

    @commands.command(aliases=["pick", "choice", "select"])
    async def choose(self, ctx, *choices):
        if ctx.message.mentions:
            return
        if "," in ctx.message.content:
            # real_choices = ctx.message.content.split()
            # real_choices = real_choices[1:]
            
            real_choices = ' '.join(choices)
            real_choices = real_choices.split(",")
        else:
            real_choices = choices
        await ctx.send(clean_string(random.choice(real_choices)))

    @commands.command(name='aesthetics', aliases=['ae'])
    async def _aesthetics(self, ctx, *, sentence: str):
        await ctx.send(aesthetics(sentence))

    @commands.command(name='fraktur')
    async def _fraktur(self, ctx, *, sentence: str):
        await ctx.send(fraktur(sentence))

    @commands.command(name='boldfaktur')
    async def _boldfaktur(self, ctx, *, sentence: str):
        await ctx.send(bold_fraktur(sentence))

    @commands.command(name='fancy', aliases=['ff'])
    async def _fancy(self, ctx, *, sentence: str):
        await ctx.send(fancy(sentence))

    @commands.command(name='boldfancy', aliases=['bf'])
    async def _bold_fancy(self, ctx, *, sentence: str):
        await ctx.send(bold_fancy(sentence))

    @commands.command(name='double', aliases=['ds'])
    async def _doublestruck(self, ctx, *, sentence: str):
        await ctx.send(double_font(sentence))

    @commands.command(name='smallcaps', aliases=['sc'])
    async def _smallcaps(self, ctx, *, sentence: str):
        await ctx.send(smallcaps(sentence))

    @commands.command(name="8ball")
    async def eightball(self, ctx):
        """
        I hate this command and everyone who uses it
        """
        r = random.choice(eight_ball_responses)
        await ctx.send(":8ball: | {}, **{}**".format(r, ctx.message.author.name))



    @commands.command(no_pm=True, hidden=True)
    async def poehere(self, ctx):
        poe_role = discord.utils.get(ctx.guild.roles, id=345966982715277312)
        if poe_role not in ctx.author.roles:
            return await ctx.send("You need to have the poe role to use this command. !poe to get it.")
        offline = [x for x in ctx.guild.members if (
            poe_role in x.roles and str(x.status) != "online")]
        for m in offline:
            await m.remove_roles(poe_role, reason="automatic poehere")
        await poe_role.edit(mentionable=True)
        await ctx.send("<@&345966982715277312>")
        for m in offline:
            await m.add_roles(poe_role, reason="automatic poehere")
        await poe_role.edit(mentionable=False)
    #@commands.cooldown(1, 900, BucketType.user)
    @commands.group(no_pm=True, invoke_without_command=True, hidden=True)
    async def sicklad(self, ctx, user: discord.Member):
        """
        For when someone's really great
        """

        self.c.execute('''SELECT sicklad
                          FROM users
                          WHERE (server=? AND id=?)''',
                       (ctx.guild.id, user.id))
        sicklad_value = self.c.fetchone()[0]

        if user == ctx.author:
            await ctx.send("You sure are.")
            ctx.command.reset_cooldown(ctx)
            return
        if not sicklad_value:
            self.c.execute('''UPDATE users
                              SET sicklad = sicklad + 1
                              WHERE (id=? AND server=?)''',
                           (user.id, ctx.guild.id))
            self.conn.commit()
            await ctx.send("Welcome to the sicklad club, **{0}**".format(user.name))
        else:
            self.c.execute('''UPDATE users
                              SET sicklad = sicklad + 1
                              WHERE (id=? AND server=?)''',
                           (user.id, ctx.guild.id))
            self.conn.commit()
            await ctx.send("**{0}** now has **{1}** sicklad points.".format(user.name.replace("_", "\\_"), sicklad_value + 1))
   
    @commands.cooldown(5,60, BucketType.guild)
    @sicklad.command(no_pm=True, name="top", aliases=['leaderboard', 'leaderboards', 'highscore', 'highscores', 'hiscores'])
    async def sickladtop(self, ctx):
        self.c.execute('''SELECT *
                          FROM users
                          WHERE server=?
                          ORDER BY sicklad DESC LIMIT 10''',
                       (ctx.guild.id,))
        sickest_lads = self.c.fetchall()
        self.c.execute('''SELECT SUM(sicklad) AS "hello"
                          FROM users
                          WHERE server=?''',
                       (ctx.guild.id,))
        total_sicklad = self.c.fetchone()[0]
        post_this = ""
        rank = 1
        for row in sickest_lads:
            name = f'<@{row[3]}>'
            post_this += ("{}. {} : {}\n".format(rank, name, row[7]))
            rank += 1
        post_this += "\n**{0}** points in total spread across **{1}** sicklads.".format(
            total_sicklad, len([x for x in ctx.guild.members]))
        em = discord.Embed(title="Current standings:",
                           description=post_this, colour=0x3ed8ff)
        em.set_author(name=self.bot.user.name,
                      icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=em)

    @commands.group(no_pm=True, invoke_without_command=True, hidden=True)
    async def retard(self, ctx, member: discord.Member=None, *, reason: str = None):
        user = ctx.message.author if member is None else member
        self.c.execute('''SELECT retard
                          FROM users
                          WHERE (server=? AND id=?)''',
                       (ctx.guild.id, user.id))
        retard = self.c.fetchone()[0]
        leftover_args = ctx.message.content.split()
        leftover_args = leftover_args[1:]
        if user == ctx.message.author:
            await ctx.send("You sure are.")
            return
        if not retard:
            self.c.execute('''UPDATE users
                              SET retard = retard + 1
                              WHERE (id=? AND server=?)''',
                           (user.id, ctx.guild.id))
            self.conn.commit()
            await ctx.send("Welcome to the retard club, **{0}**".format(user.name))
        else:
            if reason is None:
                self.c.execute('''UPDATE users
                                  SET retard = retard + 1
                                  WHERE (id=? AND server=?)''',
                               (user.id, ctx.guild.id))
                self.conn.commit()
                await ctx.send("**{0}** now has **{1}** coins.".format(user.name.replace("_", "\\_"), retard + 1))
            else:
                self.c.execute('UPDATE users SET retard = retard + 1 WHERE (id=? AND server=?)',
                               (user.id, ctx.guild.id))
                self.conn.commit()
               
