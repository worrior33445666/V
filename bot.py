from pornhub_api import PornhubApi
from pornhub_api.backends.aiohttp import AioHttpBackend
from pornhub_api.modules import video
from pyrogram import Client, filters
from pyrogram.types import (InlineQuery, InlineQueryResultArticle,
                            InputTextMessageContent, Message)
import youtube_dl
import os

from config import Config
import wget

app = Client("pornhub_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN)

if os.path.exists("downloads"):
    print("Download Path Exist")
else:
    print("Download Path Created")


def link_fil(filter, client, update):
    if "www.pornhub" in update.text:
        return True
    else:
        return False

link_filter = filters.create(link_fil, name="link_filter")

@app.on_inline_query()
async def search(client, InlineQuery : InlineQuery):
    query = InlineQuery.query
    backend = AioHttpBackend()
    api = PornhubApi(backend=backend)
    src = await api.search.search(query)#, ordering="mostviewed")
    videos = src.videos
    await backend.close()
    

    results = []

    for vid in videos:
        results.append(InlineQueryResultArticle(
            title=vid.title,
            input_message_content=InputTextMessageContent(
                message_text=f"{vid.url}"
            ),
            description=f"Duration : {vid.duration}\nViews : {vid.views}\nRating : {vid.rating}",
            thumb_url=vid.thumb
        ))

    await InlineQuery.answer(results)
    

@app.on_message(link_filter)
async def download_video(client, message : Message):
    await message.reply("Downloading...")
    url = message.text
    print(url)
    a = url.replace("unknownview_video.php", "")
    print(a)
    # print(url)
    # path = wget.download(url)
    # print(path)

    ydl_opts = {
            'format': 'best',
            'outtmpl': "downloads",
            'nooverwrites': True,
            'no_warnings': False,
            'ignoreerrors': True,
        }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for file in os.listdir("downloads"):
        await message.reply_video(f"downloads/{file}", caption="Here Is your Requested Video")





app.run()
