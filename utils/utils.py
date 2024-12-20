import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    raise RuntimeError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model once at module level
MODEL_NAME = 'gemini-pro'
model = None
try:
    model = genai.GenerativeModel(MODEL_NAME)
    logger.info("Gemini Model initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Gemini model: {e}")
    logger.error(f"Please make sure the API Key is correct and the Gemini API is reachable")
    
def get_gemini_embeddings(text: str):
    try:
        if model is None:
           logger.error("Gemini Model is not initialized")
           return None
        
        gemini_embedding = model.embed_content(
            content = text,
            model = "models/embedding-001"
        ).embedding.values
        return gemini_embedding
    except Exception as e:
      logger.error(f"Error generating embedding: {e}")
      return None

def generate_gemini_response(prompt: str, generation_config:dict = None) -> str:
    try:
        if model is None:
            logger.error("Gemini Model is not initialized")
            return None
        if generation_config is None:
           generation_config = {
               "temperature": 1,
               "top_p": 0.8,
               "top_k": 40,
               "max_output_tokens": 800
           }

        response = model.generate_content(
            contents=[
                {
                    "role": "user",
                    "parts": prompt
                }
            ],
            generation_config=generation_config
        )
        logger.info("Gemini response generated successfully!")
        return response.text if response.text else ""

    except Exception as e:
      logger.error(f"Error generating response: {e}")
      return ""