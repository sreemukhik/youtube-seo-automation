import os
import re
import json
import requests
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# 1. SETUP & CONFIGURATION
# Load environment variables from .env file
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not YOUTUBE_API_KEY or not GEMINI_API_KEY:
    print("❌ ERROR: Missing API keys!")
    print("Please create a .env file and add your YOUTUBE_API_KEY and GEMINI_API_KEY.")
    exit(1)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def extract_video_id(url):
    """Extract YouTube video ID from URL."""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_youtube_data(video_id):
    """Fetch video snippet and statistics from YouTube Data API."""
    print("📡 Fetching real data from YouTube API...")
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={video_id}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"❌ YouTube API Error: {response.text}")
        exit(1)
        
    data = response.json()
    if not data.get("items"):
        print("❌ Video not found or API key is invalid.")
        exit(1)
        
    return data["items"][0]

def analyze_with_pandas(video_data):
    """Use pandas to calculate key metrics and identify SEO patterns."""
    print("📊 Processing data with pandas...")
    snippet = video_data['snippet']
    stats = video_data['statistics']
    
    # Store raw data in a DataFrame structure for analysis
    df = pd.DataFrame([{
        'Title': snippet.get('title', ''),
        'Description': snippet.get('description', ''),
        'Tags': ", ".join(snippet.get('tags', [])),
        'Views': int(stats.get('viewCount', 0)),
        'Likes': int(stats.get('likeCount', 0)),
        'Comments': int(stats.get('commentCount', 0))
    }])
    
    # Simple calculations
    df['Engagement Rate (%)'] = ((df['Likes'] + df['Comments']) / df['Views']) * 100
    df['Title Length'] = df['Title'].apply(len)
    df['Has Tags'] = df['Tags'].apply(lambda x: len(x) > 0)
    
    # Extract calculated values
    metrics = {
        "title": df['Title'].iloc[0],
        "tags": df['Tags'].iloc[0],
        "views": int(df['Views'].iloc[0]),
        "engagement_rate": round(df['Engagement Rate (%)'].iloc[0], 2),
        "title_length": int(df['Title Length'].iloc[0]),
        "has_tags": bool(df['Has Tags'].iloc[0]),
        # Truncate description to save AI context tokens
        "description_preview": df['Description'].iloc[0][:300] + "..."
    }
    return metrics

def generate_ai_insights(metrics):
    """Pass the processed metrics to Gemini API for SEO recommendations."""
    print("🤖 Generating AI SEO insights via Gemini...")
    prompt = f"""
    You are an expert SEO Automation AI. Analyze this YouTube video's data:
    
    Title: {metrics['title']}
    Title Length: {metrics['title_length']} characters
    Tags used: {metrics['tags']}
    Views: {metrics['views']}
    Engagement Rate: {metrics['engagement_rate']}%
    Description Start: {metrics['description_preview']}

    Based on this real data, generate a concise, structured markdown report with:
    1. **Data Summary**: Briefly summarize the metrics.
    2. **Analysis**: How good is the title length? Is the engagement rate strong?
    3. **Actionable SEO Improvements**: 3 specific recommendations.
    4. **AI Output Suggestion**: Provide 2 better, highly clickable title alternatives.
    """
    
    response = model.generate_content(prompt)
    return response.text

def main():
    print("Welcome to the AI-Powered YouTube SEO Automation Tool!")
    print("-" * 50)
    
    video_url = input("🔗 Enter YouTube Video URL: ").strip()
    video_id = extract_video_id(video_url)
    
    if not video_id:
        print("❌ Invalid YouTube URL.")
        return

    # 1. Fetch
    raw_data = get_youtube_data(video_id)
    
    # 2. Analyze
    metrics = analyze_with_pandas(raw_data)
    
    # 3. Generate Insights
    report_markdown = generate_ai_insights(metrics)
    
    # 4. Save Outputs
    report_filename = f"SEO_Report_{video_id}.md"
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(report_markdown)
        
    print("-" * 50)
    print(f"✅ SUCCESS! Workflow complete.")
    print(f"📄 Your AI Insight Report is saved at: {report_filename}")

if __name__ == "__main__":
    main()
