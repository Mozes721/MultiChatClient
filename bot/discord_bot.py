from discord import Intents, Client, Message
from config.config_files import APIkeys
from model.llm import LLM

class DiscordBot:
    def __init__(self, bot_service):
        self.bot_service = bot_service
        self.bart_llm = LLM
        self.client = Client(intents=Intents.default())
      
        self.register_events()

    def register_events(self):
        @self.client.event
        async def on_ready():
            print(f'{self.client.user} is now running!')

        @self.client.event
        async def on_message(message: Message):
            if message.author == self.client.user:
                return

            user_message = message.content
            await self.send_message(message, user_message)

    def get_response(self, user_message: str) -> str:
        response = self.bart_llm.generate_response(user_message)
        return response

    async def send_message(self, message: Message, user_message: str) -> None:
        if not user_message:
            print("Message is empty")
            return
        
        is_private = user_message[0] == '?'
        user_message = user_message[1:] if is_private else user_message

        try:
            response = self.get_response(user_message)
            await message.author.send(response) if is_private else await message.channel.send(response)
        except Exception as e:
            print(f"Error sending message: {e}")

    def run(self):
        print(APIkeys.discordToken)
        self.client.run(APIkeys.discordToken)
