from typing import Dict, Optional
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

class QueryAgent:
    """Agent responsible for processing natural language queries and extracting relevant parameters."""
    
    def __init__(self):
        """Initialize the QueryAgent with Mixtral-8x7B-Instruct model."""
        self.client = InferenceClient(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            token=os.getenv("HUGGINGFACE_API_KEY")
        )
        
        self.system_prompt = """
        You are a helpful assistant that extracts information from queries about OEE (Overall Equipment Efficiency) calculations.
        From the user's query, extract the following information:
        
        1. Device ID: Look for machine names or IDs (e.g., "Machine A", "Packaging Line 1")
        2. Location: Look for line numbers or locations (e.g., "Line 1", "Production Area B")
        3. Time Period: Look for months or date ranges (e.g., "January", "last week")
        
        If any information is missing, return "MISSING" for that field.
        
        Format your response as a JSON with the following structure:
        {
            "device_id": "device_id or MISSING",
            "location": "location or MISSING",
            "time_period": "month or date range or MISSING"
        }
        
        Example queries and responses:
        Query: "What was the OEE of Machine A in January?"
        Response: {"device_id": "Machine A", "location": "MISSING", "time_period": "January"}
        
        Query: "Show me the OEE for Packaging Line 1 last week"
        Response: {"device_id": "Packaging Line 1", "location": "MISSING", "time_period": "last week"}
        
        Query: "What was the OEE of Machine B in Line 2 during February?"
        Response: {"device_id": "Machine B", "location": "Line 2", "time_period": "February"}
        """
    
    def process_query(self, query: str) -> Dict[str, str]:
        """
        Process the user query and extract relevant parameters.
        
        Args:
            query (str): The user's natural language query
            
        Returns:
            Dict[str, str]: Dictionary containing extracted parameters
        """
        try:
            # Format the prompt for Mixtral
            prompt = f"<s>[INST] {self.system_prompt}\n\nUser Query: {query} [/INST]"
            
            # Get response from the model
            response = self.client.text_generation(
                prompt,
                max_new_tokens=200,
                temperature=0.1,
                do_sample=False,
                return_full_text=False
            )
            
            # Extract JSON from the response using regex
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                return result
            else:
                print(f"Could not find JSON in response: {response}")
                return {
                    "device_id": "MISSING",
                    "location": "MISSING",
                    "time_period": "MISSING"
                }
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {
                "device_id": "MISSING",
                "location": "MISSING",
                "time_period": "MISSING"
            }
        except Exception as e:
            print(f"Error processing query: {e}")
            return {
                "device_id": "MISSING",
                "location": "MISSING",
                "time_period": "MISSING"
            }
    
    def needs_clarification(self, params: Dict[str, str]) -> bool:
        """
        Check if the extracted parameters need clarification.
        
        Args:
            params (Dict[str, str]): Extracted parameters
            
        Returns:
            bool: True if clarification is needed, False otherwise
        """
        return any(value == "MISSING" for value in params.values())
    
    def get_clarification_prompt(self, params: Dict[str, str]) -> str:
        """
        Generate a clarification prompt based on missing parameters.
        
        Args:
            params (Dict[str, str]): Extracted parameters
            
        Returns:
            str: Clarification prompt
        """
        missing_fields = [k for k, v in params.items() if v == "MISSING"]
        if not missing_fields:
            return ""
        
        prompt = "I need more information to help you. Please specify:"
        for field in missing_fields:
            if field == "device_id":
                prompt += "\n- Which machine or device you're interested in (e.g., 'Machine A', 'Packaging Line 1')"
            elif field == "location":
                prompt += "\n- The location or line number (e.g., 'Line 1', 'Production Area B')"
            elif field == "time_period":
                prompt += "\n- The time period you want to analyze (e.g., 'January', 'last week', 'February 2024')"
        
        return prompt 