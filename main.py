import argparse
import subprocess
import sys

def run_discord():
    from bot.discord_bot import DiscordBot
    DiscordBot().run()

def run_streamlit():
    subprocess.run([sys.executable, "-m", "streamlit", "run", "bot/local_bot.py"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stock, Crypto & Weather Bot")
    parser.add_argument("--discord", action="store_true", help="Run Discord bot")
    parser.add_argument("--streamlit", action="store_true", help="Run Streamlit UI")
    args = parser.parse_args()
    
    if args.discord:
        run_discord()
    elif args.streamlit:
        run_streamlit()
    else:
        print("Usage: python main.py --discord")
        print("       python main.py --streamlit")
