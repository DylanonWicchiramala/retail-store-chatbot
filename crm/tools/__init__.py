# %%
## Document vector store for context
from copy import copy
from langchain_core.tools import tool
## For database search tool
from crm.database.customer_data import (
    get_customer_information_by_id,
    save_customer_information as __save_customer_information,
    CustomerInformationInput
)
from crm.tools.retail_store_data import (
    search_retail_store
)

CURRENT_USER_ID:int = None


def set_current_user_id(user_id:str):
    global CURRENT_USER_ID
    CURRENT_USER_ID = user_id
    return CURRENT_USER_ID


def get_current_user_id():
    id = copy(CURRENT_USER_ID)
    return id


def save_customer_information(input_dict:CustomerInformationInput):
    """ this function to save customers persona data and interests into the databases.
        when no field required, do not pass parameter string of "None" or "Unknown".
    """
    global CURRENT_USER_ID
    return __save_customer_information(input_dict=input_dict, user_id=CURRENT_USER_ID)


save_customer_information = tool(save_customer_information)
get_customer_information_by_id = tool(get_customer_information_by_id)
search_retail_store=tool(search_retail_store)

all_tools = [
    save_customer_information,
    get_customer_information_by_id,
    search_retail_store,
    ]    