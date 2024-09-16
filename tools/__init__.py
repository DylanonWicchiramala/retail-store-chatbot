# %%
## Document vector store for context
from langchain_core.tools import tool
import functools
from copy import copy
## For database search tool
from tools.retail_store_data import (
    search_retail_store
)
from tools.customer_data import (
    get_customer_information,
    save_customer_information
)

tools_outputs=""


def get_tools_output():
    global tools_outputs
    result = copy(tools_outputs)
    tools_outputs = ""
    return result


def save_tools_output(func):
    @functools.wraps(func) 
    def wrapper(*args, **kwargs):
        global tools_outputs
        # Call the original function and get its return value
        result = func(*args, **kwargs)
        # Append the result to tools_outputs
        tools_outputs += str(result) + "\n"
        # Return the original result
        return result
    return wrapper


get_customer_information = tool(get_customer_information)
save_customer_information = tool(save_customer_information)
search_retail_store = tool(search_retail_store)

all_tools = [
    get_customer_information,
    save_customer_information,
    search_retail_store,
    ]