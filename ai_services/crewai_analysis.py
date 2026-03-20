from crewai.flow.flow import Flow, listen, router, start, or_
from pydantic import BaseModel
from typing import Literal
from crewai import LLM
from crewai import LLM
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

class ChatbotState(BaseModel):
    user_query: str = ""
    user_query_lang: str = ""
    query_type: Literal[
        "legal",
        "non_legal"
    ] = "legal"
    
class QueryType(BaseModel):
    query_type: Literal[
        "legal",
        "non_legal"
    ] = "legal"
    
class CrewaiAnalysisFlow(Flow[ChatbotState]):
    def __init__(self, update_fn: str, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.update_fn = update_fn  
        
    @start()
    def know_user_query_type(self):
        self.update_fn("Determining query type")
        
        print("Starting the Flow")
        print(self.state.user_query)
        print("================")
        
        llm = LLM(model="gpt-4o", response_format=QueryType, temperature=0)
        response = llm.call(
			"Analyze the following input and determine whether the query is related to law or not. "
			"You are an assistant that classifies user queries. "
			"If the query is related to legal matters, return 'legal'. "
			"If the query is not related to legal matters, return 'non_legal'. "
			"Return the result in JSON format as {\"query_type\": <value>}. "
			f"Here is the user query: {self.state.user_query}"
		)
        print("Response from LLM:", response)
        print("User query type determined:", response.query_type)
        self.state.query_type = response.query_type
        
        # Detect language
        try:
            lang = detect(self.state.user_query)
        except:
            lang = "en"
        self.state.user_query_lang = lang
        
    
    @router(know_user_query_type)
    def decider(self):
        if self.state.query_type == "legal":
            return "legal"
        else:
            return "non_legal"

    @listen("non_legal")
    def handle_non_legal(self):   
        lang = self.state.user_query_lang
        if lang == "id":
            response_text = (
                "Maaf, saya hanya dapat menjawab pertanyaan yang berkaitan dengan hukum."
            )
        else:
            response_text = (
                "Sorry, I can only answer queries related to legal matters."
            )
        return response_text
    
    @listen("legal")
    def handle_legal(self):  
        self.update_fn("Formatting response")
        
        user_prompt = self.state.user_query
        llm = LLM(model="gpt-4o", max_tokens=600)
        lang = self.state.user_query_lang
        if lang == "id":
            prompt = (
                "Anda adalah asisten hukum profesional. "
                "Jawablah pertanyaan berikut secara jelas, tepat, dan berbasis hukum di Indonesia. "
                f"Pertanyaannya: {user_prompt}"
            )
        else:
            prompt = (
                "You are a professional legal assistant. "
                "Answer the following question clearly, accurately, and legally. "
                f"The question: {user_prompt}"
            )
        response = llm.call(prompt)
        return response
        
        