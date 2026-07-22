from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()

class AIResponse:
    def __init__(self, query, results):
        self.query = query
        self.results = results

        try:
            self.llm = ChatGoogleGenerativeAI(
            api_key = os.environ.get("GEMINI_API_KEY"),
            model="gemini-3.1-flash-lite",
            temperature=0.0,
            max_tokens=20000,
            max_retries=2
        )
        except Exception as e:
            print(f'\n\nError in initialising Google Gemini: \n\n{e}')
            raise RuntimeError("Error in loading Google Gemini")


    #prepare the context and return final_prompt
    def _prepare_context_and_prompt(self):
        """Helper method to parse matching documents and generate the final prompt structure."""
        try:
            context_chunks = []
            if self.results and ('matches' in self.results):
                for match in self.results['matches']:
                    text_data = match['metadata']['page_content']
                    text_string = " ".join(text_data) if isinstance(text_data, list) else text_data
                    context_chunks.append(text_string) 
                
            context = "\n\n".join(context_chunks)

            if not context:
                raise RuntimeError("No Relevant Context found on search to generate response!")
        
        except Exception as e:
            print(f"\n\nError in AIResponse Class at parsing context\n\n :{e}")
            raise RuntimeError(f"Error in Finding Relevant Context to Generate Response! \n{e}")
        
        try:
            template = ChatPromptTemplate.from_messages([
                (
                "system",
                "You are an expert financial analyst. Your task is to provide a comprehensive, "
                "detailed, and highly accurate synthesis of the retrieved financial documents "
                "in response to the user's query.\n\n"
                
                "CRITICAL INSTRUCTIONS FOR FINANCIAL ACCURACY:\n"
                "1. GROUNDING: Rely strictly on the provided context. If the retrieved documents do not "
                "contain the facts or figures necessary to answer a specific part of the query, explicitly "
                "state what information is missing. Do not make up or assume any financial metrics.\n"
                "2. DATA INTEGRITY: Retain exact numbers, percentages, currencies, dates, and fiscal periods "
                "(e.g., Q3 2025, FY2026). Do not round off values unless the source text does.\n"
                "3. ATTRIBUTION: Where possible, attribute findings to their source document or date mentioned "
                "in the text (e.g., 'According to the Q3 report...').\n"
                "4. NO SPECULATION: Differentiate clearly between historical facts/reported data and forward-looking "
                "statements or projections found in the text.\n\n"
                
                "RESPONSE STRUCTURE:\n"
                "- Executive Summary: A concise, high-level overview of what the relevant documents conclude regarding the query.\n"
                "- Detailed Financial Analysis: Break down the core findings into logical sub-sections or bullet points "
                "(e.g., Revenue Metrics, Market Trends, Risks/Headwinds) using data extracted from the context.\n"
                "- Discrepancies or Limitations: Note if different source documents contradict each other or if there is a glaring gap in the data."
                "End in a Positive Note"
                ),
                (
                    "user",
                    "Context:\n {context} \n\nQuestion:\n{question}"
                )
            ])

            return template.format_messages(question=self.query, context=context)
        
        except Exception as e:
            print(f"\n\nError in forming prompt template: \n\n{e}")
            raise RuntimeError("Error in forming prompt template")


    #generating the response
    def generate_ai_response_function(self):
        try:
            # Calling helper to retrieve final_prompt
            final_prompt = self._prepare_context_and_prompt()

            # Stream chunks from the model
            for chunk in self.llm.stream(final_prompt):
                content = chunk.content

                # Case 1: Gemini 3.x returns content as a list of dicts (text/metadata blocks)
                #To case 1 mein:- Stream ki Lists ki Dicts{metadata,text} ki text ko uthakar print karna hai
                if isinstance(content, list):
                    for block in content:
                        if (
                            isinstance(block, dict)
                            and block.get("type") == "text"
                        ):
                            text_val = block.get("text", "")
                            if text_val:
                                yield text_val

                # Case 2: Standard string response (older models or fallback format)
                elif isinstance(content, str):
                    if content:
                        yield content

        except Exception as e:
            print(
                f"\n\nError in AIResponse Class at generating response\n\n :{e}"
            )
            raise RuntimeError(
                f"Error in Finding Relevant Context to Generate Response!\n\nException:-{e}"
            )