import threading
import google.generativeai as genai
import logging

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
        return self._chat

    def get_detailed_description_of_product(self, relevant_data):
        prompt = (
            "I will be giving you the details of a product. "
            + "I want you to give a human friendly response, where you talk about the product as a human salesman. "
            + f"PRODUCT_DETAILS = {relevant_data}"
        )
        response = self.chat.send_message(prompt)
        reply = response._result.candidates[0].content.parts[0].text.strip()
        return reply

    def get_description_of_products(self, query, relevant_data):
        prompt = (
            "I will be giving you the details of a few products. "
            + "I want you to give a human friendly response, where you talk about the products as a human salesman. "
            + "Mention the top 3 products, no need to go beyond that . \n\n"
            + f"PRODUCT_DETAILS = {relevant_data}\n\n"
            + f"QUERY = {query}"
        )
        response = self.chat.send_message(prompt)
        reply = response._result.candidates[0].content.parts[0].text.strip()
        return reply
