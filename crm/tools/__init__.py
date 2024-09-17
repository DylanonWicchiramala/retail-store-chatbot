# %%
## Document vector store for context
from langchain_core.tools import tool
## For database search tool
from crm.tools.customer_data import (
    get_customer_information,
    save_customer_information
)


get_customer_information = tool(get_customer_information)
save_customer_information = tool(save_customer_information)

all_tools = [
    get_customer_information,
    save_customer_information,
    ]    