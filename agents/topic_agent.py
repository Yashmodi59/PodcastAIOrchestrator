import os
import json
import random
from datetime import datetime
from utils.openai_utils import get_completion

class TopicAgent:
    """Agent responsible for recommending podcast topics based on user preferences."""
    
    def __init__(self, user_preferences=None):
        """
        Initialize the TopicAgent.
        
        Args:
            user_preferences (dict): User preferences for topics, length, and style.
        """
        self.user_preferences = user_preferences or {}
    
    def generate_topic_suggestions(self, num_suggestions=3):
        """
        Generate podcast topic suggestions based on user preferences.
        
        Args:
            num_suggestions (int): Number of topic suggestions to generate.
            
        Returns:
            list: A list of dictionaries containing topic suggestions.
        """
        # Get current date/time for timely topics
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Construct the prompt for OpenAI
        preferred_topics = self.user_preferences.get("preferred_topics", [])
        preferred_style = self.user_preferences.get("preferred_style", "Conversational")
        
        topics_str = ", ".join(preferred_topics) if preferred_topics else "any interesting topics"
        
        prompt = f"""
        Generate {num_suggestions} podcast topic suggestions based on the following parameters:
        - User's preferred topics: {topics_str}
        - Preferred style: {preferred_style}
        - Current date: {current_date}
        
        For each topic suggestion, provide:
        1. A catchy title (30 characters or less)
        2. A brief description (1-2 sentences)
        
        Return the suggestions as a JSON array of objects, each with 'title' and 'description' fields.
        """
        
        try:
            response = get_completion(
                prompt=prompt,
                temperature=0.7,
                response_format="json_object"
            )
            
            # Parse the response
            suggestions = json.loads(response).get("suggestions", [])
            
            # Ensure we have the requested number of suggestions
            if len(suggestions) < num_suggestions:
                # Add some generic suggestions if we don't have enough
                generic_suggestions = [
                    {
                        "title": "The Future of AI",
                        "description": "Exploring how artificial intelligence is reshaping our world and what it means for humanity."
                    },
                    {
                        "title": "Health Myths Debunked",
                        "description": "Separating fact from fiction in common health advice and wellness trends."
                    },
                    {
                        "title": "Productivity Hacks",
                        "description": "Practical strategies to boost your efficiency and get more done in less time."
                    },
                    {
                        "title": "Climate Solutions",
                        "description": "Innovative approaches to addressing climate change and building a sustainable future."
                    }
                ]
                
                # Add generic suggestions until we have enough
                while len(suggestions) < num_suggestions:
                    suggestions.append(generic_suggestions.pop(0))
                    
            return suggestions[:num_suggestions]
            
        except Exception as e:
            print(f"Error generating topic suggestions: {e}")
            # Fallback to generic suggestions if API call fails
            return [
                {
                    "title": "The Future of AI",
                    "description": "Exploring how artificial intelligence is reshaping our world and what it means for humanity."
                },
                {
                    "title": "Health Myths Debunked",
                    "description": "Separating fact from fiction in common health advice and wellness trends."
                },
                {
                    "title": "Productivity Hacks",
                    "description": "Practical strategies to boost your efficiency and get more done in less time."
                }
            ][:num_suggestions]
