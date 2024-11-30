import threading
import google.generativeai as genai
import logging
from tfidf import tfidf_search
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
        api_key = "AIzaSyB5VNULcuxAjbppS2DPRyErxNd7jXiCky0"
        if not api_key:
            raise ValueError(
                "Gemini API key not found in settings or environment variables"
            )
        genai.configure(api_key=api_key)

        try:
            self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            self._initialized = True
        except Exception as e:
            logger.error(f"Error initializing Gemini models: {str(e)}")
            raise

    @property
    def chat(self):
        if self._chat is None:
            self._chat = self.model.start_chat(enable_automatic_function_calling=True)
            self._chat.send_message("")
        return self._chat

    def basic_salesman_prompt(self,query):
        prompt = ("""You are an enthusiastic and an energetic salesman who constantly 
                  provides responses to the user queries and answers to users dobts and questions using context from whatever you are provided below.
                  Rember that you are integrated as an AI voice assitat into an e commerce clothing store.
                  Keep the responses concise and energetic""")
        self.chat.send_message(prompt)

    # -------------------------------------------------------------------------------------------------------------------------------------------

    # HOME PAGE FUNCTIONS 

    def identify_searched_product_category(query):
        '''Identifies the category of products that the user is looking for'''
        url = "products/" + urlencode(query)
        return url