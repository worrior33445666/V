from pornhub_api import PornhubApi
from pornhub_api.backends.aiohttp import AioHttpBackend
from pyrogram import Client, filters
from pyrogram.types import (InlineQuery, InlineQueryResultArticle, CallbackQuery, InlineQueryResultPhoto,
                            InputTextMessageContent, Message, InlineKeyboardMarkup, InlineKeyboardButton)
from pyrogram.errors.exceptions import UserNotParticipant, FloodWait, MessageNotModified
from pyrogram.types.input_message_content.input_message_content import InputMessageContent
import youtube_dl
import os
import asyncio
import threading

from config import Config
from database import Data
from pyromod.helpers import ikb

app = Client("pornhub_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN)

if os.path.exists("downloads"):
    print("Download Path Exist")
else:
    print("Download Path Created")

btn1 = InlineKeyboardButton("Search Here",switch_inline_query_current_chat="",)
btn2 = InlineKeyboardButton("Go Inline", switch_inline_query="")

active_list = []
queue = []


async def run_async(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


def link_fil(filter, client, update):
    if "www.pornhub" in update.text:
        return True
    else:
        return False

link_filter = filters.create(link_fil, name="link_filter")

def joined():

    def decorator(func):

        async def wrapped(client, message : Message):

            try:
                check = await app.get_chat_member("SJ_Bots", message.from_user.id)
                if check.status in ['member','administrator','creator']:
                    await func(client, message)
                else:
                    await message.reply("💡 You must join our channel in order to use this bot.\n/start the bot again after joining",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("JOIN CHANNEL", url="https://t.me/SJ_Bots")]]))
            except UserNotParticipant as e:
                await message.reply("💡 You must join our channel in order to use this bot",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("JOIN CHANNEL", url="https://t.me/SJ_Bots")]]))

        return wrapped

    return decorator

@app.on_inline_query()
async def search(client, InlineQuery : InlineQuery):
    query = InlineQuery.query
    backend = AioHttpBackend()
    api = PornhubApi(backend=backend)
    results = []
    try:
        src = await api.search.search(query)#, ordering="mostviewed")
    except ValueError as e:
        results.append(InlineQueryResultArticle(
                title="No Such Videos Found!",
                description="Sorry! No Such Vedos Were Found. Plz Try Again",
                input_message_content=InputTextMessageContent(
                    message_text="No Such Videos Found!"
                )
            ))
        await InlineQuery.answer(results,
                            switch_pm_text="Search Results",
                            switch_pm_parameter="start")
            
        return


    videos = src.videos
    await backend.close()
    

    for vid in videos:
        # vid.categories
        # vid.duration
        # vid.pornstars
        # vid.thumb
        # vid.url
        # vid.tags
        # vid.views
        # vid.title

        try:
            pornstars = ", ".join(v for v in vid.pornstars)
            categories = ", ".join(v for v in vid.categories)
            tags = ", #".join(v for v in vid.tags)
        except:
            pornstars = "N/A"
            categories = "N/A"
            tags = "N/A"
        msgg = (f"**TITLE** : `{vid.title}`\n"
                f"**DURATION** : `{vid.duration}`\n"
                f"VIEWS : `{vid.views}`\n\n"
                f"**{pornstars}**\n"
                f"Categories : {categories}\n\n"
                f"{tags}"
                f"Link : {vid.url}")

        msg = f"{vid.url}"
         
        results.append(InlineQueryResultArticle(
            title=vid.title,
            input_message_content=InputTextMessageContent(
                message_text=msg,
            ),
            description=f"Duration : {vid.duration}\nViews : {vid.views}\nRating : {vid.rating}",
            thumb_url=vid.thumb,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Watch online", url=vid.url),
                btn1
            ]]),
        ))

    await InlineQuery.answer(results,
                            switch_pm_text="Search Results",
                            switch_pm_parameter="start")


@app.on_message(filters.command("start"))
@joined()
async def start(client, message : Message):
    await message.reply(f"Hello @{message.from_user.username},\n"
                        "━━━━━━━━━━━━━━━━━━━━━\n"
                        "This Bot Can Search PornHub\n"
                        "Videos & Download Them For You\n"
                        "━━━━━━━━━━━━━━━━━━━━━\n"
                        "⚠️The Bot Contains 18+ Content\n"
                        "So Kindly Access it with Your own\n"
                        "Risk. Children Please Stay Away.\n" 
                        "We don't intend to spread Pørno-\n"
                        "-graphy here. It's just a bot for a\n" 
                        "purpose as many of them wanted.\n" 
                        "━━━━━━━━━━━━━━━━━━━━━\n"
                        "Click The Buttons Below To Search", reply_markup=InlineKeyboardMarkup([[btn1, btn2]]))

    check = await Data.is_in_db(message.from_user.id)
    if check == False:
        await Data.add_new_user(message.from_user.id)

    

@app.on_message(link_filter)
@joined()
async def options(client, message : Message):
    print(message.text)
    await message.reply("What would like to do?", 
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Download", f"d_{message.text}"), InlineKeyboardButton("Watch Video",url=message.text)]
            ])
            )

def humanbytes(size):
    """Convert Bytes To Bytes So That Human Can Read It"""
    if not size:
        return ""
    power = 2 ** 10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


def edit_msg(client, message, to_edit):
    try:
        client.loop.create_task(message.edit(to_edit))
    except MessageNotModified:
        pass
    except FloodWait as e:
        client.loop.create_task(asyncio.sleep(e.x))
    except TypeError:
        pass


def download_progress_hook(d, message, client):
    if d['status'] == 'downloading':
        current = d.get("_downloaded_bytes_str") or humanbytes(int(d.get("downloaded_bytes", 1)))
        total = d.get("_total_bytes_str") or d.get("_total_bytes_estimate_str")
        file_name = d.get("filename")
        eta = d.get('_eta_str', "N/A")
        percent = d.get("_percent_str", "N/A")
        speed = d.get("_speed_str", "N/A")
        to_edit = f"<b><u>Downloading File</b></u> \n<b>File Name :</b> <code>{file_name}</code> \n<b>File Size :</b> <code>{total}</code> \n<b>Speed :</b> <code>{speed}</code> \n<b>ETA :</b> <code>{eta}</code> \n<i>Downloaded {current} out of {total}</i> (__{percent}__)"
        threading.Thread(target=edit_msg, args=(client, message, to_edit)).start()


@app.on_callback_query(filters.regex("^d"))
async def download_video(client, callback : CallbackQuery):
    url = callback.data.split("_",1)[1]
    msg = await callback.message.edit("Downloading...")
    user_id = callback.message.from_user.id

    if user_id in active_list:
        await callback.message.edit("Sorry! You can download only one video at a time")
        return
    else:
        active_list.append(user_id)

    ydl_opts = {
            #'format': 'best',
            #'outtmpl': "downloads", 
            # 'nooverwrites': True,
            # 'no_warnings': False,
            # 'ignoreerrors': True,
            "progress_hooks": [lambda d: download_progress_hook(d, callback.message, client)]
        }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
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
            await callback.message.reply_video(f"{file}", caption="**Here Is your Requested Video**\n@SJ_Bots",
                                reply_markup=InlineKeyboardMarkup([[btn1, btn2]]))
            os.remove(f"{file}")
            break
        else:
            continue

    await msg.delete()
    active_list.remove(user_id)


@app.on_message(filters.command("cc"))
async def download_video(client, message : Message):
    files = os.listdir("downloads")
    await message.reply(files)

@app.on_message(filters.command("broadcast") & filters.reply)# & filters.user([-1048643192, -1903946976]))
async def stats(client, message : Message):
    users = await Data.get_user_ids()
    tmsg = message.reply_to_message.text.markdown

    msg = await message.reply("Broadcast started")

    fails = 0
    success = 0

    for user in users:
        try:
            await app.send_message(int(user), tmsg)
            success += 1
        except:
            fails += 1

        quotient = (fails + success)/len(users)
        percentage = float(quotient * 100)
        await msg.edit(f"**Broadcast started**\n\nTotal Users : {len(users)}\nProgress : {percentage} %")

    await msg.edit(f"Broadcast Completed**\n\nTotal Users : {len(users)}\nSuccess : {success}\nFails : {fails}")


@app.on_message(filters.command("stats"))# & filters.user([-1048643192, -1903946976]))
async def stats(client, message : Message):
    count = await Data.count_users()
    await message.reply(f"**STATS**\nTotal Users : {count}")




app.run()
