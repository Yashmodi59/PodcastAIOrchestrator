import os
import json
from utils.openai_utils import get_completion

class PromotionAgent:
    """Agent responsible for generating promotion content for podcasts."""
    
    def __init__(self):
        """Initialize the PromotionAgent."""
        pass
    
    def generate_promotion(self, topic, script, length_minutes):
        """
        Generate promotional content for a podcast.
        
        Args:
            topic (dict): The podcast topic information.
            script (str): The podcast script.
            length_minutes (int): Length of the podcast in minutes.
            
        Returns:
            dict: Promotional content including title, post, summary, and hashtags.
        """
        # Extract key information from the script
        # For a real implementation, we might use a more sophisticated approach
        script_excerpt = script[:1000] if len(script) > 1000 else script
        
        # Construct the prompt for OpenAI
        prompt = f"""
        Create promotional content for a podcast about "{topic['title']}" with the following description:
        "{topic['description']}"
        
        The podcast is approximately {length_minutes} minutes long.
        
        Here's an excerpt from the podcast script to help you understand the content:
        ```
        {script_excerpt}
        ```
        
        Generate the following promotional elements:
        1. Catchy title (max 50 characters)
        2. Social media post (max 280 characters, suitable for Twitter)
        3. Brief summary (2-3 sentences for newsletter/email)
        4. 5 relevant hashtags
        
        Return the content as a JSON object with the following structure:
        {{
            "title": "catchy title",
            "post": "social media post",
            "summary": "brief summary",
            "hashtags": ["hashtag1", "hashtag2", ...]
        }}
        """
        
        try:
            response = get_completion(
                prompt=prompt,
                temperature=0.7,
                response_format="json_object"
            )
            
            # Parse the response
            promotion = json.loads(response)
            
            # Ensure all required fields are present
            if not all(key in promotion for key in ["title", "post", "summary", "hashtags"]):
                missing_keys = [key for key in ["title", "post", "summary", "hashtags"] if key not in promotion]
                print(f"Missing keys in promotion response: {missing_keys}")
                # Add missing keys with default values
                for key in missing_keys:
                    if key == "title":
                        promotion["title"] = f"New Podcast: {topic['title']}"
                    elif key == "post":
                        promotion["post"] = f"Check out our new podcast about {topic['title']}! {topic['description']}"
                    elif key == "summary":
                        promotion["summary"] = f"In this episode, we explore {topic['title']}. {topic['description']}"
                    elif key == "hashtags":
                        promotion["hashtags"] = ["podcast", "newepisode", topic['title'].replace(" ", "")]
            
            # Format hashtags properly
            promotion["hashtags"] = [tag if tag.startswith("#") else f"#{tag}" for tag in promotion["hashtags"]]
            
            return promotion
            
        except Exception as e:
            print(f"Error generating promotion: {e}")
            # Return default promotion if API call fails
            return {
                "title": f"New Podcast: {topic['title']}",
                "post": f"Check out our new podcast about {topic['title']}! {topic['description']}",
                "summary": f"In this episode, we explore {topic['title']}. {topic['description']}",
                "hashtags": ["#podcast", "#newepisode", f"#{topic['title'].replace(' ', '')}"]
            }
    
    def generate_show_notes(self, topic, research, script):
        """
        Generate detailed show notes for a podcast.
        
        Args:
            topic (dict): The podcast topic information.
            research (dict): Research data used for the podcast.
            script (str): The podcast script.
            
        Returns:
            str: Formatted show notes.
        """
        # Construct the prompt for OpenAI
        prompt = f"""
        Create detailed show notes for a podcast about "{topic['title']}".
        
        Topic description: {topic['description']}
        
        Include the following elements:
        1. Episode overview
        2. Key topics discussed (extract from the script)
        3. Resources mentioned (from the research sources)
        4. Timestamps for major topics (estimate based on the script structure)
        
        Format the show notes in markdown.
        """
        
        try:
            response = get_completion(
                prompt=prompt,
                temperature=0.4
            )
            
            return response
            
        except Exception as e:
            print(f"Error generating show notes: {e}")
            # Return basic show notes if API call fails
            sources = "\n".join([f"- {source['title']}" for source in research.get('sources', [])])
            
            return f"""
            # Show Notes: {topic['title']}
            
            ## Episode Overview
            {topic['description']}
            
            ## Key Topics Discussed
            {', '.join(research['key_points'][:3])}
            
            ## Resources Mentioned
            {sources}
            
            ## Timestamps
            0:00 - Introduction
            1:00 - Main Discussion
            10:00 - Conclusion
            """
