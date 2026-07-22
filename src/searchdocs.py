from tavily import TavilyClient
from dotenv import load_dotenv
load_dotenv()
import os
from langchain_core.documents import Document

class SearchDocs:
    def __init__(self,query):
        self.query = query
        self.tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY")) 

    def search_docs_tavily(self) ->list[Document]:
        try:
            response = self.tavily_client.search(
                query=self.query,
                search_depth="advanced",
                max_results=20,
                topic="finance",
            )

            search_results = response.get("results", []) #list[Dict]
            
            #all data retrieved in form of list[Document]
            docs_list = []

            for result in search_results:
                content = result.get("content","Null")
                url = result.get("url","unknown source") 

                doc = Document(
                        page_content=content,
                        metadata={
                            "source":url,
                            "query":self.query
                        }
                    )

                docs_list.append(doc)
            
            return docs_list

        except Exception as e:
            print(f"\n\nError in Tavily Document Search:\n\n {e}") #for debugging
            raise RuntimeError("Error in Searching the Documents from Web using Tavily!") #to show as an error to user if there's error