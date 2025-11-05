import streamlit as st
import json
import os
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
from google import genai
from google.genai import types
import zipfile
import io

# === CONFIG ===
st.set_page_config(page_title="AI Blog Generator", layout="wide")
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMIAN_PAI_KKEY")  # ensure your .env uses correct spelling
model = "gemini-2.5-flash"  # or gemini-1.5-pro

# Virtual blog folder
BLOG_DIR = "blog"
os.makedirs(BLOG_DIR, exist_ok=True)

# === GEMINI BLOG GENERATION FUNCTION ===
def generate_blog_article(title: str, details: str = "") -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )

    system_prompt = f"""
You are an expert programming blogger. Write a complete, high-quality blog post in Markdown.

Title: {title}
Extra Instructions: {details or "Write for intermediate developers. Include code examples, best practices, and a conclusion."}

Requirements:
- Start with the title as # Heading
- Engaging intro with a real-world hook
- 3–5 sections with ## subheadings
- Include at least 2 code blocks in ```python (or relevant language)
- Use bullet points for tips/lists
- End with a conclusion and key takeaways
- Total: ~800 words
- Tone: clear, professional, practical
- Output ONLY the Markdown content. No JSON. No wrappers.

Begin now.
"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=system_prompt,
            config=config,
        )
        text_out = response.candidates[0].content.parts[0].text
        return text_out

    except Exception as e:
        print(f"[ERROR] Gemini extraction failed: {e}")
        return {"error": str(e)}

# === SAVE ARTICLE ===
def save_article(title: str, content: str) -> str:
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:60]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{BLOG_DIR}/{safe_name}_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(content))
    return filename

# === ZIP HELPER ===
def create_zip(folder):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for root, _, files in os.walk(folder):
            for file in files:
                zf.write(os.path.join(root, file), file)
    buffer.seek(0)
    zip_path = f"{folder}.zip"
    with open(zip_path, "wb") as f:
        f.write(buffer.getvalue())
    return buffer.getvalue()

# === STREAMLIT UI ===
st.title("AI Programming Blog Generator")
st.markdown("Generate **10 articles** instantly using **Gemini**")

st.subheader("Step 1: Enter Article Titles")
st.caption("One per line. Add `| details` for custom instructions.")

example_input = """
Python Asyncio Demystified | For beginners, include event loop diagram in text
FastAPI vs Flask in 2025 | Compare performance, include benchmarks
Dockerizing Streamlit Apps | Step-by-step, include Dockerfile
Mastering Pandas in 10 Tricks | Include real datasets
Git Worktrees for Power Users
Type Hints in Python: Beyond Basics | Include mypy, protocols
Build a CLI Tool with Typer
Web Scraping with Playwright | Handle JS, avoid detection
Real-time Apps with WebSockets
CI/CD with GitHub Actions & Docker
"""

user_input = st.text_area(
    "Paste titles here:",
    value=example_input.strip(),
    height=300
)

# --- Persist generated results ---
if "generated_articles" not in st.session_state:
    st.session_state.generated_articles = []

# === GENERATE ARTICLES ===
if st.button("Generate All Articles", type="primary"):
    lines = [line.strip() for line in user_input.split("\n") if line.strip() and not line.startswith("#")]

    if not lines:
        st.error("Please enter at least one title.")
    else:
        progress = st.progress(0)
        status = st.empty()
        results = []

        for i, line in enumerate(lines):
            status.text(f"Generating {i+1}/{len(lines)}: {line.split('|')[0]}...")

            title = line.split("|")[0].strip()
            details = line.split("|")[1].strip() if "|" in line else ""

            content = generate_blog_article(title, details)
            filepath = save_article(title, content)

            results.append({
                "title": title,
                "file": filepath,
                "preview": content[:500] + "..." if len(content) > 500 else content
            })

            progress.progress((i + 1) / len(lines))

        status.success(f"Generated {len(results)} articles in `{BLOG_DIR}/`")
        st.session_state.generated_articles = results

# === DISPLAY RESULTS ===
if st.session_state.generated_articles:
    st.subheader("Generated Articles")

    for r in st.session_state.generated_articles:
        with st.expander(f"**{r['title']}** → `{os.path.basename(r['file'])}`"):
            st.code(r['preview'])
            if st.button("View Full", key=f"view_{r['file']}"):
                st.session_state[f"show_full_{r['file']}"] = True

    # === FULL PREVIEW ===
    for r in st.session_state.generated_articles:
        if st.session_state.get(f"show_full_{r['file']}"):
            st.markdown(f"---\n**Full Article: {r['title']}**")
            with open(r['file'], "r", encoding="utf-8") as f:
                st.markdown(f.read())
            if st.button("Hide Full", key=f"hide_{r['file']}"):
                st.session_state[f"show_full_{r['file']}"] = False
            st.markdown("---")

    # === DOWNLOAD ALL ===
    st.download_button(
        "Download All as ZIP",
        data=open(f"{BLOG_DIR}.zip", "rb") if os.path.exists(f"{BLOG_DIR}.zip") else create_zip(BLOG_DIR),
        file_name=f"programming_blog_{datetime.now().strftime('%Y%m%d')}.zip",
        mime="application/zip"
    )

# === FOOTER ===
st.markdown("---")
st.markdown(
    """
    <small>
    Articles saved in <code>./blog/</code> as <code>.md</code> files<br>
    Uses your <b>Gemini structured prompt pattern</b> — no external apps needed<br>
    Ready for Jekyll, Hugo, Hashnode, Dev.to, or Notion
    </small>
    """,
    unsafe_allow_html=True
)
