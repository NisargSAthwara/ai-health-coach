from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config.settings import GEMINI_API_KEY

# Initialize the Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY)

# You can add other client-related configurations or helper functions here if needed

def get_llm():
    """Returns the initialized LLM client."""
    return llm