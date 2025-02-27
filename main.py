# import os
# import subprocess
# from helper.bot_factory import BotFactory
# from helper.bot_service import BotService
# from api.requests import APIRequests
# from config.config_files import APIkeys
from model.llm import LLM

def main():
    llm = LLM()

    queries = [
        "What is the price of Apple?",
        "What is the price of AAPL?",
        "What is the price of BTC right now?",
        "Do you know the current price of bitcoin and where it is heading?",
        # "What is the current weather of New York?",
        # "What's the weather like in Berlin currently?"
    ]

    # for query in queries:
    #     print(f"Query: {query}")
    result = llm.generate_response("What is the price of Apple?")
    print(result)
    
    # if not False:
    #     # If not deployed, launch LocalBot via Streamlit
    #     local_bot_path = os.path.join(os.path.dirname(__file__), "bot", "local_bot.py")
    #     subprocess.run(["streamlit", "run", local_bot_path], check=True)
    # else:
    #     # If deployed, launch DiscordBot or any other bot
    #     api_requests = APIRequests()
    #     bot_service = BotService(api_requests)
        
    #     bot = BotFactory.create_bot(DEPLOYMENT, bot_service)

    #     if bot:
    #         bot.run()

if __name__ == "__main__":
    main()