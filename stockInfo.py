import json
import time
import os
from bs4 import BeautifulSoup
import re
import requests

from langchain.llms import OpenAI
from langchain.agents import load_tools, AgentType, Tool, initialize_agent
import yfinance as yf

import openai
import warnings
warnings.filterwarnings("ignore")

OpenAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if OpenAI_API_KEY:
    pass
else:
    print("No API key provided")

llm = OpenAI(temperature=0,
             model_name="gpt-3.5-turbo-16k-0613")

# Fetch stock data from Yahoo Finance
def get_stock_price(ticker, history=5):
    
    time.sleep(5) # Avoiding the rate limit
    if "." in ticker:
        ticker = ticker.split(".")[0]
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")
    df = df[["Close", "Volume"]]
    df.index = [str(x).split()[0] for x in list(df.index)]
    df.index.rename("Date", inplace=True)
    df = df[-history:]

    return df.to_string()  

# Scrape Google for recent news
def google_query(search_term):
    if "news" not in search_term:
        search_term = search_term + " stock news"
    url = f"https://www.google.com/search?q={search_term}"
    url = re.sub(r"\s", "+", url)
    return url

def get_recent_stock_news(company_name):
    time.sleep(5) #Avoid rate limit 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}

    g_query = google_query(company_name)
    res = requests.get(g_query, headers=headers).text
    soup = BeautifulSoup(res, "html.parser")
    news = []
    for n in soup.find_all("div", "n0jPhd ynAwRc tNxQIb nDgy9d"):
        news.append(n.text)
    for n in soup.find_all("div", "IJl0Z"):
        news.append(n.text)

    if len(news) > 10:
        news = news[:10]
    else:
        news = news
    news_string = ""
    for i, n in enumerate(news):
        news_string += f"{i}. {n}\n"
    top10_news = "Recent News:\n\n" + news_string

    return top10_news

# Yahoo Finance to get financial statements
def get_financial_statements(ticker):
    time.sleep(5) #Avoid rate limit
    if "." in ticker:
        ticker = ticker.split(".")[0]
    else:
        ticker = ticker
    company = yf.Ticker(ticker)
    balance_sheet = company.balance_sheet
    if balance_sheet.shape[1] >= 3:
        balance_sheet = balance_sheet.iloc[:, :3]  # Remove 4th years data
    balance_sheet = balance_sheet.dropna(how="any")
    balance_sheet = balance_sheet.to_string()
    return balance_sheet



function = [
    {
        "name": "get_company_Stock_ticker",
        "description": "This will get the stock ticker of the company",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker_symbol": {
                    "type": "string",
                    "description": "This is the stock symbol of the company.",
                },

                "company_name": {
                    "type": "string",
                    "description": "This is the name of the company given in query",
                }
            },
            "required": ["company_name", "ticker_symbol"],
        },
    }
]


def get_stock_ticker(query):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[{
            "role": "user",
            "content": f"Given the user request, what is the comapany name and the company stock ticker ?: {query}?"
        }],
        
        functions=function,
        function_call={"name": "get_company_Stock_ticker"},
    )
    message = response["choices"][0]["message"]
    arguments = json.loads(message["function_call"]["arguments"])
    company_name = arguments["company_name"]
    company_ticker = arguments["ticker_symbol"]
    return company_name, company_ticker


def stockAnalyzer(query):
    
    Company_name, ticker = get_stock_ticker(query)
    print({"Query": query, "Company_name": Company_name, "Ticker": ticker})
    stock_data = get_stock_price(ticker, history=10)
    stock_financials = get_financial_statements(ticker)
    stock_news = get_recent_stock_news(Company_name)

    available_information = f"Stock Price: {stock_data}\n\nStock Financials: {stock_financials}\n\nStock News: {stock_news}"
    

    
    analysis = llm(f"Give detail stock analysis, Use the available data and provide investment recommendation. \
             The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer \
             User question: {query} \
             You have the following information available about {Company_name}. Write (5-8) pointwise investment analysis to answer user query, At the end conclude with proper explaination.Try to Give positives and negatives  : \
              {available_information} "
                   )
    

    return analysis
