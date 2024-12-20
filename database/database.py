import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_conversation_history(user_id: str, conversation_history: list, conversation_folder = "conversation_history"):
    """
    Saves the conversation history to a JSON file.
    """
    try:
        if not os.path.exists(conversation_folder):
            os.makedirs(conversation_folder)

        file_path = os.path.join(conversation_folder, f"{user_id}.json")
        with open(file_path, "w") as f:
            json.dump(conversation_history, f, indent=4)
        logger.info(f"Conversation history saved to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving conversation history: {e}")
        return False

def load_conversation_history(user_id: str, conversation_folder = "conversation_history") -> list:
     """
     Loads the conversation history from a JSON file.
     """
     try:
          file_path = os.path.join(conversation_folder, f"{user_id}.json")
          if os.path.exists(file_path):
              with open(file_path, "r") as f:
                  history = json.load(f)
              logger.info(f"Conversation history loaded from {file_path}")
              return history
          else:
            return []
     except Exception as e:
        logger.error(f"Error loading conversation history: {e}")
        return []
        
def save_embeddings(embeddings, file_path = "embeddings/embeddings.pkl"):
     """
      Saves the conversation embeddings to a pickle file.
     """
     import pickle
     try:
        if not os.path.exists(os.path.dirname(file_path)):
             os.makedirs(os.path.dirname(file_path))
        with open(file_path, 'wb') as f:
            pickle.dump(embeddings, f)
        logger.info(f"Embeddings saved to {file_path}")
        return True
     except Exception as e:
        logger.error(f"Error saving embeddings: {e}")
        return False

def load_embeddings(file_path = "embeddings/embeddings.pkl"):
    """
      Loads the conversation embeddings from a pickle file.
     """
    import pickle
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                embeddings = pickle.load(f)
            logger.info(f"Embeddings loaded from {file_path}")
            return embeddings
        else:
            return None
    except Exception as e:
        logger.error(f"Error loading embeddings: {e}")
        return None