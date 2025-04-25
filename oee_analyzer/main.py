import gradio as gr
from typing import List, Tuple
import os
from dotenv import load_dotenv
from agents.query_agent import QueryAgent
from agents.data_agent import DataAgent
from agents.oee_agent import OEEAgent

load_dotenv()

class OEEAnalyzer:
    def __init__(self):
        """Initialize the OEE Analyzer with all required agents."""
        self.query_agent = QueryAgent()
        self.data_agent = DataAgent()
        self.oee_agent = OEEAgent()
    
    def process_query(self, query: str, history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Process a user query and return the response.
        
        Args:
            query (str): User's query
            history (List[Tuple[str, str]]): Chat history
            
        Returns:
            Tuple[str, List[Tuple[str, str]]]: Response and updated chat history
        """
        try:
            # Process query with QueryAgent
            params = self.query_agent.process_query(query)
            
            # Check if we need clarification
            if self.query_agent.needs_clarification(params):
                clarification = self.query_agent.get_clarification_prompt(params)
                return clarification, history + [(query, clarification)]
            
            # Get filtered data
            filtered_data = self.data_agent.filter_data(params)
            
            if filtered_data.empty:
                no_data_msg = "No data found for the specified parameters. Please check your query and try again."
                return no_data_msg, history + [(query, no_data_msg)]
            
            # Calculate OEE metrics
            metrics = self.oee_agent.calculate_oee(filtered_data)
            
            # Generate report
            report = self.oee_agent.generate_report(metrics)
            
            return report, history + [(query, report)]
            
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            return error_msg, history + [(query, error_msg)]

def create_interface():
    """Create and launch the Gradio interface."""
    analyzer = OEEAnalyzer()
    
    with gr.Blocks(title="OEE Analyzer") as interface:
        gr.Markdown("# OEE Analyzer - Packaging Machine Efficiency Calculator")
        gr.Markdown("Ask questions about your packaging machine's OEE in natural language.")
        
        chatbot = gr.Chatbot(
            height=500,
            label="Chat History",
            show_copy_button=True
        )
        msg = gr.Textbox(
            label="Your Query",
            placeholder="e.g., 'What was the OEE for Machine A in January?'",
            show_label=True
        )
        clear = gr.Button("Clear Chat")
        
        def respond(message, chat_history):
            response, new_history = analyzer.process_query(message, chat_history)
            return "", new_history
        
        msg.submit(
            respond,
            [msg, chatbot],
            [msg, chatbot]
        )
        
        clear.click(lambda: [], None, chatbot, queue=False)
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(share=True)
