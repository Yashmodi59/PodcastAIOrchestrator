import os
import json
from openai import OpenAI

# Load API key from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def get_completion(
    prompt, 
    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
    temperature=0.7,
    max_tokens=None,
    response_format=None
):
    """
    Get a completion from OpenAI API.
    
    Args:
        prompt (str): The prompt to send to the model.
        model (str): The model to use for completion.
        temperature (float): The temperature for generation.
        max_tokens (int, optional): Maximum number of tokens to generate.
        response_format (dict, optional): Format specification for the response.
        
    Returns:
        str: The completion text.
    """
    messages = [{"role": "user", "content": prompt}]
    
    # Prepare the API call parameters
    params = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    
    # Add optional parameters if provided
    if max_tokens is not None:
        params["max_tokens"] = max_tokens
        
    if response_format is not None:
        if response_format == "json_object":
            params["response_format"] = {"type": "json_object"}
        else:
            params["response_format"] = response_format
    
    try:
        # Make the API call
        response = client.chat.completions.create(**params)
        
        # Return the completion text
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        # Re-raise the exception to be handled by the caller
        raise

def analyze_with_system_prompt(
    prompt,
    system_prompt,
    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
    temperature=0.7,
    max_tokens=None,
    response_format=None
):
    """
    Get a completion from OpenAI API with a system prompt.
    
    Args:
        prompt (str): The user prompt to send to the model.
        system_prompt (str): The system prompt to guide the model.
        model (str): The model to use for completion.
        temperature (float): The temperature for generation.
        max_tokens (int, optional): Maximum number of tokens to generate.
        response_format (dict, optional): Format specification for the response.
        
    Returns:
        str: The completion text.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    # Prepare the API call parameters
    params = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    
    # Add optional parameters if provided
    if max_tokens is not None:
        params["max_tokens"] = max_tokens
        
    if response_format is not None:
        if response_format == "json_object":
            params["response_format"] = {"type": "json_object"}
        else:
            params["response_format"] = response_format
    
    try:
        # Make the API call
        response = client.chat.completions.create(**params)
        
        # Return the completion text
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        # Re-raise the exception to be handled by the caller
        raise
