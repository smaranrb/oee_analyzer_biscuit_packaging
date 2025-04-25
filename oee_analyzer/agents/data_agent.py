import pandas as pd
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import os
from dateutil import parser

class DataAgent:
    """Agent responsible for loading and filtering data from Excel files."""
    
    def __init__(self, data_path: str = "data/packaging_data.xlsx"):
        """
        Initialize the DataAgent with the path to the Excel file.
        
        Args:
            data_path (str): Path to the Excel file containing packaging data
        """
        self.data_path = data_path
        self.data = None
        self.valid_combinations = None
    
    def load_data(self) -> None:
        """Load data from the Excel file."""
        try:
            # Read Excel file with openpyxl engine
            self.data = pd.read_excel(self.data_path, engine='openpyxl')
            
            # Convert timestamp to datetime
            self.data['Timestamp'] = pd.to_datetime(self.data['Timestamp'])
            
            # Pre-compute valid device-location combinations
            self.valid_combinations = self.data.groupby(['Device_ID', 'Location']).size().reset_index()
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def validate_parameters(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """
        Validate if the provided parameters are valid combinations.
        
        Args:
            params (Dict[str, str]): Dictionary containing filter parameters
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if self.data is None:
            self.load_data()
        
        # Map input parameters to actual values
        device_map = {
            "machine a": "DEV_A1",
            "machine b": "DEV_B2",
            "machine c": "DEV_C3",
            "dev_a1": "DEV_A1",
            "dev_b2": "DEV_B2",
            "dev_c3": "DEV_C3"
        }
        
        location_map = {
            "plant 1": "Plant_1",
            "plant 2": "Plant_2",
            "plant 3": "Plant_3",
            "line 1": "Plant_1",
            "line 2": "Plant_2",
            "line 3": "Plant_3"
        }
        
        device_id = params['device_id'].lower()
        if device_id in device_map:
            device_id = device_map[device_id]
        
        location = params['location'].lower()
        if location in location_map:
            location = location_map[location]
        
        # Check if device exists
        if device_id not in self.data['Device_ID'].unique():
            return False, f"Device {device_id} does not exist in the dataset."
        
        # Check if location exists
        if location not in self.data['Location'].unique():
            return False, f"Location {location} does not exist in the dataset."
        
        # Check if device-location combination exists
        if not self.valid_combinations[
            (self.valid_combinations['Device_ID'] == device_id) & 
            (self.valid_combinations['Location'] == location)
        ].empty:
            return True, ""
        
        return False, f"Device {device_id} is not present in {location}."
    
    def filter_data(self, params: Dict[str, str]) -> pd.DataFrame:
        """
        Filter data based on the provided parameters.
        
        Args:
            params (Dict[str, str]): Dictionary containing filter parameters
            
        Returns:
            pd.DataFrame: Filtered data
        """
        if self.data is None:
            self.load_data()
        
        # Validate parameters first
        is_valid, error_msg = self.validate_parameters(params)
        if not is_valid:
            raise ValueError(error_msg)
        
        filtered_data = self.data.copy()
        
        # Apply filters
        if params['device_id'] != "MISSING":
            device_map = {
                "machine a": "DEV_A1",
                "machine b": "DEV_B2",
                "machine c": "DEV_C3",
                "dev_a1": "DEV_A1",
                "dev_b2": "DEV_B2",
                "dev_c3": "DEV_C3"
            }
            device_id = params['device_id'].lower()
            if device_id in device_map:
                device_id = device_map[device_id]
            filtered_data = filtered_data[filtered_data['Device_ID'] == device_id]
        
        if params['location'] != "MISSING":
            location_map = {
                "plant 1": "Plant_1",
                "plant 2": "Plant_2",
                "plant 3": "Plant_3",
                "line 1": "Plant_1",
                "line 2": "Plant_2",
                "line 3": "Plant_3"
            }
            location = params['location'].lower()
            if location in location_map:
                location = location_map[location]
            filtered_data = filtered_data[filtered_data['Location'] == location]
        
        if params['time_period'] != "MISSING":
            if " to " in params['time_period']:
                start_date, end_date = params['time_period'].split(" to ")
                start_date = pd.to_datetime(start_date)
                end_date = pd.to_datetime(end_date)
                filtered_data = filtered_data[
                    (filtered_data['Timestamp'] >= start_date) & 
                    (filtered_data['Timestamp'] <= end_date)
                ]
            else:
                try:
                    month_date = parser.parse(params['time_period'])
                    filtered_data = filtered_data[
                        (filtered_data['Timestamp'].dt.month == month_date.month) & 
                        (filtered_data['Timestamp'].dt.year == month_date.year)
                    ]
                except:
                    month_map = {
                        'january': 1, 'february': 2, 'march': 3, 'april': 4,
                        'may': 5, 'june': 6, 'july': 7, 'august': 8,
                        'september': 9, 'october': 10, 'november': 11, 'december': 12
                    }
                    month_name = params['time_period'].lower()
                    if month_name in month_map:
                        month_num = month_map[month_name]
                        filtered_data = filtered_data[
                            filtered_data['Timestamp'].dt.month == month_num
                        ]
        
        if filtered_data.empty:
            raise ValueError("No data found for the specified time period.")
        
        return filtered_data
    
    def get_available_devices(self) -> list:
        """
        Get list of available device IDs.
        
        Returns:
            list: List of unique device IDs
        """
        if self.data is None:
            self.load_data()
        return self.data['Device_ID'].unique().tolist()
    
    def get_available_locations(self) -> list:
        """
        Get list of available locations.
        
        Returns:
            list: List of unique locations
        """
        if self.data is None:
            self.load_data()
        return self.data['Location'].unique().tolist()
    
    def get_device_locations(self, device_id: str) -> list:
        """
        Get list of locations where a device is present.
        
        Args:
            device_id (str): Device ID to check
            
        Returns:
            list: List of locations where the device is present
        """
        if self.data is None:
            self.load_data()
        return self.data[self.data['Device_ID'] == device_id]['Location'].unique().tolist() 