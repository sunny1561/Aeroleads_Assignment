import http.client
import json
import re
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMIAN_PAI_KKEY")  # ensure your .env uses correct spelling
SERPER_API_KEY = os.getenv("SERPER_API_kEY")

# -------------------------------------------------
# Helper: Perform search query via Serper API
# -------------------------------------------------
def search(query: str):
    """
    Performs a Google-like search using Serper.dev API and returns the top 3 organic results.
    """
    try:
        conn = http.client.HTTPSConnection("google.serper.dev")
        payload = json.dumps({"q": query})
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()

        response = json.loads(data.decode("utf-8"))
        results = response.get("organic", [])[:3]

        top_results = [
            {
                "title": r.get("title"),
                "industry": r.get("snippet"),
                "linkedin": r.get("link"),
            }
            for r in results
        ]
        return top_results

    except Exception as e:
        print(f"[ERROR] Search API failed: {e}")
        return []


# -------------------------------------------------
# Helper: Scrape LinkedIn company page text
# -------------------------------------------------
def scrape_linkedin_company_profile(url: str) -> str:
    """
    Uses Serper.dev scraper endpoint to fetch text from a LinkedIn company profile URL.
    """
    try:
        conn = http.client.HTTPSConnection("scrape.serper.dev")
        payload = json.dumps({"url": url})
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        conn.request("POST", "/", payload, headers)
        res = conn.getresponse()
        data = res.read()

        json_data = json.loads(data.decode("utf-8"))
        return json_data.get("text", "")

    except Exception as e:
        print(f"[ERROR] Scraping failed for {url}: {e}")
        return ""


# -------------------------------------------------
# Helper: Extract JSON block from Markdown text
# -------------------------------------------------
def extract_json_from_markdown(text: str):
    """
    Extracts JSON object enclosed in a ```json ... ``` block.
    """
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if not match:
        print("[WARN] No JSON block found in model output.")
        return None

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON decode failed: {e}")
        return None


# -------------------------------------------------
# Core: Extract structured data from LinkedIn profile
# -------------------------------------------------
def extract_data_in_json(query: str, model: str = "gemini-2.5-flash", thinking_budget: int = 0):
    """
    Given a company name or query, searches LinkedIn, scrapes data,
    and extracts structured company info in JSON format using Gemini.
    """
    results = search(query)
    if not results:
        return {"error": "No search results found."}

    top_result = results[0]
    linkedin_url = top_result.get("linkedin", "")
    title = top_result.get("title", "")
    industry = top_result.get("industry", "")

    # Fetch company content
    context = scrape_linkedin_company_profile(linkedin_url)
    print(f"[INFO] Extracting company data from: {linkedin_url}")

    # Initialize Gemini client
    client = genai.Client(api_key=GEMINI_API_KEY)
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=thinking_budget)
    )

    # Define structured extraction prompt
    system_prompt = f"""
You are a precise and structured information extractor.

Given the following context about a company, extract and return the information in JSON format with these fields:

- company_name
- industry_type
- funding
- founding_stage
- number_of_employees
- location
- company_description
- type_of_company (private or public)

If any field is not mentioned, return "Not available" for that field.

Context:
{context}

Title: {title}
Industry: {industry}

Output format (strict JSON):
{{
  "company_name": "",
  "industry_type": "",
  "funding": "",
  "founding_stage": "",
  "number_of_employees": "",
  "location": "",
  "company_description": "",
  "type_of_company": ""
}}
"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=system_prompt,
            config=config,
        )
        text_out = response.candidates[0].content.parts[0].text
        json_data = extract_json_from_markdown(text_out)

        if json_data:
            json_data["linkedin_url"] = linkedin_url
        else:
            json_data = {"error": "Failed to parse JSON output", "linkedin_url": linkedin_url}

        return json_data

    except Exception as e:
        print(f"[ERROR] Gemini extraction failed: {e}")
        return {"error": str(e)}


