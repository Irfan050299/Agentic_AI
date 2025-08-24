from ddgs import DDGS
from langchain.tools import tool
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime
import requests
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatGoogleGenerativeAI(model = 'gemini-2.5-flash-lite', temperature = 0)


#******************* DuckDuckGo Search Tool****************
@tool
def generate_resonse(query: str) -> str:
    """
    Performs a DuckDuckGo search for the given query and returns results as text.
    """
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=3):
            results.append(f"- {r['title']}: {r['href']}")
    return "\n".join(results)



#**************** Currency Exchanger Tool****************

access_key = "ca0bdebd11fd15e1110ef770b1382625"
@tool
def converter(query: str) -> str:
    """
    Give me the current inr value of the given query
    """
    try:
        parts = query.split()
        # if len(parts) != 2:
        #     return "Format galat hai. Example: '10 USD'"

        amount = float(parts[0])
        from_currency = parts[1].upper()
        to_currency = "INR"

        # Free plan: always source=USD
        url = f"http://api.currencylayer.com/live?access_key={access_key}&currencies={from_currency},{to_currency}&source=USD&format=1"
        response = requests.get(url)
        data = response.json()

        if data.get("success"):
            usd_to_inr = data["quotes"].get("USDINR")

            # Special case: if from_currency == USD
            if from_currency == "USD":
                converted = amount * usd_to_inr
                return f"{amount} {from_currency} = {converted:.2f} {to_currency}"

            usd_to_from = data["quotes"].get(f"USD{from_currency}")

            if usd_to_from and usd_to_inr:
                rate = usd_to_inr / usd_to_from
                converted = amount * rate
                return f"{amount} {from_currency} = {converted:.2f} {to_currency}"
            else:
                return "Conversion rate not found."
        else:
            return f"Error: {data}"

    except Exception as e:
        return f"Error: {str(e)}"
    


# **********Current Time and Date Tool***************
@tool
def datetime_tool(query: str = "") -> str:
    """
    Returns the current date, time, or both based on the query.
    Example queries:
    - 'date' → 23 August 2025
    - 'time' → 13:45:32
    - 'datetime' → 23 August 2025, 13:45:32
    """
    try:
        now = datetime.now()

        if query.lower() == "date":
            return now.strftime("%d %B %Y")  # e.g., 23 August 2025
        elif query.lower() == "time":
            return now.strftime("%H:%M:%S")  # e.g., 13:45:32
        elif query.lower() in ["datetime", "date time"]:
            return now.strftime("%d %B %Y, %H:%M:%S")  # e.g., 23 August 2025, 13:45:32
        else:
            return (
                "Invalid query. Use 'date', 'time', or 'datetime'."
            )
    except Exception as e:
        return f"Error: {str(e)}"
    

# *************** Joke Generator Tool*************
@tool
def joke_generator(query: str) -> str:
    """
    Generate joke about the given topic
    """
    prompt = ChatPromptTemplate(f"Plese generate two lines of joke about {query}")
    formatted_prompt = prompt.format(topic=query)
    response = llm.invoke(formatted_prompt)
    return response.content

#******************* 2. Tools list**************** 
tools = [generate_resonse, converter, datetime_tool,joke_generator]

from langchain.agents import initialize_agent, AgentType

# ------------------------------
# ******************** Memory *********************
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# *****************Agent initialize****************

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)

    
