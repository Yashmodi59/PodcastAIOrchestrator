import os
import json
from utils.openai_utils import get_completion

class ScriptAgent:
    """Agent responsible for creating a podcast script based on research."""
    
    def __init__(self, user_preferences=None):
        """
        Initialize the ScriptAgent.
        
        Args:
            user_preferences (dict): User preferences for podcast style and length.
        """
        self.user_preferences = user_preferences or {}
    
    def create_script(self, topic, research, preferred_length_minutes=15):
        """
        Create a podcast script based on research.
        
        Args:
            topic (dict): The selected topic with 'title' and 'description'.
            research (dict): Research data including key points and sources.
            preferred_length_minutes (int): Preferred podcast length in minutes.
            
        Returns:
            str: The formatted podcast script.
        """
        # Get preferred style from user preferences
        preferred_style = self.user_preferences.get("preferred_style", "Conversational")
        
        # Calculate approximate word count based on preferred length
        # Average speaking rate is about 150 words per minute
        word_count = preferred_length_minutes * 150
        
        # Construct the prompt for OpenAI
        prompt = f"""
        Create a complete podcast script about "{topic['title']}" based on the provided research information.
        
        Script details:
        - Style: {preferred_style}
        - Target length: {preferred_length_minutes} minutes (approximately {word_count} words)
        - Format: Include intro, body, and conclusion
        
        Research information:
        - Topic: {topic['title']}
        - Description: {topic['description']}
        - Key points to cover:
          {self._format_list_for_prompt(research['key_points'])}
        - Related topics:
          {self._format_list_for_prompt(research['related_topics'])}
        - Interesting facts (if available):
          {self._format_list_for_prompt(research.get('facts', ['No specific facts provided']))}
        
        Script requirements:
        1. Begin with a welcoming introduction that hooks the listener
        2. Include transitions between topics
        3. Reference at least 2 sources from the research
        4. End with a conclusion and call-to-action for listeners
        5. Use a {preferred_style.lower()} tone throughout
        6. Format the script clearly with speaker indicators (HOST:) and segment breaks
        
        Avoid using placeholder text or generic statements - be specific to the topic.
        """
        
        try:
            response = get_completion(
                prompt=prompt,
                temperature=0.5,
                max_tokens=2500  # Adjust based on expected length
            )
            
            return response
            
        except Exception as e:
            print(f"Error creating script: {e}")
            # Create a basic fallback script
            return self._create_fallback_script(topic, research)
    
    def _format_list_for_prompt(self, items):
        """Format a list as a string for inclusion in a prompt."""
        return "\n".join([f"    - {item}" for item in items]) if items else "    - No items provided"
    
    def _create_fallback_script(self, topic, research):
        """Create a basic fallback script if the API call fails."""
        key_points = "\n".join([f"- {point}" for point in research['key_points']])
        sources = "\n".join([f"- {source['title']}" for source in research.get('sources', [])])
        
        return f"""
        HOST: Welcome to our podcast! Today we're discussing {topic['title']}.
        
        HOST: {topic['description']}
        
        === MAIN CONTENT ===
        
        HOST: Let's explore some key aspects of this topic:
        
        {key_points}
        
        HOST: I've found some interesting information from these sources:
        
        {sources}
        
        === CONCLUSION ===
        
        HOST: That wraps up our discussion on {topic['title']}. 
        Thanks for listening, and please join us again for another fascinating topic!
        """
