# ai_interface.py

import os
import json
import google.generativeai as genai

# This is the "brain" we designed in Phase 2. It's much more detailed.
PRIMORDIA_SYSTEM_PROMPT = """
You are Primordia, the AI Chronicler for a text-based evolution simulation game.
Your tone is a mix of a scientific nature documentary narrator (like David Attenborough) and a wise, ancient entity.
You have a two-step job each game turn:

1.  **FIRST MESSAGE:** You will receive a large JSON object with the complete game state. Your task is to synthesize this data into a short (2-4 sentences), evocative, and scientific narrative for the player. Describe the state of their lineage and the world. Mention any active world events or dominant threats. End your response by asking the player for their command, presenting them with their available choices. **Do not output any JSON in this step.**

2.  **SECOND MESSAGE:** You will receive a short text string which is the player's chosen command. Your task is to formalize this choice. Your FINAL output for this message MUST be a single, valid JSON object with one key: "command_to_execute". The value must be a single string matching one of the original choices (e.g., "increase_toxin_resistance"). **Do not add any other text or explanation outside of this final JSON object.**
"""

class AIInterface:
    """
    Connects to the live Google Gemini API and manages the two-step conversational flow.
    """
    def __init__(self):
        try:
            api_key = os.environ["GOOGLE_API_KEY"]
            genai.configure(api_key=api_key)
            print("[AI Interface] API key found. Connecting to Google AI.")
        except KeyError:
            raise ConnectionError("ERROR: GOOGLE_API_KEY environment variable not set. The AI is offline.")

        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=PRIMORDIA_SYSTEM_PROMPT
        )
        self.chat = None # Will hold the chat session for a turn

    def start_new_turn(self, game_state_json: str) -> str:
        """Starts a new turn by sending the game state to get the narrative."""
        self.chat = self.model.start_chat()
        response = self.chat.send_message(game_state_json)
        return response.text

    def get_player_command(self, player_input: str) -> dict:
        """Sends the player's text choice to get the final JSON command."""
        if not self.chat:
            raise RuntimeError("Must start a new turn before getting a player command.")
        
        try:
            response = self.chat.send_message(player_input)
            cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_text)
        except Exception as e:
            print(f"AI command parsing error: {e}. Defaulting to 'wait'.")
            return {"command_to_execute": "wait"}