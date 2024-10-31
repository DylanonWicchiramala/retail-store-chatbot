from os.path import dirname, realpath, sep, pardir, curdir
import sys
from tabnanny import verbose

from deprecated import deprecated
sys.path.append(dirname(realpath(__file__)) + sep + pardir)

# load env ------------------------------------------------------------------------
import os
import crm.utils as utils

utils.load_env()
os.environ['LANGCHAIN_TRACING_V2'] = "false"


# debug ------------------------------------------------------------------
from langchain.globals import set_debug, set_verbose
set_verbose(True)
set_debug(False)

from langchain_core.messages import (
    AIMessage, 
    HumanMessage,
    ToolMessage
)
from langgraph.graph import END, StateGraph, START
from crm.agents import(
    AgentState,
    agent_metadata,
    agent_names
)
from crm.tools import all_tools, set_current_user_id
import crm.database.ads as ads
from crm.database.customer_data import get_customer_information_by_id, get_all_user_ids
from crm.database.chat_history import load_chat_history
from crm.database.persona import get_by_id as get_persona_by_id, get_all_persona_ids
from crm.ads_timing import save_user_active_time
from crm.create_persona import pipeline as create_persona_pipeline
from crm.push_ads import push_ads_pipeline, push_ads_pipeline_test

from langgraph.checkpoint.memory import MemorySaver

from datetime import datetime
import schedule
import time
import threading

## Define Tool Node
from langgraph.prebuilt import ToolNode
from typing import Literal

tool_node = ToolNode(all_tools)

def router(state) -> Literal["call_tool", "continue", "__end__"]:
    # This is the router
    messages = state["messages"]
    last_message = messages[-1]
    if "FINALANSWER" in last_message.content:
        return "__end__"
    if last_message.tool_calls:
        # The previous agent is invoking a tool
        return "call_tool"
    else:
        return "continue"


## CRM Workflow Graph ------------------------------------------------------------------------
crm_workflow = StateGraph(AgentState)

# add agent nodes
name = "crm_agent"
crm_workflow.add_node(name, agent_metadata[name]['node'])
    
crm_workflow.add_node("call_tool", tool_node)

crm_workflow.add_conditional_edges(
    name,
    router,
    {
        "call_tool": "call_tool",
        "__end__": END,
        "continue": END, 
        }
)

crm_workflow.add_conditional_edges(
    "call_tool",
    # Each agent node updates the 'sender' field
    # the tool calling node does not, meaning
    # this edge will route back to the original agent
    # who invoked the tool
    lambda x: x["sender"],
    {name:name},
)

crm_workflow.add_edge(START, name)


## creative_communication_agent Workflow Graph ------------------------------------------------------------------------
creative_communication_workflow = StateGraph(AgentState)

# add agent nodes
name = "creative_communication_agent"
creative_communication_workflow.add_node(name, agent_metadata[name]['node'])
    
creative_communication_workflow.add_node("call_tool", tool_node)

creative_communication_workflow.add_conditional_edges(
    name,
    router,
    {
        "call_tool": "call_tool",
        "__end__": END,
        "continue": END, 
        }
)

creative_communication_workflow.add_conditional_edges(
    "call_tool",
    # Each agent node updates the 'sender' field
    # the tool calling node does not, meaning
    # this edge will route back to the original agent
    # who invoked the tool
    lambda x: x["sender"],
    {name:name},
)

creative_communication_workflow.add_edge(START, name)
    

def __submitMessage(
    input:str, 
    workflow,
    user_id:str="test", 
    verbose:bool=False,
    recursion_limit:int=10
    ) -> str:
    
    set_current_user_id(user_id=user_id)
    
    graph = workflow.compile()

    events = graph.stream(
        {
            "messages": [f"user id: {user_id}", input],
            # "chat_history": input
        },
        # Maximum number of steps to take in the graph
        {"recursion_limit": recursion_limit},
    )
    
    if not verbose:
        events = [e for e in events]
        response = list(events[-1].values())[0]
    else:
        for e in events:
            a = list(e.items())[0]
            a[1]['messages'][0].pretty_print()
        
        response = a[1]
    
    response = response["messages"][0].content
    response = utils.format_bot_response(response, markdown=True)
    
    return response


def format_chat_history_to_str(history:list[AIMessage|HumanMessage])->str:
    history_str = ""
    for chat in history:
        if isinstance(chat, HumanMessage):
            history_str += "Human: "+ chat.content.strip() + "\n"
        if isinstance(chat, AIMessage):
            history_str += "AI: "+ chat.content[:50].replace("\n","\t").strip() + "...\n"
    
    if history_str:
        return history_str
    else:
        return "--Empty chat history--"


def listening_chat_history_from_db(user_id:str, after:datetime=None, verbose=False):
    """ Listening chat history from database then create a user personal data (such as hobbies, name, age, sex) in Customer database.
    """
    chat_history = load_chat_history(user_id=user_id, after=after)
    chat_history = format_chat_history_to_str(chat_history)
    bot_response = __submitMessage(input=chat_history, workflow=crm_workflow, user_id=user_id, verbose=verbose)

    return bot_response


def listening_chat_history(chat_history:list[AIMessage|HumanMessage], user_id:str, verbose=False):
    """ Listening chat history then create a user personal data (such as hobbies, name, age, sex) in Customer database.
    """
    chat_history = format_chat_history_to_str(chat_history)
    bot_response = __submitMessage(input=chat_history, workflow=crm_workflow, user_id=user_id, verbose=verbose)

    return bot_response


def create_personalized_ads(user_id:str, verbose=False):
    user_info = get_customer_information_by_id(user_id=user_id)
    user_info = str(user_info)
    bot_response = __submitMessage(input=user_info, workflow=creative_communication_workflow, user_id=user_id, verbose=verbose)
    ads.set(user_id=user_id, content=bot_response)
    return bot_response


def create_persona_ads(persona_id:str, verbose=False):
    persona = get_persona_by_id(persona_id=persona_id)
    persona_str = str(persona)
    bot_response = __submitMessage(input=persona_str, workflow=creative_communication_workflow, user_id='No ID', verbose=verbose)
    # add ads to user matches persooa.
    for user_id in persona['members']:
        ads.set(user_id=user_id, content=bot_response)
    return bot_response


def crm_pipeline(verbose=True):
    user_ids = get_all_user_ids()
    
    for user_id in user_ids:
        after = get_customer_information_by_id(user_id).get("latest_update")
        listening_chat_history_from_db(user_id=user_id, after=after, verbose=verbose)
        create_personalized_ads(user_id=user_id, verbose=verbose)
        save_user_active_time(user_id=user_id)
    
    # create ads for persona
    persona = create_persona_pipeline()
    for items in persona:
        persona_id = items['persona_id']
        # create_persona_ads(persona_id=persona_id)

    return
   
@deprecated("use google cloud scheduler.")
def schedule_crm_pipeline():
    def __crm_pipeline():
        crm_pipeline(verbose=True)
        
    schedule.every().day.at("09:00", tz = "Asia/Bangkok").do(__crm_pipeline)
    
    while True:
        schedule.run_pending()  # Check if scheduled task is due
        time.sleep(60)  # Wait before checking again
        

def run_pipelines():
    # Create a thread for the scheduling function
    ads_thread = threading.Thread(target=push_ads_pipeline)
    ads_thread.daemon = True  # Daemon threads exit when the main program exits
    ads_thread.start()
    
    ads_thread_test = threading.Thread(target=push_ads_pipeline_test)
    ads_thread_test.daemon = True  # Daemon threads exit when the main program exits
    ads_thread_test.start()
    
    crm_thread = threading.Thread(target=crm_pipeline)
    crm_thread.daemon = True  # Daemon threads exit when the main program exits
    crm_thread.start()
    