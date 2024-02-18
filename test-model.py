from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models import ChatAnyscale

chat = ChatAnyscale(model="meta-llama/Llama-2-70b-chat-hf", anyscale_api_key="<key>")

messages = [
    SystemMessage(
        content="You are a helpful AI that shares everything you know."
    )
]

while(True):
    user_input = input("User: ")
    messages.append(HumanMessage(content=user_input))
    res = chat(messages)
    messages.append(res)
    print("Bot: ", res.content)
