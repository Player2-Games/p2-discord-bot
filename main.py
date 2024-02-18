import discord
import openai
from dotenv import load_dotenv
from discord.ext import commands
import os


load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

openai.api_key=OPENAI_API_KEY

# Função que retorna o prompt
def load_prompt_from_file(file_path):
    with open(file_path, 'r') as file:
        prompt = file.read()
    return prompt

# Função que busca as mensagens do discord
async def get_channel_history(channel, limit=5):
    messages_list = []
    async for message in channel.history(limit=limit):
        messages_list.append(
            {
                "role": "user" if message.author.id != bot.user.id else "system",
                "content": message.content
            }
        )
        
    messages_list.reverse()
    return messages_list

# Função que faz requisição para o chat gpt  com as mensagens do discord e retorna a resposta do assistent
def request_gpt(messages):
    prompt = {
        "role": "system",
        "content": load_prompt_from_file('prompt.txt')
    }
    
    messages.insert(0, prompt)
    
    response = openai.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo-16k",
        temperature=0.9,
        max_tokens=3000,
    )
    
    return response.choices[0].message.content

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    async with message.channel.typing():
        # Busca um array com as ultimas 5 mensagens do discord (bot e usuario)
        messages = await get_channel_history(message.channel)
        
        # Faz requisição pra api com as mensagens do discord
        response = request_gpt(messages)

        # Responde a mensagem com a resposta do gpt
        await message.reply(response)
        
    await bot.process_commands(message)

bot.run(DISCORD_BOT_TOKEN)