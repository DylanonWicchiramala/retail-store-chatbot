# %%
## Document vector store for context
from langchain_core.tools import tool
## For database search tool
from crm.tools.customer_data import (
    get_customer_information_by_id,
    save_customer_information
)
from crm.tools.retail_store_data import (
    search_retail_store
)


save_customer_information = tool(save_customer_information)
get_customer_information_by_id = tool(get_customer_information_by_id)
search_retail_store=tool(search_retail_store)

all_tools = [
    save_customer_information,
    get_customer_information_by_id,
    search_retail_store,
    ]    