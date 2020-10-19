import os
import random
import requests
from datetime import datetime

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils import replace

# main
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OWM_API = os.getenv('OWM_API_KEY')

bot = commands.Bot(command_prefix='%')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='Welcome for testing'))
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send_help(ctx.command)
    else:
        print(error)

@bot.command(help='Says hello to Monty Bot')
async def hello(ctx):
    await ctx.send(f'Hi, {ctx.author.name}!')

@bot.command(help='Simulates rolling dice')
async def rolldice(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='weather', help='Get weather info of a city')
async def weather(ctx, city):
    city = replace(city, ['-', '_'], ' ')

    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': city,
        'appid': OWM_API,
        'units': 'metric',
    }

    rjs = requests.get(url=url, params=params).json()

    if int(rjs['cod']) == 200:
        current_time = datetime.utcfromtimestamp(rjs['dt']+rjs['timezone'])\
            .strftime('%I:%M %p')
        title = f'Weather at {rjs["name"]}'
        desc = f'data at {current_time} local time'
        field_params = {
            'Weather': f'{rjs["weather"][0]["description"].capitalize()}',
            'Temperature': f'{rjs["main"]["temp"]:.1f} deg. C '\
                f'({rjs["main"]["temp_min"]:.1f} - {rjs["main"]["temp_max"]:.1f})',
            'Feels like': f'{rjs["main"]["feels_like"]} deg. C',
            'Humidity': f'{rjs["main"]["humidity"]}\%',
            'Wind speed': f'{rjs["wind"]["speed"]} m/s',
        }
        weather_icon_url = \
            'http://openweathermap.org/img/wn/' + rjs['weather'][0]['icon'] + '.png'
        footer = 'Powered by OpenWeather'
        favicon_url = \
            'https://openweathermap.org/themes/openweathermap/assets/vendor/owm/img/icons/logo_32x32.png'

        embed = discord.Embed(title=title, description=desc, color=0x7289da)
        for key, value in field_params.items():
            embed.add_field(name=key, value=value)
        embed.set_thumbnail(url=weather_icon_url)
        embed.set_footer(text=footer, icon_url=favicon_url)

        await ctx.send(embed=embed)

    elif int(rjs['cod']) == 404:
        await ctx.send('City not found.')

    else:
        await ctx.send(f'{rjs["cod"]}: Weather data could not be requested.')

@bot.command(help='Get a random quote')
async def quote(ctx):
    rjs = requests.get('https://api.quotable.io/random').json()
    await ctx.send(f'{rjs["content"]}    \u2014\u2014 {rjs["author"]}')

@bot.command(help='Search Wikipedia article')
async def wiki(ctx, search_string):
    search_string = replace(search_string, [' ', '-'], '_')

    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srsearch': search_string,
        'srlimit': 1,
    }

    rjs = requests.get(url=url, params=params).json()
    page_url = 'https://en.wikipedia.org/wiki/'

    if not rjs['query']['search']:
        await ctx.send('No results found.')
        return

    title = rjs['query']['search'][0]['title'].replace(' ', '_')
    await ctx.send(page_url + title)

@bot.command(help='Get a random Wikipedia page of specified category')
async def randomwiki(ctx, category=None):
    def good_title(title):
        return ':' not in title

    category = replace(category, [' ', '-'], '_')

    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
    }

    if category is None:
        params.update({
            'list': 'random',
            'rnlimit': 50,
        })
    else:
        params.update({
            'list': 'categorymembers',
            'cmtitle': 'Category:' + category,
            'cmtype': 'page',
            'cmlimit': 'max',
        })

    rjs = requests.get(url=url, params=params).json()
    page_url = 'https://en.wikipedia.org/wiki/'

    if category is None:
        all_titles = [ent['title'] for ent in rjs['query']['random']]
    else:
        if not rjs['query']['categorymembers']:
            await ctx.send("Category doesn't exist.")
            return
        all_titles = [ent['title'] for ent in rjs['query']['categorymembers']]

    choice = random.choice(list(filter(good_title, all_titles)))
    choice = choice.replace(' ', '_')
    await ctx.send(page_url + choice)

bot.run(TOKEN)