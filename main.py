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
    
## flight agent node
def flight_agent(state:TravelState):
    query = state["user_query"]
    flight_data = search_flights(query)
    return{
        "flight_results":flight_data,
        "messages":[
            AIMessage(content=f"Flight results fetched")
        ],
        "llm_calls":state.get("llm_calls",0)+1
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
    Create a travel itinerary
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
    Generate final travel response.
    Flights:
    {state['flight_results']}
    Hotels:
    {state['hotel_results']}
    Itinerary:
    {state['itinerary']}
    """
    response = llm.invoke(
        [
            HumanMessage(content=final_prompt)
        ]
    )
    return {
        "messages":[response],
        "llm_calls":state.get("llm_calls",0)+1
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
    user_input = input("enter travel requests: ")
    result = app.invoke(
        {
            "messages":[
                HumanMessage(content=user_input)
            ],
            "user_query":user_input,
            "flight_results":"",
            "hotel_results":"",
            "itinerary":"",
            "llm_calls":0
                },
        config=config
    )
    print("\n FINALRESPONSE:\n")
    for msg in result["messages"]:
        print(msg.content)