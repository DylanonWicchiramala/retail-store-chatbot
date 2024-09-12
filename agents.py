from langchain_openai import ChatOpenAI
from tools import (
    find_place_from_text, 
    nearby_search, 
    nearby_dense_community, 
    search_population_community_household_expenditures_data,
    duckduckgo_search,
    restaurant_sale_projection,
    python_repl,
    all_tools
)
from langchain_core.messages import (
    AIMessage, 
    BaseMessage,
    ToolMessage
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import operator
from typing import Annotated, Sequence, TypedDict, List
from prompt import (
    system_prompt,
    agent_meta as agents
)
import functools

llm = ChatOpenAI(
    model="gpt-4o-mini-2024-07-18", 
    temperature=0, 
    top_p=0, 
    )

## Create agents ------------------------------------------------------------------------
def create_agent(llm, tools, system_message: str):
    # memory = ConversationBufferMemory(memory_key='chat_history', return_messages=False)
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    
    # return llm without tools
    if tools:
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        #llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])
        llm = llm.bind_tools(tools)
    else:
        prompt = prompt.partial(tool_names="<no available tools for you>")
    
    agent = prompt | llm
    return agent


## create agent node
def agent_node(state, agent, name):
    result = agent.invoke(state)
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
        # result = AIMessage(**result.dict(), name=name)
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        "sender": name,
    }


## Define state ------------------------------------------------------------------------
# This defines the object that is passed between each node
# in the graph. We will create different nodes for each agent and tool
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    chat_history: List[BaseMessage]
    sender: str


agent_name = list(agents.keys())

analyst = agents['analyst']
data_collector = agents['data_collector']
reporter = agents['reporter']
    
analyst['node'] = create_agent(
        llm,
        [find_place_from_text, restaurant_sale_projection],
        system_message=analyst['prompt'],
    )

data_collector['node'] = create_agent(
        llm,
        [restaurant_sale_projection, search_population_community_household_expenditures_data, find_place_from_text, nearby_search, nearby_dense_community, duckduckgo_search] ,
        system_message=data_collector['prompt'],
    )

reporter['node'] = create_agent(
        llm,
        [],
        system_message=reporter['prompt'],
    )

analyst['node'] = functools.partial(agent_node, agent=analyst['node'], name='analyst')
data_collector['node'] = functools.partial(agent_node, agent=data_collector['node'], name='data_collector')
reporter['node'] = functools.partial(agent_node, agent=reporter['node'], name='reporter')