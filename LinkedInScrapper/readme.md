# AI-Powered Business Intelligence & Content Suite  
**Instant Company Insights + 10x Blog Content in 60 Seconds**

> **Built for speed. Built for impact.**  
> Powered by **Google Gemini AI**, **Streamlit**, and **public web data**.

---

## Executive Summary

| Goal | Solution |
|------|----------|
| **Understand any company instantly** | Enter name → get funding, size, industry, LinkedIn |
| **Publish 10 expert blog posts weekly** | Enter titles → AI writes full Markdown articles |
| **No developers needed after setup** | Fully automated, runs locally or in cloud |

---

## Live Demo (Run in 30 Seconds)

```bash
streamlit run app_blog_generator.py    # Blog Generator
streamlit run app_company_finder.py    # Company Intel(LinkedIn Scrapper )




# Building an AI Blog Generator with Streamlit and Gemini

Creating high-quality technical blogs consistently can be challenging, especially for developers juggling multiple projects. Imagine if you could automate that — generating complete, polished blog posts with code snippets, sections, and takeaways in just one click. That’s exactly what we’ll achieve today using **Streamlit** and **Google’s Gemini API**.

---

## Why Automate Blog Writing?

For developers, blogs are more than writing — they’re a way to:
- Showcase your expertise.
- Document your learning journey.
- Build a professional brand.

But writing takes time. With **LLMs (Large Language Models)** like Gemini, we can automate much of the structure, tone, and flow — while maintaining a developer-focused style.

---

## Step 1: Setting Up the Environment

We’ll use **Streamlit** for the frontend and **Gemini 2.5 Flash** for content generation.

### Install Dependencies

```bash
pip install streamlit google-genai python-dotenv
