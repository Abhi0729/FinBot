# 💰 FinBot - Finance Assistant Bot

A full-stack AI-powered sales analysis assistant built with Python, FastAPI, Streamlit, and LangChain.

## 🌟 Features

- **AI-Powered Analysis**: Uses Groq's free LLM (Llama 3.1) for intelligent responses
- **REST API Backend**: FastAPI with multiple endpoints for data and LLM interaction
- **Interactive Frontend**: Beautiful Streamlit dashboard with charts and tables
- **Real-time Analytics**: Visualizations using Plotly
- **Quick Queries**: Pre-built buttons for common questions
- **Natural Language**: Ask questions in plain English

## 📁 Project Structure


## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Groq API Key (free at https://console.groq.com)

### Installation

1. **Clone or create the project folder**
   ```bash
   mkdir finbot
   cd finbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Groq API Key**
   
   Get your free API key from: https://console.groq.com/keys

### Running the Application

1. **Start the FastAPI Backend** (Terminal 1)
   ```bash
   uvicorn main:app --reload
   ```

2. **Start the Streamlit Frontend** (Terminal 2)
   ```bash
   streamlit run frontend.py
   ```

## 🎯 Usage

### Quick Queries (Sidebar)
- 📈 Total Revenue
- 🏆 Top Product
- 🌍 Sales by Region
- 💵 Average Revenue
- 📦 Total Sales Count



## 📊 Sample Data

The bot includes 20 hardcoded sales records with:
- Products: Laptop, Mouse, Keyboard, Monitor, Headphones, USB Cable
- Regions: North, South, East, West
- Revenue range: ₹200 - ₹48,000
- Total revenue: ₹248,570

## 🤖 FinBot Personality

- **Name**: FinBot
- **Domain**: Finance & Sales Analysis
- **Style**: Concise, professional, data-driven
- **Currency**: Indian Rupees (₹)
- **Behavior**: Politely redirects off-topic questions

## 🛠️ Technology Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **LLM Framework**: LangChain
- **LLM Provider**: Groq (free Llama 3.1)
- **Data Processing**: Pandas
- **Visualization**: Plotly
- **API Client**: Requests

##  Sample Prompts

"Which region contributes the largest share of total revenue?"
"What is the average sales quantity per product?"
"Are sales evenly distributed across all regions?"
"Identify the most consistent region in terms of revenue."
"Which region shows the highest variability in revenue?"
"Which products have steady performance across regions?"
"Predict which region could outperform next quarter based on trends."
"Do high-revenue products have fewer sales or more?"
"What’s the revenue contribution percentage of each region?"
"Summarize key takeaways from current sales data."



