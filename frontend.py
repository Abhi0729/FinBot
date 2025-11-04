"""
Streamlit Frontend for FinBot
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configuration
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="FinBot - Sales Assistant",
    page_icon="💰",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        padding-bottom: 2rem;
    }
    .chat-box {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        background-color: #f9f9f9;
        margin-bottom: 1rem;
        max-height: 500px;
        overflow-y: auto;
    }
    .user-msg {
        background-color: #dbeafe;
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .bot-msg {
        background-color: #f3f4f6;
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">💰 FinBot - Sales Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your AI-powered finance and sales analysis companion</div>', unsafe_allow_html=True)

# Check API health
try:
    health_response = requests.get(f"{API_URL}/")
    if health_response.status_code != 200:
        st.error("⚠️ Cannot connect to FinBot API. Please ensure the backend is running.")
        st.stop()
except requests.exceptions.ConnectionError:
    st.error("⚠️ Cannot connect to FinBot API. Please start the backend server with: `python main.py`")
    st.stop()

# Fetch data
@st.cache_data
def fetch_sales_data():
    response = requests.get(f"{API_URL}/sales-data")
    return response.json()

@st.cache_data
def fetch_summary():
    response = requests.get(f"{API_URL}/summary")
    return response.json()

sales_data = fetch_sales_data()
summary = fetch_summary()
df = pd.DataFrame(sales_data['data'])

# Sidebar
with st.sidebar:
    st.header("📊 Quick Stats")
    st.metric("Total Revenue", f"₹{summary['total_revenue']:,}")
    st.metric("Total Sales", summary['total_sales'])
    st.metric("Avg Revenue/Sale", f"₹{summary['average_revenue']:,.2f}")
    st.metric("Top Product", summary['top_product'])
    
    st.markdown("---")
    st.header("🎯 Quick Queries")
    
    if st.button("📈 Total Revenue", use_container_width=True):
        st.session_state['quick_query'] = 'total_revenue'
        st.session_state['quick_query_text'] = 'Total Revenue'
    
    if st.button("🏆 Top Product", use_container_width=True):
        st.session_state['quick_query'] = 'top_product'
        st.session_state['quick_query_text'] = 'Top Product'
    
    if st.button("🌍 Sales by Region", use_container_width=True):
        st.session_state['quick_query'] = 'sales_by_region'
        st.session_state['quick_query_text'] = 'Sales by Region'
    
    if st.button("💵 Average Revenue", use_container_width=True):
        st.session_state['quick_query'] = 'average_revenue'
        st.session_state['quick_query_text'] = 'Average Revenue'
    
    if st.button("📦 Total Sales Count", use_container_width=True):
        st.session_state['quick_query'] = 'total_sales'
        st.session_state['quick_query_text'] = 'Total Sales Count'

# Main content area
tab1, tab2, tab3 = st.tabs(["💬 Chat with FinBot", "📊 Data View", "📈 Analytics"])

with tab1:
    st.header("Chat with FinBot")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "question_input" not in st.session_state:
        st.session_state.question_input = ""  # preserve text after submission

    # Handle quick query
    if 'quick_query' in st.session_state:
        with st.spinner("Asking FinBot..."):
            response = requests.post(
                f"{API_URL}/quick-query",
                json={"query_type": st.session_state['quick_query']}
            )
            if response.status_code == 200:
                result = response.json()
                st.session_state.chat_history.append(("You", st.session_state.get('quick_query_text', st.session_state['quick_query'])))
                st.session_state.chat_history.append(("FinBot", result['answer']))
            else:
                st.error("Failed to get response from FinBot")
        del st.session_state['quick_query']
        if 'quick_query_text' in st.session_state:
            del st.session_state['quick_query_text']
        st.rerun()

    # Chat display area (only show when there’s something)
    if len(st.session_state.chat_history) > 0:
        st.markdown('<div class="chat-box">', unsafe_allow_html=True)
        for sender, message in st.session_state.chat_history:
            if sender == "You":
                st.markdown(f'<div class="user-msg">🧑‍💼 <b>You:</b> {message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-msg">🤖 <b>FinBot:</b> {message}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("💬 Start chatting with FinBot using the box below!")

    # User input (persist text)
    user_question = st.text_input(
        "Your Question:",
        value=st.session_state.question_input,
        placeholder="e.g., How is our North region performing?",
        key="question_box"
    )

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        ask_button = st.button("🚀 Ask", use_container_width=True)
    with col2:
        clear_button = st.button("🧹 Clear Chat", use_container_width=True)

    if ask_button and user_question.strip():
        with st.spinner("FinBot is thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": user_question.strip()}
                )
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.chat_history.append(("You", user_question.strip()))
                    st.session_state.chat_history.append(("FinBot", result['answer']))
                    st.session_state.question_input = user_question.strip()  
                    st.rerun()
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Failed to connect to FinBot: {str(e)}")

    if clear_button:
        st.session_state.chat_history = []
        st.session_state.question_input = ""
        st.rerun()

with tab2:
    st.header("Sales Data Table")
    st.dataframe(df, use_container_width=True, height=400)
    
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name="sales_data.csv",
        mime="text/csv"
    )

with tab3:
    st.header("Sales Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        product_revenue = df.groupby('product')['revenue'].sum().reset_index()
        fig1 = px.bar(
            product_revenue,
            x='product',
            y='revenue',
            title='Revenue by Product',
            labels={'revenue': 'Revenue (₹)', 'product': 'Product'},
            color='revenue',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        region_revenue = df.groupby('region')['revenue'].sum().reset_index()
        fig2 = px.pie(
            region_revenue,
            values='revenue',
            names='region',
            title='Revenue Distribution by Region',
            hole=0.4
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    st.subheader("Sales Distribution")
    fig3 = px.histogram(
        df,
        x='revenue',
        nbins=10,
        title='Revenue Distribution',
        labels={'revenue': 'Revenue (₹)', 'count': 'Number of Sales'},
        color_discrete_sequence=['#1f77b4']
    )
    st.plotly_chart(fig3, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888;'>© 2025 SP Software. All rights reserved.</div>",
    unsafe_allow_html=True
)
