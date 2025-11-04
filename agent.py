import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import pandas as pd


with open("config.json") as f:
    config = json.load(f)


class FinBot:
    """Finance Assistant Bot with personality and domain expertise"""
    
    def __init__(self, api_key=None, config_path="config.json"):
        """Initialize FinBot with Groq API"""
        if api_key:
            self.api_key = api_key
        else:
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    self.api_key = config.get("groq_api_key")
            except FileNotFoundError:
                raise FileNotFoundError(f"Config file '{config_path}' not found.")
            
        if not self.api_key:
            raise ValueError("Groq API key not found. Please set it in config.json or pass manually.")
    
        
        self.llm = ChatGroq(
            temperature=0.3,
            model_name="llama-3.1-8b-instant",
            groq_api_key=self.api_key
        )
        
        self.system_prompt = """You are FinBot, a friendly finance and sales analysis assistant.
                    Your domain: Finance & Sales Data Analysis
                    Your style: Concise, professional, data-driven.

                    Guidelines:
                    1. Always format currency in Indian Rupees (₹)
                    2. Provide clear numeric answers with context
                    3. Keep responses under 100 words unless analysis requires more
                    4. If asked about non-finance topics, politely redirect: "I specialize in finance and sales analysis. How can I help with your sales data?"
                    5. Be friendly but professional.

                    You have access to the following financial dataset summary and detailed breakdown:

                    === SUMMARY ===
                    {data_summary}

                    === DETAILED BREAKDOWN ===
                    {detailed_data}

                    Now, answer the following question from the user:
                    {question}

                    Provide a concise, insightful, and data-backed explanation."""


    

    def prepare_detailed_data(self, sales_df: pd.DataFrame) -> str:
        """Prepare detailed data breakdown for LLM"""
        
        # Product-wise analysis
        product_stats = sales_df.groupby('product').agg({
            'revenue': ['sum', 'mean', 'count'],
            'quantity': 'sum'
        }).round(2)
        
        product_breakdown = "PRODUCT ANALYSIS:\n"
        for product in product_stats.index:
            total_rev = product_stats.loc[product, ('revenue', 'sum')]
            avg_rev = product_stats.loc[product, ('revenue', 'mean')]
            count = product_stats.loc[product, ('revenue', 'count')]
            total_qty = product_stats.loc[product, ('quantity', 'sum')]
            
            product_breakdown += f"- {product}: {int(count)} sales, Total Revenue ₹{total_rev:,.0f}, Avg Revenue/Sale ₹{avg_rev:,.2f}, Total Quantity {int(total_qty)}\n"
        
        # Region-wise analysis
        region_stats = sales_df.groupby('region').agg({
            'revenue': ['sum', 'mean', 'count'],
            'quantity': 'sum'
        }).round(2)
        
        region_breakdown = "\nREGION ANALYSIS:\n"
        for region in region_stats.index:
            total_rev = region_stats.loc[region, ('revenue', 'sum')]
            avg_rev = region_stats.loc[region, ('revenue', 'mean')]
            count = region_stats.loc[region, ('revenue', 'count')]
            
            region_breakdown += f"- {region}: {int(count)} sales, Total Revenue ₹{total_rev:,.0f}, Avg Revenue/Sale ₹{avg_rev:,.2f}\n"
        
        # Top performers
        top_product = product_stats[('revenue', 'sum')].idxmax()
        top_product_revenue = product_stats.loc[top_product, ('revenue', 'sum')]
        
        top_region = region_stats[('revenue', 'sum')].idxmax()
        top_region_revenue = region_stats.loc[top_region, ('revenue', 'sum')]
        
        top_performers = f"\nTOP PERFORMERS:\n- Best Product: {top_product} (₹{top_product_revenue:,.0f})\n- Best Region: {top_region} (₹{top_region_revenue:,.0f})\n"
        
        return product_breakdown + region_breakdown + top_performers

    def get_response(self, question: str, data_summary: dict, sales_df: pd.DataFrame = None) -> str:
        """Generate response based on user question and data"""

        # Prepare detailed data breakdown
        detailed_data = ""
        if sales_df is not None:
            detailed_data = self.prepare_detailed_data(sales_df)

        # Include region sales explicitly
        sales_by_region_text = "\n".join(
            [f"- {region}: ₹{revenue:,}" for region, revenue in data_summary['sales_by_region'].items()]
        )

        # Format summary
        summary_text = f"""
            Total Revenue: ₹{data_summary['total_revenue']:,}
            Total Sales: {data_summary['total_sales']}
            Average Revenue per Sale: ₹{data_summary['average_revenue']:,.2f}
            Top Product: {data_summary['top_product']} (₹{data_summary['top_product_revenue']:,})
            Sales by Region:
            {sales_by_region_text}
        """

        prompt = ChatPromptTemplate.from_template(self.system_prompt)
        chain = prompt | self.llm | StrOutputParser()

        try:
            response = chain.invoke({
                "detailed_data": detailed_data,
                "data_summary": summary_text,
                "question": question
            })
            return response
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again."


    def get_predefined_response(self, query_type: str, data_summary: dict, sales_df: pd.DataFrame = None) -> str:
        """Handle common predefined queries with calculated responses"""
        
        if sales_df is None:
            # Fallback to basic responses
            responses = {
                "total_revenue": f"The total revenue across all sales is ₹{data_summary['total_revenue']:,}.",
                "top_product": f"The top product by revenue is {data_summary['top_product']}, generating ₹{data_summary['top_product_revenue']:,} in total sales.",
                "average_revenue": f"The average revenue per sale is ₹{data_summary['average_revenue']:,.2f}.",
                "sales_by_region": "Sales by region:\n" + "\n".join([
                    f"• {region}: ₹{revenue:,}" 
                    for region, revenue in data_summary['sales_by_region'].items()
                ]),
                "total_sales": f"We have recorded {data_summary['total_sales']} total sales transactions."
            }
            return responses.get(query_type, None)
        
        # Enhanced responses with detailed calculations
        if query_type == "total_revenue":
            return f"Our total revenue across all {data_summary['total_sales']} sales is ₹{data_summary['total_revenue']:,}. This includes sales from all products and regions."
        
        elif query_type == "top_product":
            product_revenue = sales_df.groupby('product')['revenue'].sum().sort_values(ascending=False)
            top = product_revenue.index[0]
            top_rev = product_revenue.iloc[0]
            second = product_revenue.index[1] if len(product_revenue) > 1 else None
            
            response = f"The top product by revenue is **{top}** with ₹{top_rev:,.0f} in total sales."
            if second:
                second_rev = product_revenue.iloc[1]
                response += f" This is significantly ahead of the second-best product, {second} (₹{second_rev:,.0f})."
            return response
        
        elif query_type == "average_revenue":
            avg = data_summary['average_revenue']
            median = sales_df['revenue'].median()
            return f"The average revenue per sale is ₹{avg:,.2f}, with a median of ₹{median:,.2f}. This means half of our sales are above ₹{median:,.2f}."
        
        elif query_type == "sales_by_region":
            region_revenue = sales_df.groupby('region')['revenue'].sum().sort_values(ascending=False)
            response = "**Sales by Region:**\n\n"
            for region, revenue in region_revenue.items():
                count = len(sales_df[sales_df['region'] == region])
                avg = revenue / count
                response += f"• **{region}**: ₹{revenue:,} ({count} sales, avg ₹{avg:,.2f}/sale)\n"
            return response
        
        elif query_type == "total_sales":
            products = sales_df['product'].nunique()
            regions = sales_df['region'].nunique()
            return f"We have recorded **{data_summary['total_sales']} total sales** transactions across {products} different products and {regions} regions."
        
        return None