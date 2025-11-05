import streamlit as st
import pandas as pd
import time
from websearch import extract_data_in_json  # Import your function that fetches the JSON result

# ------------------ STREAMLIT APP ------------------ #

st.title("🏢 Company Information Finder (via LinkedIn & Web Search)")

st.write("""
🔎 **Enter a company name or query** to fetch publicly available company data  
including industry type, funding, size, and official LinkedIn profile.

⚠️ **Note:** This tool uses *only publicly accessible data* (no login or scraping private content).
""")

# Input query
query_input = st.text_area(
    "Enter company name or search query (one per line):",
    placeholder="Example:\nAeroLeads\nFreshworks San Francisco\nStripe"
)

# Process on button click
if st.button("Fetch Company Data"):
    queries = [q.strip() for q in query_input.split("\n") if q.strip()]
    
    if not queries:
        st.warning("⚠️ Please enter at least one company name or query.")
    else:
        st.info("🔍 Searching... please wait a few seconds per query.")
        
        results = []
        for query in queries:
            with st.spinner(f"Fetching info for: {query}"):
                try:
                    data = extract_data_in_json(query)  # Your function should return a dict
                    results.append(data)
                except Exception as e:
                    results.append({"company_name": query, "Error": str(e)})
                time.sleep(2)  # polite delay between requests
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        st.success("✅ Data fetched successfully!")
        
        # Show DataFrame
        st.dataframe(df)

        # Add clickable LinkedIn URL (if present)
        def make_clickable(link):
            if pd.notna(link) and link.startswith("http"):
                return f'<a href="{link}" target="_blank">View LinkedIn</a>'
            return "Not available"
        
        if "linkedin_url" in df.columns:
            df["LinkedIn Profile"] = df["linkedin_url"].apply(make_clickable)
            st.markdown(
                df[["company_name", "industry_type", "funding", 
                    "founding_stage", "number_of_employees", 
                    "location", "LinkedIn Profile"]]
                .to_html(escape=False, index=False),
                unsafe_allow_html=True
            )
        
        # Save CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name="company_data.csv",
            mime="text/csv"
        )
