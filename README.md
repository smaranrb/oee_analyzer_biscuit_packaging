# OEE Analyzer - Packaging Machine Efficiency Calculator

A GenAI-powered web application that calculates and displays the Overall Equipment Efficiency (OEE) of packaging machines in a biscuit manufacturing plant.

## Features

- Natural language query interface
- Modular agent-based architecture
- Real-time OEE calculations
- Conversational UI with context retention

## System Architecture

The application follows an agent-based design with three main components:

1. **QueryAgent**: Processes natural language queries using LLaMA 3
2. **DataAgent**: Handles data loading and filtering
3. **OEEAgent**: Computes OEE metrics (Availability, Performance, Quality)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up your Hugging Face API key in a `.env` file:
```
HUGGINGFACE_API_KEY=your_api_key_here
```

## Usage

1. Place your Excel data file in the `data` directory
2. Run the application:
```bash
python oee_analyzer/main.py
```
3. Access the web interface at the provided local URL

## Data Format

The Excel file should contain the following columns:
- Unit_ID
- Timestamp
- Device_ID
- Location
- Production_Time (seconds)
- Ideal_Cycle_Time (seconds)
- Result (Accepted/Rejected)

## License

MIT License

