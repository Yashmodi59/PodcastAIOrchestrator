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
        # Handle compound topics with "or", "and", "vs" by searching for each part
        original_topic = topic_title
        separator_words = [" or ", " and ", " vs ", " versus "]
        separate_topics = []
        
        for separator in separator_words:
            if separator in topic_title.lower():
                separate_topics = [term.strip() for term in topic_title.lower().split(separator)]
                break
        
        # Try to find exact match first for the original topic
        page = self.wiki.page(topic_title)
        
        # If no exact match, try with capitalized first letters
        if not page.exists():
            # Try capitalizing first letter of each word
            capitalized_title = ' '.join(word.capitalize() for word in topic_title.split())
            page = self.wiki.page(capitalized_title)
            
        # If still no match, try searching for the whole phrase with common variations
        if not page.exists():
            variations = [
                topic_title.capitalize(),  # Capitalize first letter only
                topic_title.title(),       # Capitalize Each Word
                topic_title.upper(),       # ALL UPPERCASE
                topic_title.lower(),       # all lowercase
                topic_title.replace(' ', '_')  # Replace spaces with underscores
            ]
            
            for variation in variations:
                test_page = self.wiki.page(variation)
                if test_page.exists():
                    page = test_page
                    break
        
        # If we have separate topics (from "or", "and", etc.), try each one
        if not page.exists() and separate_topics:
            for part in separate_topics:
                test_page = self.wiki.page(part.capitalize())
                if test_page.exists():
                    page = test_page
                    break
                    
                # Try capitalization
                part_capitalized = ' '.join(word.capitalize() for word in part.split())
                test_page = self.wiki.page(part_capitalized)
                if test_page.exists():
                    page = test_page
                    break
        
        # For abstract concepts like "love" or "death", try more specific related articles
        if not page.exists():
            abstract_concepts = {
                "love": ["Romance (love)", "Love", "Interpersonal relationship", "Courtly love", "Emotion"],
                "death": ["Death", "Mortality", "Afterlife", "Grief", "Mourning"],
                "life": ["Life", "Human condition", "Meaning of life", "Quality of life"],
                "happiness": ["Happiness", "Well-being", "Positive psychology", "Joy"],
                "sadness": ["Sadness", "Melancholy", "Depression (mood)", "Grief"],
                "beauty": ["Beauty", "Aesthetics", "Art", "Physical attractiveness"],
                "truth": ["Truth", "Philosophy", "Epistemology", "Knowledge"],
                "freedom": ["Freedom", "Liberty", "Free will", "Political freedom"],
                "time": ["Time", "Philosophy of time", "Time perception", "Space-time"],
                "money": ["Money", "Finance", "Wealth", "Currency"]
            }
            
            # Check if any word in our topic matches these abstract concepts
            for word in original_topic.lower().split():
                if word in abstract_concepts:
                    for concept in abstract_concepts[word]:
                        test_page = self.wiki.page(concept)
                        if test_page.exists():
                            page = test_page
                            break
                    if page.exists():
                        break
        
        # If still no exact match, search for the two most important words together
        if not page.exists():
            words = [word for word in topic_title.split() if len(word) > 3]
            if len(words) >= 2:
                combined_terms = []
                # Try pairs of words
                for i in range(len(words) - 1):
                    combined_terms.append(f"{words[i]} {words[i+1]}")
                
                for term in combined_terms:
                    test_page = self.wiki.page(term)
                    if test_page.exists():
                        page = test_page
                        break
        
        # If still no match, try individual words from the topic
        if not page.exists():
            for word in original_topic.split():
                if len(word) > 3:  # Only try meaningful words
                    test_page = self.wiki.page(word.capitalize())
                    if test_page.exists():
                        page = test_page
                        break
        
        # If still no match, use a generic page related to the topic
        if not page.exists():
            # Try to match with topics of interest
            generic_topics = ["Love", "Death", "Life", "Art", "Relationships", "Philosophy", 
                             "Emotions", "Psychology", "Culture", "History", "Literature"]
            
            # First look for matches in the topic title
            for topic in generic_topics:
                if topic.lower() in topic_title.lower():
                    test_page = self.wiki.page(topic)
                    if test_page.exists():
                        page = test_page
                        break
            
            # If still no match, use any generic topic that exists
            if not page.exists():
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
            # Create a more customized fallback response based on the topic
            return {
                "title": original_topic,
                "summary": f"While specific Wikipedia information on '{original_topic}' wasn't found, this topic touches on fundamental aspects of human existence and experience that can be explored through philosophy, psychology, literature, and art.",
                "url": "",
                "sections": ["Philosophical perspectives", "Cultural significance", "Psychological aspects", "Literary and artistic representations"],
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
        # Determine if we're dealing with a compound topic (containing "or", "and", etc.)
        is_compound_topic = any(separator in topic['title'].lower() for separator in [" or ", " and ", " vs ", " versus "])
        
        # Create appropriate prompt based on topic type
        if is_compound_topic:
            prompt = f"""
            Create a structured research summary for a podcast episode comparing and contrasting the concepts in "{topic['title']}".
            
            Topic: {topic['title']}
            Topic Description: {topic['description']}
            
            Wikipedia information found: {wiki_data['title']}
            Summary: {wiki_data['summary']}
            
            Since this topic involves comparing multiple concepts, please:
            1. Provide 5-7 key points that explore both concepts, their relationships, contrasts, and intersections
            2. Include 3-5 related topics that connect to this comparative exploration
            3. Add any interesting philosophical, cultural, or psychological insights about these concepts
            
            Format the information as a JSON object with this structure:
            {{
                "key_points": ["point 1", "point 2", ...],
                "related_topics": ["topic 1", "topic 2", ...],
                "facts": ["fact 1", "fact 2", ...],
                "sources": [
                    {{"title": "Source 1", "url": "url1"}},
                    ...
                ]
            }}
            
            Include the Wikipedia information as the first source if available.
            """
        elif wiki_data["url"] == "":  # No Wikipedia page was found
            # Handle abstract concepts with a more philosophical approach
            prompt = f"""
            Create a thoughtful, philosophical structured research summary for a podcast episode on "{topic['title']}".
            
            Topic: {topic['title']}
            Topic Description: {topic['description']}
            
            This appears to be an abstract or philosophical concept without a direct Wikipedia entry.
            
            Please create content that:
            1. Provides 5-7 thoughtful key points exploring this concept from different angles (philosophical, psychological, cultural, historical)
            2. Suggests 3-5 related topics or themes that connect to this concept
            3. Includes interesting perspectives, quotes, or cultural references related to this concept
            
            Format the information as a JSON object with this structure:
            {{
                "key_points": ["point 1", "point 2", ...],
                "related_topics": ["topic 1", "topic 2", ...],
                "facts": ["insight 1", "perspective 2", ...],
                "sources": [
                    {{"title": "Philosophy of {topic['title']}", "url": ""}},
                    {{"title": "Cultural perspectives on {topic['title']}", "url": ""}}
                ]
            }}
            
            Be creative but insightful - this is for a thoughtful podcast exploring deep concepts.
            """
        else:
            # Standard approach for topics with Wikipedia information
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
                temperature=0.7,  # Slightly higher temperature for more creative responses
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            structured_data = json.loads(response)
            
            # Ensure Wikipedia is included as a source if it exists
            sources = structured_data.get("sources", [])
            if wiki_data["url"]:
                wiki_source_exists = any(source.get("url") == wiki_data["url"] for source in sources)
                
                if not wiki_source_exists:
                    sources.append({
                        "title": wiki_data["title"],
                        "url": wiki_data["url"]
                    })
                    
            structured_data["sources"] = sources
            
            return structured_data
            
        except Exception as e:
            print(f"Error structuring research: {e}")
            # Create a more relevant fallback based on the topic type
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
                            "title": wiki_data["title"],
                            "url": wiki_data["url"]
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
                            "title": wiki_data["title"],
                            "url": wiki_data["url"]
                        }
                    ]
                }
