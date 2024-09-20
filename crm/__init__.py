# from os.path import dirname, realpath, sep, pardir, curdir
# import sys
# sys.path.append(dirname(realpath(__file__)) + sep + pardir)

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
import crm.database.ads as ads
from crm.tools import all_tools
from crm.database.customer_data import get_customer_information_by_id
from crm.database.chat_history import load_chat_history
from crm.ads_timing import save_user_active_time
from crm.create_persona import pipeline as persona_pipeline

from langgraph.checkpoint.memory import MemorySaver

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


def listening_chat_history_from_db(user_id:str, verbose=False):
    """ Listening chat history from database then create a user personal data (such as hobbies, name, age, sex) in Customer database.
    """
    chat_history = load_chat_history(user_id=user_id)
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
    persona = get_customer_information_by_id(user_id=user_id)
    persona = str(persona)
    bot_response = __submitMessage(input=persona, workflow=creative_communication_workflow, user_id=user_id, verbose=verbose)
    ads.set(user_id=user_id, content=bot_response)
    return bot_response


def pipeline():
    pass