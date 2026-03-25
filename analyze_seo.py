import pandas as pd
import json
import sys

def analyze_seo(video_data):
    """
    Analyzes YouTube video data and returns SEO insights.
    """
    try:
        # Error Handling
        if not video_data or 'snippet' not in video_data or 'statistics' not in video_data:
            return {"error": "Invalid API data structure passed from YouTube."}

        snippet = video_data['snippet']
        stats = video_data['statistics']
        
        # Metrics Calculation
        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        comments = int(stats.get('commentCount', 0))
        
        df = pd.DataFrame([{'views': views, 'likes': likes, 'comments': comments}])
        df['engagement_rate'] = ((df['likes'] + df['comments']) / df['views'].replace(0, 1)) * 100
        engagement_rate = round(df['engagement_rate'].iloc[0], 2)
        
        # Keyword Extraction
        title = snippet.get('title', '')
        description = snippet.get('description', '')
        text_blob = (title + " " + description).lower()
        
        is_seo_weak = False
        if len(title) < 20 or len(title) > 65:
            is_seo_weak = True 
        
        stopwords = ['the', 'and', 'for', 'with', 'how', 'to', 'is', 'in', 'of', 'a', 'on', 'this', 'you']
        words = [w for w in text_blob.split() if w.isalnum() and w not in stopwords]
        word_counts = pd.Series(words).value_counts()
        top_keywords = list(word_counts.head(5).index)
        
        analysis = {
            "metrics": {
                "views": views,
                "likes": likes,
                "comments": comments,
                "engagement_rate": engagement_rate
            },
            "seo_audit": {
                "title_length": len(title),
                "is_title_weak": is_seo_weak,
                "top_keywords": top_keywords,
                "tags_used": snippet.get('tags', [])[:5] 
            },
            "video_context": {
                "title": title,
                "description_preview": description[:200] + "..." 
            }
        }
        
        return analysis

    except Exception as e:
        return {"error": f"Analysis Error: {str(e)}"}

if __name__ == "__main__":
    try:
        tmp_path = r"C:\Users\KUNCHE SREEMUKHI\AppData\Local\Temp\n8n_yt_input.json"
        
        with open(tmp_path, 'r', encoding='utf-8') as f:
            video_json = json.load(f)

        if isinstance(video_json, list):
            video_json = video_json[0]

        if "items" in video_json and len(video_json["items"]) > 0:
            video_json = video_json["items"][0]

        result = analyze_seo(video_json)
        print(json.dumps(result))

    except json.JSONDecodeError as de:
        print(json.dumps({"error": f"Parse Error: {str(de)}"}))
    except Exception as e:
        print(json.dumps({"error": f"Internal Script Error: {str(e)}"}))
