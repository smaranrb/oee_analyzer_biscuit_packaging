import pandas as pd
from typing import Dict, Tuple
from datetime import datetime, timedelta

class OEEAgent:
    """Agent responsible for calculating OEE metrics."""
    
    def calculate_oee(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate OEE metrics from the filtered data.
        
        Args:
            data (pd.DataFrame): Filtered data containing production information
            
        Returns:
            Dict[str, float]: Dictionary containing OEE metrics
        """
        if data.empty:
            return {
                "availability": 0.0,
                "performance": 0.0,
                "quality": 0.0,
                "oee": 0.0
            }
        
        # Calculate Quality
        total_units = len(data)
        accepted_units = len(data[data['Result'] == 'Accepted'])
        quality = (accepted_units / total_units) * 100 if total_units > 0 else 0
        
        # Calculate Performance
        # Performance = (Ideal Cycle Time * Total Units) / Actual Production Time
        total_production_time = data['Production_Time'].sum()
        ideal_cycle_time = data['Ideal_Cycle_Time'].iloc[0]  # All units have same ideal cycle time
        performance = (ideal_cycle_time * total_units / total_production_time) * 100 if total_production_time > 0 else 0
        
        # Cap performance at 100%
        performance = min(performance, 100.0)
        
        # Calculate Availability
        # For monthly data, planned time is 24/7 operation
        start_time = data['Timestamp'].min()
        end_time = data['Timestamp'].max()
        
        # Calculate total seconds in the time period
        if start_time.month == end_time.month:
            # Same month
            days_in_month = (end_time.replace(day=1) + timedelta(days=32)).replace(day=1) - end_time.replace(day=1)
            planned_time = days_in_month.days * 24 * 60 * 60  # Convert to seconds
        else:
            # Different months, use actual time range
            planned_time = (end_time - start_time).total_seconds()
        
        # Calculate actual run time
        # This is the time between first and last production, plus the production time of the last unit
        time_range = (end_time - start_time).total_seconds()
        actual_run_time = time_range + data['Production_Time'].iloc[-1]  # Add last unit's production time
        
        # Calculate availability
        availability = (actual_run_time / planned_time) * 100 if planned_time > 0 else 0
        
        # Cap availability at 100%
        availability = min(availability, 100.0)
        
        # Calculate OEE
        oee = (availability * performance * quality) / 10000
        
        return {
            "availability": round(availability, 2),
            "performance": round(performance, 2),
            "quality": round(quality, 2),
            "oee": round(oee, 2)
        }
    
    def generate_report(self, metrics: Dict[str, float]) -> str:
        """
        Generate a human-readable report of OEE metrics.
        
        Args:
            metrics (Dict[str, float]): Dictionary containing OEE metrics
            
        Returns:
            str: Formatted report string
        """
        report = f"""
        OEE Analysis Report:
        -------------------
        Availability: {metrics['availability']}%
        Performance: {metrics['performance']}%
        Quality: {metrics['quality']}%
        Overall OEE: {metrics['oee']}%
        
        Interpretation:
        - Availability indicates the percentage of time the machine was running
        - Performance shows how well the machine ran compared to its ideal speed
        - Quality represents the percentage of good units produced
        - OEE is the product of all three factors, representing overall efficiency
        """
        return report 