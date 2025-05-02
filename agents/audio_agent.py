import os
import json
import tempfile
import time
from gtts import gTTS

class AudioAgent:
    """Agent responsible for converting podcast scripts to audio."""
    
    def __init__(self):
        """Initialize the AudioAgent."""
        # Create a directory for audio files if it doesn't exist
        os.makedirs("audio", exist_ok=True)
    
    def generate_audio(self, script, podcast_id, voice="en-US"):
        """
        Generate audio from a podcast script using gTTS.
        
        Args:
            script (str): The podcast script to convert to audio.
            podcast_id (str): Unique identifier for the podcast.
            voice (str): Voice identifier for TTS.
            
        Returns:
            str: Path to the generated audio file.
        """
        try:
            # Prepare the script for TTS
            # We need to clean it up to make it suitable for speech
            processed_script = self._prepare_script_for_tts(script)
            
            # Generate the audio file
            audio_file_path = f"audio/podcast_{podcast_id}.mp3"
            
            # Generate audio using gTTS
            tts = gTTS(text=processed_script, lang='en', slow=False)
            tts.save(audio_file_path)
            
            return audio_file_path
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            # Return a path to a non-existent file to indicate failure
            return None
    
    def _prepare_script_for_tts(self, script):
        """
        Prepare a podcast script for text-to-speech conversion.
        
        Args:
            script (str): Original podcast script.
            
        Returns:
            str: Processed script suitable for TTS.
        """
        # Remove speaker indicators (e.g., "HOST:") and formatting
        lines = script.split('\n')
        processed_lines = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
                
            # Remove speaker indicators
            if ":" in line and line.split(":")[0].strip().upper() == line.split(":")[0].strip():
                # This looks like a speaker indicator line
                processed_line = ". ".join(part.strip() for part in line.split(":")[1:])
                processed_lines.append(processed_line)
            else:
                # Regular line
                processed_lines.append(line)
        
        # Join the processed lines
        processed_script = " ".join(processed_lines)
        
        # Replace multiple spaces with a single space
        processed_script = " ".join(processed_script.split())
        
        # Add pauses for better speech flow (periods, commas, etc.)
        processed_script = processed_script.replace(". ", ". <break time='0.5s'> ")
        processed_script = processed_script.replace("! ", "! <break time='0.5s'> ")
        processed_script = processed_script.replace("? ", "? <break time='0.5s'> ")
        processed_script = processed_script.replace(", ", ", <break time='0.3s'> ")
        
        return processed_script

    def combine_audio_segments(self, segments, podcast_id):
        """
        Combine multiple audio segments into a single podcast.
        
        Args:
            segments (list): List of audio file paths to combine.
            podcast_id (str): Unique identifier for the podcast.
            
        Returns:
            str: Path to the combined audio file.
        """
        # This is a placeholder for more advanced audio processing
        # In a real implementation, you might use a library like pydub
        print("Audio segment combination not implemented")
        # Return the first segment as a fallback
        return segments[0] if segments else None
