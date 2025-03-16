import discord
from discord.ext import commands
from imageai.Detection import ObjectDetection
import os

def detect_objects(img, model_path):
    global output_image_path, output_image, detections
    detector = ObjectDetection()
    detector.setModelTypeAsYOLOv3()
    detector.setModelPath(model_path)
    detector.loadModel()
    
    output_image_path = "output_image.jpg"
    detections = detector.detectObjectsFromImage(
        input_image=img,
        output_image_path=output_image_path,
        minimum_percentage_probability=30
    )

    output_image = output_image_path
    return detections


#potrzebne
intents = discord.Intents.all()
intents.reactions = True
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot_permissions = discord.Permissions()

#Wiadomości błędów
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"{ctx.author.mention}, nie masz odpowiedniej roli, aby użyć tej komendy.")
    if isinstance(error, commands.BadArgument):
        await ctx.send(f"{ctx.author.mention}, zły argument, wpisz /help lub /adm_help")
    if isinstance(error, commands.CommandOnCooldown):
        retry_after = round(error.retry_after)
        await ctx.send(f"Spokojnie... musisz poczekać jeszcze {retry_after}s zanim użyjesz tej komendy")
    if isinstance(error, commands.CommandError):
        print(error)
        await ctx.send(f"Coś nie pykło...")
    else:
        raise error
    
#Wiadmomość uruchomienia
@bot.event
async def on_ready():
    print("online")
    try:
        synced = await bot.tree.sync()
        print(f"Zynschronizowano {len(synced)}")
    except Exception as e:
        print(e)

#!detect
@bot.command()
async def detect(ctx):
    global output_image
    if not ctx.message.attachments:
        await ctx.send("Musisz załączyć obrazek!")
        return

    img_path = "input.jpg"
    await ctx.message.attachments[0].save(img_path)
    
    detect_objects(img_path, "yolov3.pt")

    if os.path.exists(output_image):
        embed = discord.Embed(
            title="Wykryte obiekty",
            description=f"Znaleziono {len(detections)} obiektów",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        await ctx.send(file=discord.File(output_image))
    else:
        await ctx.send("Nie udało się wykryć obiektów.")
    
    os.remove(img_path)


bot.run("token")
