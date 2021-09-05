from pornhub_api import PornhubApi
from pornhub_api.backends.aiohttp import AioHttpBackend
from pyrogram import Client, filters
from pyrogram.types import (InlineQuery, InlineQueryResultArticle, CallbackQuery,
                            InputTextMessageContent, Message, InlineKeyboardMarkup, InlineKeyboardButton)
from pyrogram.types.messages_and_media import message
import youtube_dl
import os
import asyncio

from config import Config
from pyromod.helpers import ikb

app = Client("pornhub_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN)

if os.path.exists("downloads"):
    print("Download Path Exist")
else:
    print("Download Path Created")


async def run_async(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


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


@app.on_message(filters.command("start"))
async def start(client, message : Message):
    btn1 = InlineKeyboardButton("Search Here",switch_inline_query_current_chat="porn",)
    btn2 = InlineKeyboardButton("Go Inline", switch_inline_query="porn")
    await message.reply(f"**Hello, @{message.from_user.username}**,\n"
                        "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                        "This Bot Can Search **Pornhub** Videos\n"
                        "And Download Them For You\n"
                        "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                        "Click The Buttons Below To Search", reply_markup=InlineKeyboardMarkup([[btn1, btn2]]))
    

@app.on_message(link_filter)
async def options(client, message : Message):
    print(message.text)
    await message.reply("What would like to do?", 
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Download", f"d_{message.text}"), InlineKeyboardButton("Watch Video",url=message.text)]
            ])
            )



@app.on_callback_query(filters.regex("^d"))
async def download_video(client, callback : CallbackQuery):
    print(callback.data)
    url = callback.data.split("_",1)[1]
    print(url)
    msg = await callback.message.edit("Downloading...")

    ydl_opts = {
            #'format': 'best',
            'outtmpl': "downloads",
            'nooverwrites': True,
            'no_warnings': False,
            'ignoreerrors': True,
        }

    with youtube_dl.YoutubeDL() as ydl:
        # meta = ydl.extract_info(url, download=False)
        # formats = meta.get('formats', [meta])
        # btn_list = []
        # for f in formats:
        #    btn_list.append([(f['resolution'], f"q_{f['ext']}_{url}")])
        #    print(f['resolution'])
        #     print(f)

        # await callback.message.edit("Choose your desired Quality", reply_markup=ikb(btn_list))

        await run_async(ydl.download, [url])

    for file in os.listdir('.'):
        if file.endswith(".mp4"):
            print("found pwd")
            await callback.message.reply_video(f"{file}", caption="Here Is your Requested Video")
            os.remove(f"{file}")
            break
        else:
            continue

    await msg.delete()


@app.on_message(filters.command("cc"))
async def download_video(client, message : Message):
    files = os.listdir("downloads")
    await message.reply(files)






app.run()
