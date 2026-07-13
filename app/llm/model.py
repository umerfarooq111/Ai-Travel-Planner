from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import GOOGLE_API_KEY


model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3,
     streaming=True
)