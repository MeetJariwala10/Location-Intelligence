from langchain_community.utilities import SerpAPIWrapper
import os
from dotenv import load_dotenv
load_dotenv()

search = SerpAPIWrapper(serpapi_api_key=os.getenv("SERPAPI_API_KEY"))
response = search.run("what is famous in gujarat")
print(response)