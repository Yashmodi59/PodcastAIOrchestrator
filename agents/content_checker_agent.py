import os
import json
from utils.openai_utils import get_completion

class ContentCheckerAgent:
    """Agent responsible for checking and refining podcast script content."""
    
    def __init__(self):
        """Initialize the ContentCheckerAgent."""
        pass
    
    def check_content(self, script, topic):
        """
        Check and refine a podcast script for grammar, clarity, and content issues.
        
        Args:
            script (str): The podcast script to check.
            topic (dict): The podcast topic information.
            
        Returns:
            tuple: A tuple containing (content_check_results, refined_script)
        """
        # Construct the prompt for OpenAI
        prompt = f"""
        Analyze the following podcast script about "{topic['title']}" for grammar, clarity, and content issues.
        Then provide a refined version of the script addressing these issues.
        
        SCRIPT TO ANALYZE:
        ```
        {script}
        ```
        
        Provide your analysis and refinements in the following JSON format:
        {{
            "grammar_issues": ["issue 1", "issue 2", ...],
            "clarity_issues": ["issue 1", "issue 2", ...],
            "content_issues": ["issue 1", "issue 2", ...],
            "refined_script": "the refined script"
        }}
        
        Be thorough but concise in your analysis. For each category, provide up to 5 specific issues.
        If there are no issues in a category, return an empty array.
        """
        
        try:
            response = get_completion(
                prompt=prompt,
                temperature=0.3,
                response_format="json_object"
            )
            
            # Parse the response
            check_results = json.loads(response)
            
            # Extract the content check results and refined script
            content_check = {
                "grammar_issues": check_results.get("grammar_issues", []),
                "clarity_issues": check_results.get("clarity_issues", []),
                "content_issues": check_results.get("content_issues", [])
            }
            
            refined_script = check_results.get("refined_script", script)
            
            return content_check, refined_script
            
        except Exception as e:
            print(f"Error checking content: {e}")
            # Return minimal results if API call fails
            return {
                "grammar_issues": [],
                "clarity_issues": [],
                "content_issues": ["Could not perform detailed content check"]
            }, script
    
    def suggest_improvements(self, script, topic):
        """
        Suggest improvements for a podcast script beyond basic content checking.
        
        Args:
            script (str): The podcast script to improve.
            topic (dict): The podcast topic information.
            
        Returns:
            dict: Suggested improvements.
        """
        prompt = f"""
        Review the following podcast script about "{topic['title']}" and suggest specific improvements
        to make it more engaging, informative, and professional.
        
        SCRIPT:
        ```
        {script}
        ```
        
        Provide suggestions in the following categories:
        1. Engagement: How to make the content more captivating
        2. Structure: How to improve the flow and organization
        3. Content depth: Areas that could use more explanation or examples
        4. Tone: Adjustments to the speaking tone or style
        
        Return your suggestions as a JSON object with these categories as keys.
        """
        
        try:
            response = get_completion(
                prompt=prompt,
                temperature=0.4,
                response_format="json_object"
            )
            
            # Parse the response
            improvements = json.loads(response)
            return improvements
            
        except Exception as e:
            print(f"Error generating improvement suggestions: {e}")
            # Return basic suggestions if API call fails
            return {
                "engagement": ["Consider adding more questions to engage the audience"],
                "structure": ["Ensure smooth transitions between topics"],
                "content_depth": ["Add specific examples where possible"],
                "tone": ["Maintain consistent tone throughout"]
            }
