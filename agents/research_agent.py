import os
import json
from utils.web_scraper import get_website_text_content
from utils.openai_utils import get_completion, analyze_with_system_prompt

class ResearchAgent:
    """Agent responsible for collecting research on a podcast topic."""
    
    def __init__(self):
        """Initialize the ResearchAgent."""
        pass
    
    def collect_research(self, topic):
        """
        Collect research information about a given topic.
        
        Args:
            topic (dict): The selected topic with 'title' and 'description'.
            
        Returns:
            dict: A dictionary containing research information.
        """
        # Step 1: Get research information using OpenAI
        research_data = self._get_ai_research_data(topic)
        
        # Step 2: Structure the research
        structured_research = self._structure_research(topic, research_data)
        
        return structured_research
    
    def _get_ai_research_data(self, topic):
        """
        Use OpenAI to generate research data about a topic.
        
        Args:
            topic (dict): The topic information with 'title' and 'description'.
            
        Returns:
            dict: Research data including summary and context.
        """
        # Determine if we're dealing with a compound topic (containing "or", "and", etc.)
        is_compound_topic = any(separator in topic['title'].lower() 
                               for separator in [" or ", " and ", " vs ", " versus "])
        
        # Create appropriate system prompt based on topic type
        if is_compound_topic:
            system_prompt = """You are a knowledgeable research assistant with expertise across many domains.
            Your task is to provide comprehensive research on comparative topics.
            For topics that compare or contrast concepts (like "love or death", "science vs religion"),
            provide balanced information about both elements and their relationships.
            Include philosophical, cultural, historical, and psychological perspectives.
            Focus on factual information and diverse viewpoints rather than personal opinions.
            Structure your response as a research summary with key concepts, perspectives, and implications."""
        else:
            # Check if topic is an abstract concept
            abstract_concepts = ["love", "death", "life", "happiness", "sadness", "beauty", 
                               "truth", "freedom", "time", "money", "meaning", "existence",
                               "consciousness", "morality", "ethics", "faith", "hope"]
            
            words_in_topic = topic['title'].lower().split()
            is_abstract = any(word in abstract_concepts for word in words_in_topic)
            
            if is_abstract:
                system_prompt = """You are a philosophical research assistant with deep knowledge of abstract concepts.
                Your task is to provide thoughtful, multifaceted research on philosophical and abstract topics.
                Include perspectives from various philosophical traditions, cultural contexts, and time periods.
                Consider psychological, sociological, artistic, and literary interpretations.
                Maintain academic integrity while making complex ideas accessible.
                Structure your response as a research summary with key philosophical viewpoints, cultural significances, and contemporary relevance."""
            else:
                system_prompt = """You are a knowledgeable research assistant with expertise across many domains.
                Your task is to provide comprehensive, factual research on specific topics.
                Include historical context, current understanding, various perspectives, and practical implications.
                Focus on accuracy, relevance, and depth without speculation.
                Structure your response as a research summary with background information, key points, and current significance."""
        
        # Create the user prompt with the topic information
        user_prompt = f"""Please provide comprehensive research on the topic: "{topic['title']}"
        
        Topic description: {topic.get('description', 'No additional description provided.')}
        
        Include the following in your research:
        1. A concise but informative summary of the topic
        2. Key historical or contextual information
        3. Major perspectives or approaches to understanding this topic
        4. Significant developments or current thinking
        5. Implications or applications
        
        Structure your response as factual research that could be used for a podcast episode on this topic."""
        
        # Get research from OpenAI
        try:
            research_response = analyze_with_system_prompt(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.5
            )
            
            # Extract relevant sources and references if possible
            sources_prompt = f"""Based on the research you just provided about "{topic['title']}", 
            please list 3-5 credible sources or references that would be valuable for further research on this topic.
            For each source, provide a title and URL if possible. Focus on academic, educational, or reputable sources."""
            
            sources_response = get_completion(sources_prompt, temperature=0.3)
            
            return {
                "title": topic['title'],
                "summary": research_response,
                "sources_text": sources_response,
                "url": "",  # No specific URL since this is AI-generated research
                "is_ai_generated": True
            }
            
        except Exception as e:
            print(f"Error generating research using AI: {e}")
            # Provide a fallback response
            return {
                "title": topic['title'],
                "summary": f"Research on '{topic['title']}' explores this topic from multiple perspectives, considering its meaning, significance, and implications across different contexts and disciplines.",
                "sources_text": "Various philosophical, psychological, and cultural sources could provide further insights into this topic.",
                "url": "",
                "is_ai_generated": True
            }
    
    def _structure_research(self, topic, research_data):
        """
        Structure the research data into a format useful for podcast creation.
        
        Args:
            topic (dict): The selected topic.
            research_data (dict): Research data about the topic.
            
        Returns:
            dict: Structured research data.
        """
        # Determine if we're dealing with a compound topic (containing "or", "and", etc.)
        is_compound_topic = any(separator in topic['title'].lower() for separator in [" or ", " and ", " vs ", " versus "])
        
        prompt = f"""
        Based on the following research about "{topic['title']}", 
        organize the information into a structured format for a podcast episode.
        
        Topic: {topic['title']}
        Topic Description: {topic.get('description', 'No additional description provided.')}
        
        Research Summary:
        {research_data['summary']}
        
        Potential sources:
        {research_data['sources_text']}
        
        Extract and organize the following information:
        1. 5-7 key points that would be interesting to cover in a podcast
        2. 3-5 related topics that could be mentioned
        3. Any interesting facts, perspectives or insights worth highlighting
        
        Return the information as a JSON object with the following structure:
        {{
            "key_points": ["point 1", "point 2", ...],
            "related_topics": ["topic 1", "topic 2", ...],
            "facts": ["fact 1", "fact 2", ...],
            "sources": [
                {{"title": "Source 1", "url": "url1"}},
                ...
            ]
        }}
        
        For sources, extract any specific sources mentioned in the research or sources text.
        If no specific sources are provided, suggest 2-3 generalized source types relevant to this topic.
        """
        
        try:
            response = get_completion(
                prompt=prompt,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            structured_data = json.loads(response)
            
            # Ensure we have all required fields
            if "key_points" not in structured_data:
                structured_data["key_points"] = []
            if "related_topics" not in structured_data:
                structured_data["related_topics"] = []
            if "facts" not in structured_data:
                structured_data["facts"] = []
            if "sources" not in structured_data:
                structured_data["sources"] = []
                
            return structured_data
            
        except Exception as e:
            print(f"Error structuring research: {e}")
            # Create a relevant fallback based on the topic type
            if is_compound_topic:
                # For compound topics like "love or death"
                parts = topic['title'].split(" or " if " or " in topic['title'] else " and " if " and " in topic['title'] else " vs ")
                return {
                    "key_points": [
                        f"The concept of {parts[0]} in human experience",
                        f"The concept of {parts[1]} in human experience",
                        f"How {parts[0]} and {parts[1]} relate and contrast with each other",
                        "Philosophical perspectives on these concepts",
                        "Cultural representations in literature and art",
                        "Psychological understanding of these experiences"
                    ],
                    "related_topics": ["Philosophy", "Psychology", "Literature", "Art", "Human experience"],
                    "facts": [
                        f"Both {parts[0]} and {parts[1]} are fundamental aspects of human experience",
                        "These concepts have been explored in philosophy since ancient times",
                        "Different cultures have varying perspectives on these concepts"
                    ],
                    "sources": [
                        {
                            "title": f"Philosophical perspectives on {topic['title']}",
                            "url": ""
                        },
                        {
                            "title": f"Cultural analysis of {topic['title']}",
                            "url": ""
                        }
                    ]
                }
            else:
                # General fallback with more relevant topics than technology
                return {
                    "key_points": [
                        f"The concept of {topic['title']} in human experience",
                        "Historical and cultural contexts",
                        "Philosophical perspectives",
                        "Modern understandings and interpretations",
                        "Personal and societal implications"
                    ],
                    "related_topics": ["Philosophy", "Psychology", "Culture", "Literature", "Human experience"],
                    "facts": [
                        f"{topic['title']} has been explored in various ways throughout human history",
                        "Different philosophical traditions offer unique perspectives on this topic",
                        "The concept continues to evolve in contemporary thought"
                    ],
                    "sources": [
                        {
                            "title": f"Academic research on {topic['title']}",
                            "url": ""
                        },
                        {
                            "title": f"Cultural perspectives on {topic['title']}",
                            "url": ""
                        }
                    ]
                }
