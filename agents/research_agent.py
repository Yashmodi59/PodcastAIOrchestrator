import os
import json
import wikipediaapi
from utils.web_scraper import get_website_text_content
from utils.openai_utils import get_completion

class ResearchAgent:
    """Agent responsible for collecting research on a podcast topic."""
    
    def __init__(self):
        """Initialize the ResearchAgent."""
        user_agent = "PodcastCreator/1.0 (https://replit.com; podcast-creator@example.com)"
        self.wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language='en')
    
    def collect_research(self, topic):
        """
        Collect research information about a given topic.
        
        Args:
            topic (dict): The selected topic with 'title' and 'description'.
            
        Returns:
            dict: A dictionary containing research information.
        """
        # Step 1: Get Wikipedia information
        wiki_data = self._get_wikipedia_data(topic['title'])
        
        # Step 2: Summarize and structure the research
        structured_research = self._structure_research(topic, wiki_data)
        
        return structured_research
    
    def _get_wikipedia_data(self, topic_title):
        """
        Get Wikipedia data for a given topic.
        
        Args:
            topic_title (str): The title of the topic to research.
            
        Returns:
            dict: Wikipedia data including summary and references.
        """
        # Try to find exact match first
        page = self.wiki.page(topic_title)
        
        # If no exact match, search for related pages
        if not page.exists():
            # Try to search for related terms
            search_terms = topic_title.split()
            for term in search_terms:
                if len(term) > 3:  # Skip short words
                    test_page = self.wiki.page(term)
                    if test_page.exists():
                        page = test_page
                        break
        
        # If still no match, use a generic page
        if not page.exists():
            # Fallback to a related generic topic
            generic_topics = ["Technology", "Science", "Health", "Entertainment", "Business", "Politics"]
            for topic in generic_topics:
                test_page = self.wiki.page(topic)
                if test_page.exists():
                    page = test_page
                    break
        
        # Extract data from the Wikipedia page
        if page.exists():
            return {
                "title": page.title,
                "summary": page.summary,
                "url": f"https://en.wikipedia.org/wiki/{page.title.replace(' ', '_')}",
                "sections": [section.title for section in page.sections],
                "references": list(page.references.keys())[:5] if hasattr(page, 'references') else []
            }
        else:
            # Return empty data if no page was found
            return {
                "title": topic_title,
                "summary": "No Wikipedia information found.",
                "url": "",
                "sections": [],
                "references": []
            }
    
    def _structure_research(self, topic, wiki_data):
        """
        Structure the research data into a format useful for podcast creation.
        
        Args:
            topic (dict): The selected topic.
            wiki_data (dict): Wikipedia data about the topic.
            
        Returns:
            dict: Structured research data.
        """
        # Create prompt for OpenAI to structure the research
        prompt = f"""
        Based on the following Wikipedia information about "{topic['title']}", 
        create a structured research summary for a podcast episode.
        
        Topic: {topic['title']}
        Topic Description: {topic['description']}
        
        Wikipedia Title: {wiki_data['title']}
        Wikipedia Summary: {wiki_data['summary']}
        
        Extract and organize the following information:
        1. 5-7 key points that would be interesting to cover in a podcast
        2. 3-5 related topics that could be mentioned
        3. Any interesting facts or statistics (if available)
        
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
        
        Include the Wikipedia page as the first source.
        """
        
        try:
            response = get_completion(
                prompt=prompt,
                temperature=0.3,
                response_format="json_object"
            )
            
            # Parse the response
            structured_data = json.loads(response)
            
            # Ensure Wikipedia is included as a source
            sources = structured_data.get("sources", [])
            wiki_source_exists = any(source.get("url") == wiki_data["url"] for source in sources)
            
            if not wiki_source_exists and wiki_data["url"]:
                sources.append({
                    "title": wiki_data["title"],
                    "url": wiki_data["url"]
                })
                
            structured_data["sources"] = sources
            
            return structured_data
            
        except Exception as e:
            print(f"Error structuring research: {e}")
            # Fallback to basic structure if API call fails
            return {
                "key_points": [
                    f"Overview of {topic['title']}",
                    "Historical context and background",
                    "Current trends and developments",
                    "Future outlook and implications"
                ],
                "related_topics": ["Technology", "Science", "Society"],
                "facts": ["Various perspectives exist on this topic"],
                "sources": [
                    {
                        "title": wiki_data["title"],
                        "url": wiki_data["url"]
                    }
                ]
            }
