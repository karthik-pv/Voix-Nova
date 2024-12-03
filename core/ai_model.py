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
        api_key = "AIzaSyC8FH1VvPdSgZ50w5NdsStIf7xGeEI9-yA"
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

    def basic_salesman_prompt(self, query, product_details, page_visit_log):
        prompt = (
            "You are an enthusiastic and an energetic salesman who constantly answers to user's queries. "
            + f"These are all the product details - {product_details}"
            + "Use these details to answer any query the user has. "
            + f"This is the users activity so far - {page_visit_log}. "
            + "Keeping the users activity in mind give an appropriate response to his query. "
            + f"The users query is - {query}."
        )
        result = self.chat.send_message(prompt)
        response = result.candidates[0].content.parts[0].text
        return response

    def home_page(self, page_visit_log):
        prompt = (
            "You are an enthusiastic and energetic salesman who is eager to help users. "
            + "The user is currently in the home page. "
            + "Ask him if he has something in mind or whether he would like some recommendations. "
            + "I am passing a log of the users activity, keep that in mind while giving a response. "
            + "If it is first time in the home page, introduce yourself as nova. "
            + "If this is not his first time in the home page, handle it accordingly. Use his activity details to give a customised response. "
            + f"USER ACTIVITY LOG - {page_visit_log}. "
            + "Make sure your response only contains things the salesman would say, and give a short response. "
            + "I will be reading this out for the user. "
        )
        result = self.chat.send_message(prompt)
        response = result.candidates[0].content.parts[0].text
        return response

    def product_list_page(self, query, page_visit_log):
        prompt = (
            "You are an enthusiastic and energetic salesman who is eager to help users. "
            + f"The user is currently in the product list page and is looking for {query}."
            + "Ask the user whether he wants to filter products, or whether he wants to know more about a particular product. "
            + "I am passing a log of the users activity, keep that in mind while giving a response. "
            + "If this is not his first time in the page, handle it accordingly. Use his activity details to give a customised response. "
            + "Refer an item that he has searched for before and make other recommendations. "
            + f"USER ACTIVITY LOG - {page_visit_log}. "
            + "Make sure to give a very short reply, the way the salesman would. "
            + "I will be reading this out for the user. "
        )
        result = self.chat.send_message(prompt)
        response = result.candidates[0].content.parts[0].text
        return response

    def filtering_interaction(self, query, current_filters, page_visit_log):
        prompt = (
            "The user is trying to filter the products that are visible to him. "
            + f"He is trying to filter in this manner - '{query}'. "
            + f"The filters currently implemented are - '{current_filters}'. "
            + "If this is not his first time filtering, handle it accordingly. Use his activity details to give a customised response. "
            + "Mention that he had filtered by some filters before, and ask that whether he wants to apply those filters again. "
            + f"USER ACTIVITY LOG - {page_visit_log}. "
            + "If his statement includes a category of filters, then mention that you have filtered according to this category. "
            + "Offer to filter according to the remaining categories he hasn't filtered by yet. "
            + "The categories of filters available are colors, categories, gender and fit. "
        )
        result = self.chat.send_message(prompt)
        response = result.candidates[0].content.parts[0].text
        return response

    def product_details_page(self, query, page_visit_log):
        prompt = (
            "You are an enthusiastic and energetic salesman who is eager to help users. "
            + f"The user is searching for this item in particular - {query}. "
            + "Ask the user whether he wants more details about the product or whether he wants to add the item to the cart. "
            + "If this is not his first time in the page, handle it accordingly. Use his activity details to give a customised response. "
            + f"USER ACTIVITY LOG - {page_visit_log}. "
            + "Make sure to give a short reply, the way the salesman would. "
            + "I will be reading this out for the user. "
        )
        result = self.chat.send_message(prompt)
        response = result.candidates[0].content.parts[0].text
        return response

    def product_description(self, query, page_visit_log):
        print(tfidf_search(query))
        data = str(tfidf_search(query)["results"][0])
        prompt = (
            "You are an enthusiastic and energetic salesman who is eager to help users. "
            + "The user wants to know more about a particular product. "
            + f"These are the details of the product - {data}. "
            + "Give a good explanation of the product based on the given data. "
            + "If this is not his first time in the page, handle it accordingly. Use his activity details to give a customised response. "
            + "Mention a product that he searched up before and suggest that the current product goes well with that, or other similar salesman tactics. "
            + f"USER ACTIVITY LOG - {page_visit_log}. "
            + "Make sure to give a concise description. "
            + "I will be reading this out for the user."
        )
        result = self.chat.send_message(prompt)
        response = result.candidates[0].content.parts[0].text
        return response

    def checkout_cart(self, cost):
        prompt = (
            "You are an enthusiastic and energetic salesman who is eager to help users. "
            + "The user wants to finalise and checkout his cart. "
            + f"The cost for all his products is - {cost}. "
            + "Ask the user for his address and say the shipment will happen there. "
            + "Speak the way a salesman would and keep it short. "
            + "I will be reading out your response to the user. "
        )
        result = self.chat.send_message(prompt)
        response = result.candidates[0].content.parts[0].text
        return response

    def recommendation_page(self, recommended_products, page_visit_log):
        prompt = (
            "You are an enthusiastic and energetic salesman who is eager to help users. "
            + "The user is in the recommendation page. "
            + "These are the products that he will be recommended on screen. "
            + f"PRODUCT DETAILS - {recommended_products}. "
            + "If this is not his first time asking for recommendations, handle it accordingly. Use his activity details to give a customised response. "
            + f"USER ACTIVITY LOG - {page_visit_log}. "
            + "Talk about the top 3 products in brief. "
            + "Give a short and crisp response. "
            + "I will read out your response to the user. "
        )
        result = self.chat.send_message(prompt)
        response = result.candidates[0].content.parts[0].text
        return response

    def cart_page(self, cart_products, recommended_products, page_visit_log):
        prompt = (
            "You are an enthusiastic and energetic salesman who is eager to help users. "
            + "The user is in the cart page. "
            + f"These are the products in his cart - {cart_products}. "
            + f"Tell him that goin by the products in his cart, these are good products to buy, and recommend products from these - {recommended_products}. "
            + "If this is not his first time in the cart page, handle it accordingly. Use his activity details to give a customised response. "
            + f"USER ACTIVITY LOG - {page_visit_log}. "
            + "After that ask him whether he wants to checkout and finalise. "
            + "Speak the way a salesman would and keep it short. "
            + "I will be reading out your response to the user. "
        )
        result = self.chat.send_message(prompt)
        response = result.candidates[0].content.parts[0].text
        return response
