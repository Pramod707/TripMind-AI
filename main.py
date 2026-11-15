import os
from typing import TypedDict,Annotated
import operator
import psycopg
from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import AnyMessage,AIMessage,SystemMessage,HumanMessage
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights
from dotenv import load_dotenv
load_dotenv()

##create agent
##plan a complete 5 days japan trip including flights , hotels , and sightseeing under 2lakhs.
llm = ChatGroq(
    model="openai/gpt-oss-120b"
)
 
DATABASE_URL = os.getenv("DATABASE_URL")

class TravelState(TypedDict):
    messages : Annotated[list[AnyMessage],add_messages]
    user_query:str
    flight_results : str
    hotel_results : str
    itinerary:str
    llm_calls:int
    
def extract_airport_codes(query):
    prompt = f"""
    Extract the departure and destination airport IATA codes
    from this travel request:

    {query}

    Return only two airport codes separated by a comma.

    Example: HYD,LHR

    If a country is mentioned instead of a city,
    select a major international airport in that country.

    Do not include explanations.
    """

    response = llm.invoke(prompt)

    departure, arrival = response.content.strip().split(",")

    return departure.strip(), arrival.strip()
## flight agent node
def flight_agent(state: TravelState):

    query = state["user_query"]

    try:
        departure, arrival = extract_airport_codes(query)
        flight_data = search_flights(query, departure, arrival)

        if not flight_data:
            flight_data = {
                "status": "unavailable",
                "message": "No flight information returned by the API."
            }

        print("FLIGHT DATA:", flight_data)

        return {
            "flight_results": flight_data,
            "messages": [
                AIMessage(
                    content="Flight search completed."
                )
            ]
        }

    except Exception as e:

        print("FLIGHT AGENT ERROR:", str(e))

        return {
            "flight_results": {
                "status": "error",
                "message": str(e)
            },
            "messages": [
                AIMessage(
                    content="Flight information could not be retrieved."
                )
            ]
        }

## hotel agent node 
def hotel_agent(state: TravelState):
    query = f"Best Hotels for {state['user_query']}"
    hotel_result = tavily_search(query)
    return {
        "hotel_results":hotel_result,
        "messages":[
            AIMessage(content="Hotel information fetched")
        ],
        "llm_calls":state.get("llm_calls",0)+1
    }
    
## itinerary agent node
def itinerary_agent(state: TravelState):
    prompt = f"""
    IMPORTANT:
Create only ONE practical itinerary.

Use the provided flight and hotel data.

Respect the user's total travel budget.

Do not invent flight schedules, hotel availability,
or verified prices.

If the trip is not feasible within the budget,
explain the limitation clearly.

Avoid suggesting alternative itineraries unless
the user specifically requests them.
    User Query:
    {state['user_query']}
    Flight Results:
    {state['flight_results']}
    Hotel Results:
    {state['hotel_results']}    
    """ 
    response = llm.invoke([
        SystemMessage(
            content="You are an expert travel planner"
        ),
        HumanMessage(content=prompt)
    ])
    
    return{
        "itinerary":response.content,
        "messages":[response],
        "llm_calls":state.get("llm_calls",0)+1
    }
    
## final agent node
def final_agent(state: TravelState):

    final_prompt = f"""
    You are TripMind AI, an expert AI travel planning assistant.

    Your task is to generate ONE best travel plan based on
    the user's requirements.

    USER REQUEST:
    {state['user_query']}

    FLIGHT DATA:
    {state.get('flight_results', 'Not available')}

    HOTEL DATA:
    {state.get('hotel_results', 'Not available')}

    GENERATED ITINERARY:
    {state.get('itinerary', 'Not available')}

    STRICT INSTRUCTIONS:

    1. Recommend ONLY ONE best travel plan.
       Do not generate Option A, Option B, or alternatives.

    2. Respect the user's requested:
       - Destination
       - Departure city
       - Travel dates
       - Number of travelers
       - Total budget

    3. FLIGHT SELECTION:
       - Select ONE best flight based on available flight data.
       - Include airline, flight number, departure,
         arrival, duration, and price when available.
       - Never invent flight numbers, schedules, or fares.
       - If verified flight details are missing,
         clearly state "Flight details unavailable".

    4. HOTEL SELECTION:
       - Recommend ONE best hotel.
       - Include hotel name, location, estimated nightly
         price, and total accommodation cost.
       - Never claim availability unless verified.

    5. BUDGET:
       - Calculate the estimated total trip cost.
       - Include flights, hotels, food, transportation,
         sightseeing, and other relevant expenses.
       - Do not claim the trip fits the budget unless
         the calculations support that conclusion.
       - If the budget is insufficient, explain the
         shortfall rather than inventing cheaper prices.

    6. ITINERARY:
       - Provide a day-by-day travel itinerary.
       - Include morning, afternoon, and evening activities.
       - Recommend practical sightseeing locations.
       - Avoid unnecessary travel between distant cities.

    7. OUTPUT FORMAT:

       # TripMind AI — Recommended Travel Plan

       ## Trip Overview
       ## Recommended Flight
       ## Recommended Hotel
       ## Day-by-Day Itinerary
       ## Estimated Budget Breakdown
       ## Important Travel Information

    8. Do not present multiple travel options.
       Do not invent live prices or confirmed bookings.
       Make the response professional, clear, and concise.
    """

    response = llm.invoke([
        SystemMessage(
            content="You are TripMind AI, a professional travel planning assistant."
        ),
        HumanMessage(content=final_prompt)
    ])

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

## creating the graph

graph = StateGraph(TravelState)
## adding nodes
graph.add_node("flight_agent",flight_agent)
graph.add_node("hotel_agent",hotel_agent)
graph.add_node("itinerary_agent",itinerary_agent)
graph.add_node("final_agent",final_agent)
## adding edges
graph.add_edge(START,"flight_agent")
graph.add_edge("flight_agent","hotel_agent")
graph.add_edge("hotel_agent","itinerary_agent")
graph.add_edge("itinerary_agent","final_agent")
graph.add_edge("final_agent",END)

## databse connection postgress
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is missing. Check your .env file."
    )
_conn = psycopg.connect(
    DATABASE_URL,
    autocommit=True
)
checkpointer = PostgresSaver(_conn)
checkpointer.setup()

##compilation of the graph
app = graph.compile(checkpointer=checkpointer)

if __name__ =="__main__":
    config={
        "configurable":{
            "thread_id":"user_pramod"
        }
    }
    # user_input = input("enter travel requests: ")
    # result = app.invoke(
    #     {
    #         "messages":[
    #             HumanMessage(content=user_input)
    #         ],
    #         "user_query":user_input,
    #         "flight_results":"",
    #         "hotel_results":"",
    #         "itinerary":"",
    #         "llm_calls":0
    #             },
    #     config=config
    # )
    # print("\n FINALRESPONSE:\n")
    # for msg in result["messages"]:
    #     print(msg.content)