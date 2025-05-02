import os
import time
import uuid
from datetime import datetime
from agents.topic_agent import TopicAgent
from agents.research_agent import ResearchAgent
from agents.script_agent import ScriptAgent
from agents.content_checker_agent import ContentCheckerAgent
from agents.audio_agent import AudioAgent
from agents.promotion_agent import PromotionAgent
from agents.email_agent import EmailAgent
from utils.storage import save_podcast, load_podcast

class PodcastWorkflow:
    """Class that orchestrates the multi-agent podcast creation workflow."""
    
    def __init__(self, user_id, preferences=None):
        """
        Initialize the PodcastWorkflow.
        
        Args:
            user_id (str): Unique identifier for the user.
            preferences (dict, optional): User preferences.
        """
        self.user_id = user_id
        self.preferences = preferences or {}
        self.podcast_id = str(uuid.uuid4())
        
        # Initialize agents
        self.topic_agent = TopicAgent(user_preferences=self.preferences)
        self.research_agent = ResearchAgent()
        self.script_agent = ScriptAgent(user_preferences=self.preferences)
        self.content_checker_agent = ContentCheckerAgent()
        self.audio_agent = AudioAgent()
        self.promotion_agent = PromotionAgent()
        self.email_agent = EmailAgent()
        
        # Workflow state
        self.topic = None
        self.research = None
        self.script = None
        self.content_check = None
        self.refined_script = None
        self.audio_path = None
        self.promotion = None
        
        # Performance tracking
        self.performance_metrics = {
            "topic_generation_time": 0,
            "research_time": 0,
            "script_creation_time": 0,
            "content_check_time": 0,
            "audio_generation_time": 0,
            "promotion_generation_time": 0,
            "email_sending_time": 0
        }
    
    def get_topic_suggestions(self, num_suggestions=3):
        """
        Get topic suggestions from the TopicAgent.
        
        Args:
            num_suggestions (int): Number of suggestions to generate.
            
        Returns:
            list: Topic suggestions.
        """
        start_time = time.time()
        
        suggestions = self.topic_agent.generate_topic_suggestions(num_suggestions)
        
        self.performance_metrics["topic_generation_time"] = time.time() - start_time
        
        return suggestions
    
    def select_topic(self, topic):
        """
        Select a topic for the podcast.
        
        Args:
            topic (dict): The selected topic.
        """
        self.topic = topic
    
    def conduct_research(self):
        """Conduct research on the selected topic."""
        if not self.topic:
            raise ValueError("No topic selected")
        
        start_time = time.time()
        
        self.research = self.research_agent.collect_research(self.topic)
        
        self.performance_metrics["research_time"] = time.time() - start_time
    
    def create_script(self):
        """Create a podcast script based on the research."""
        if not self.topic or not self.research:
            raise ValueError("Topic and research are required")
        
        start_time = time.time()
        
        # Get preferred length from user preferences, default to 15 minutes
        preferred_length = self.preferences.get("preferred_length", 15)
        
        self.script = self.script_agent.create_script(
            self.topic, 
            self.research,
            preferred_length_minutes=preferred_length
        )
        
        self.performance_metrics["script_creation_time"] = time.time() - start_time
    
    def check_content(self):
        """Check and refine the podcast script."""
        if not self.script:
            raise ValueError("Script is required")
        
        start_time = time.time()
        
        self.content_check, self.refined_script = self.content_checker_agent.check_content(
            self.script, 
            self.topic
        )
        
        self.performance_metrics["content_check_time"] = time.time() - start_time
    
    def generate_audio(self, voice="en-US"):
        """
        Generate audio from the refined script.
        
        Args:
            voice (str): Voice identifier for TTS.
        """
        if not self.refined_script:
            raise ValueError("Refined script is required")
        
        start_time = time.time()
        
        self.audio_path = self.audio_agent.generate_audio(
            self.refined_script,
            self.podcast_id,
            voice
        )
        
        self.performance_metrics["audio_generation_time"] = time.time() - start_time
    
    def generate_promotion(self):
        """Generate promotional content for the podcast."""
        if not self.topic or not self.refined_script:
            raise ValueError("Topic and refined script are required")
        
        start_time = time.time()
        
        # Get preferred length from user preferences, default to 15 minutes
        preferred_length = self.preferences.get("preferred_length", 15)
        
        self.promotion = self.promotion_agent.generate_promotion(
            self.topic,
            self.refined_script,
            preferred_length
        )
        
        self.performance_metrics["promotion_generation_time"] = time.time() - start_time
    
    def send_emails(self, subscribers):
        """
        Send podcast notification emails to subscribers.
        
        Args:
            subscribers (list): List of subscriber email addresses.
            
        Returns:
            bool: True if emails were sent successfully, False otherwise.
        """
        if not self.promotion or not self.audio_path:
            raise ValueError("Promotion and audio are required")
        
        start_time = time.time()
        
        podcast_info = {
            "title": self.promotion["title"],
            "summary": self.promotion["summary"],
            "hashtags": self.promotion["hashtags"]
        }
        
        result = self.email_agent.send_notification(
            subscribers,
            podcast_info,
            self.audio_path
        )
        
        self.performance_metrics["email_sending_time"] = time.time() - start_time
        
        return result
    
    def save_podcast(self):
        """
        Save the podcast to storage.
        
        Returns:
            bool: True if saved successfully, False otherwise.
        """
        podcast_data = {
            "id": self.podcast_id,
            "user_id": self.user_id,
            "title": self.promotion["title"] if self.promotion else f"Podcast on {self.topic['title']}",
            "topic": self.topic["title"],
            "description": self.topic["description"],
            "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "script": self.refined_script if self.refined_script else self.script,
            "audio_path": self.audio_path,
            "promotion": self.promotion,
            "performance_metrics": self.performance_metrics
        }
        
        return save_podcast(self.user_id, podcast_data)
    
    def get_performance_report(self):
        """
        Get a performance report for the workflow.
        
        Returns:
            dict: Performance metrics and stats.
        """
        total_time = sum(self.performance_metrics.values())
        
        performance_report = {
            "total_processing_time": total_time,
            "metrics": self.performance_metrics,
            "percentages": {
                step: (time / total_time) * 100 if total_time > 0 else 0
                for step, time in self.performance_metrics.items()
            }
        }
        
        return performance_report
