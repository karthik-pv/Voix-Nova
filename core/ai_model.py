import threading
import google.generativeai as genai
import logging
from .tfidf import tfidf_search
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class GeminiClient:
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    _chat = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(GeminiClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        api_key = "AIzaSyDj4YHEMjddEOTxlyfgdM4eu2glzCHQsFI"
        if not api_key:
            raise ValueError(
                "Gemini API key not found in settings or environment variables"
            )
        genai.configure(api_key=api_key)

        try:
            self.model = genai.GenerativeModel(model_name="gemini-1.5-flash", tools=[])
            self._initialized = True
        except Exception as e:
            logger.error(f"Error initializing Gemini models: {str(e)}")
            raise

    @property
    def chat(self):
        if self._chat is None:
            self._chat = self.model.start_chat(enable_automatic_function_calling=True)
        return self._chat

    def basic_salesman_prompt(self, query):
        prompt = """You are an enthusiastic and an energetic salesman who constantly 
                  provides responses to the user qoueries and answers to users dobts and questions using context from whatever you are provided below.
                  Rember that you are integrated as an AI voice assitat into an e commerce clothing store.
                  Keep the responses concise and energetic"""
        self.chat.send_message(prompt)

    def home_page(self):
        prompt = (
            "You are an enthusiastic and energetic salesman who is eager to help users. "
            + "If you havent seen this prompt before, Introduce yourself as NOVA, an AI assistant present to help the user. "
            + "The user is currently in the home page. "
            + "Ask him if he has something in mind or whether he would like some recommendations. "
            + "Make sure your response only contains things the salesman would say, and give a short response. "
            + "I will be reading this out for the user. "
        )
        result = self.chat.send_message(prompt)
        response = result.candidates[0].content.parts[0].text
        return response

    def product_list_page(self, query):
        prompt = (
            "You are an enthusiastic and energetic salesman who is eager to help users. "
            + f"The user is currently in the product list page and is looking for {query}."
            + "Ask the user whether he wants to filter products, or whether he wants to know more about a particular product. "
            + "Make sure to give a very short reply, the way the salesman would. "
            + "I will be reading this out for the user. "
        )
        result = self.chat.send_message(prompt)
        response = result.candidates[0].content.parts[0].text
        return response

    def filtering_interaction(self, query):
        prompt = (
            "The user is trying to filter the products that are visible to him. "
            + f"He is trying to filter in this manner - '{query}'"
            + "If his statement includes a category of filters, then mention that you have filtered according to this category. "
            + "Offer to filter according to the remaining categories. "
            + "The categories of filters available are colors, categories, gender and fit. "
        )
        result = self.chat.send_message(prompt)
        response = result.candidates[0].content.parts[0].text
        return response
