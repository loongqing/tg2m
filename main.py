from telethon import custom, TelegramClient
import asyncio
import traceback
import time
from telethon.tl.functions.channels import JoinChannelRequest
import log
import sqlite3
import matrix

session = 'printer'
api_id = 0
api_hash = ""
homeserver = ""
username = ""
passwd = ""

clientm = matrix.Matrix(homeserver, username, passwd)
clientm.login()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = TelegramClient(session, api_id, api_hash, loop=loop).start()
db = sqlite3.connect("tg2m")


def handleMessage(clientm: matrix.Matrix, event: custom.Message):
    id = event.from_id
    cursor = db.execute("SELECT * FROM tablemap WHERE `targetid` = ?", [id])
    for row in cursor:
        clientm.send_message(row[3], event.message)
        event.mark_read()


async def main(clientm: matrix.Matrix):
    global client
    dialogs = await client.get_dialogs()
    for i in dialogs:
        unreadc = i.unread_count
        try:
            result = await client.get_messages(i, limit=unreadc)
        except:
            await client.send_message(-1001788712066, str(i.id))
            continue
        for j in result:
            handleMessage(clientm, j)


async def try_subscribe(clientm: matrix.Matrix):
    cursor = db.execute("SELECT * FROM tablemap WHERE `prepare_finished` = 0")
    for row in cursor:
        try:
            ent = await client.get_entity(row[2])
            await client(JoinChannelRequest(ent))
        except:
            await clientm.send_message(row[3], traceback.format_exc() + "\nCant subscribe this channel.")
            await clientm.client.room_leave(row[3])
            db.execute("DELECT FROM tablemap WHERE `id` = ?", [row[0]])
            continue
        db.execute("UPDATE tablemap set `prepare_finished` = 1, `targetid` = ? WHERE `id` = ?", [ent.id,row[0]])
        await clientm.send_message(row[3], "subscribed. now listener is waiting for message!")


def start():
    global client, clientm
    while True:
        with client:
            try:
                client.loop.run_until_complete(try_subscribe(clientm))
                client.loop.run_until_complete(main(clientm))
            except:
                traceback.print_exc()
                log.logger.error(traceback.format_exc())
                client.loop.run_until_complete(client.send_message(-1001788712066,
                                                                   "#paicatchbot #documentHandle #handleException " + traceback.format_exc()))
        time.sleep(600)
