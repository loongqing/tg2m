import asyncio
from nio import AsyncClient, MatrixRoom, RoomMessageText
import re
import sqlite3
import markdown


class Matrix:
    def __init__(self,homeserver,username,passwd):
        self.homeserver=homeserver
        self.passwd=passwd
        self.username=username
        self.client = AsyncClient(self.homeserver, self.username)
        self.db=sqlite3.connect("tg2m")

    async def send_message(self, channel, message):
        await self.client.room_send(
            room_id=channel,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": message,
                "format": "org.matrix.custom.html",
                "formatted_body": markdown.markdown(message, extensions=['fenced_code', 'nl2br'])},
        )

    async def commandHandler(self,room:MatrixRoom,event:RoomMessageText):
        if re.search("/createmirror .+",event.body) != None:
            channelName=re.search("/createmirror .+",event.body)
            createdRoom = await self.client.room_create(name=channelName,federate=False,invite=[event.sender])
            self.db.execute("INSECT INTO tablemap (target, roomid) VALUES (?, ?)",[channelName,createdRoom.room_id])
            await self.send_message(createdRoom.room_id,"this room is waiting to be prepared.")


    async def messageHandler(self, room: MatrixRoom, event: RoomMessageText):
        if not isinstance(event,RoomMessageText):
            return
        if room.name == "TG2M Settings":
            await self.commandHandler(room,event)
            return


    async def login(self):
        await self.client.login(self.passwd)
        self.client.add_event_callback(self.messageHandler, RoomMessageText)
        await self.client.sync_forever(timeout=30000, full_state=True)