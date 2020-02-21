from aiovk.longpoll import BotsLongPoll

from base import BaseBot
from bot.processor import Processor
from bot.events import VKEvent
from utils import split_message


MESSAGE_LEN_THRESHOLD = 500


class VKBot(BaseBot):
    def __init__(self, token: str, pg_user: str, pg_password: str, pg_database: str, pg_host: str):
        super().__init__(token, pg_user, pg_password, pg_database, pg_host)

        self._longpoll = BotsLongPoll(self._api, mode=[2, 8], group_id=185597155)
        self._pr = Processor()

    async def run(self):
        while True:
            updates = (await self._longpoll.wait())['updates']
            for update in updates:
                print(update, '\n')
                event = VKEvent(update)
                # print(event, '\n')

                if event.msg_to_me:
                    reply, attachment = await self._pr.process(self._api, event.text.lower(), event.from_id)
                    replies = split_message(reply, MESSAGE_LEN_THRESHOLD)
                    for r in replies:
                        if event.to_chat:
                            await self.write_msg(person_id=event.from_id, response=r, chat_id=event.chat_id, attachment=attachment)
                        else:
                            await self.write_msg(person_id=event.from_id, response=r, attachment=attachment)


