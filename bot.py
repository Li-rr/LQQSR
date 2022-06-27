from mirai import Mirai,WebSocketAdapter,FriendMessage,Plain,GroupMessage
from mirai import Voice,MessageChain
from pathlib import Path

if __name__ == "__main__":
    bot = Mirai(
        qq=2155654750,
        adapter=WebSocketAdapter(
            verify_key="INITKEYXegd2lRo",host="127.0.0.1",port=8089
        )
    )

    @bot.on(FriendMessage)
    async def on_friend_message(event: FriendMessage):
        # voice = event.message_chain[Voice][0] # 一条消息只会包含一个语音
        # await voice.download(filename='./temps/1.silk')
        if str(event.message_chain) == '你好':
        
            await bot.send_friend_message(event.sender.id, [Plain('欢迎使用 YiriMirai。')])
            return bot.send(event, 'Hello, World!')

    @bot.on(GroupMessage)
    async def on_group_message(event: GroupMessage):
        # voice = event.message_chain[Voice][0] # 一条消息只会包含一个语音
        # await voice.download(filename='./temps/1.silk')
        if str(event.message_chain) == '黑黑':
            print(event)
            # await bot.send_friend_message(event.sender.id, [Plain('欢迎使用 YiriMirai。')])
            message_chain4 = MessageChain([
                await Voice.from_local('./temps/test_audio.silk')
            ])
            return bot.send(event,message_chain4)

    bot.run()