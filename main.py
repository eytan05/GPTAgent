from autogptagent import AutoGPTAgent
from dotenv import load_dotenv
import os


def main():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    agent = AutoGPTAgent(api_key)
    user_input = input()
    agent.handle_request(user_input)

if __name__ == "__main__":
    main()
