# AI-Powered YouTube SEO Automation Workflow

**Project Overview:** This is an end-to-end automation system that takes a YouTube video URL, extracts the video ID, pulls real metadata (views, likes, tags, descriptions) from the YouTube Data API, analyzes engagement metrics using a Python script (pandas), and finally uses the Gemini AI API to structure a comprehensive Markdown SEO report with actionable title and keyword suggestions.

**Tech Stack (STRICT):**
*   **n8n**: Primary automation workflow engine.
*   **YouTube Data API v3**: Real data source for metrics.
*   **Python (pandas)**: Intermediary data analysis and cleanup.
*   **OpenRouter API (Llama 3 / Gemma 3 / Mistral)**: AI-generated insights and recommendations.

---

##  MANUAL STEP 1: Installing n8n Locally
*   **Prerequisites:** You must have Node.js installed ([nodejs.org](https://nodejs.org/)).
*   **Command:** Open your terminal/command prompt and run:
    ```bash
    npm install n8n -g
    ```
*   **Execution:** Run `n8n` in the terminal.
*   **Expected Output:** n8n will start and give you a localhost URL (usually `http://localhost:5678`). Open this in your browser to access the n8n canvas.
*   **Common Error:** `npm ERR! code EACCES` (Permission error). **Fix:** Run terminal as Administrator (Windows) or use `sudo` (Mac/Linux).

##  MANUAL STEP 2: Creating Google Cloud Project & YouTube API Key
*   **Steps:**
    1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
    2.  Click the Project Dropdown at the top left and select **New Project**. Name it `YouTube-SEO-Bot`.
    3.  Go to **Library** (left menu), search for **YouTube Data API v3**, and click **Enable**.
    4.  Go to **Credentials** -> **Create Credentials** -> **API Key**.
*   **Expected Output:** A pop-up will show your new API key `AIzaSy...`. Copy this.

##  MANUAL STEP 3: Getting OpenRouter API Key
*   **Steps:**
    1.  Go to [OpenRouter](https://openrouter.ai/).
    2.  Sign in and go to Settings -> Keys.
    3.  Click **Create Key**.
*   **Expected Output:** A completely free API key `sk-or-v1-...`. Copy this for the OpenRouter node later.

##  MANUAL STEP 4: Python Environment Setup
*   **Steps:**
    1.  Ensure Python is installed (`python --version`).
    2.  Open terminal and run: `pip install pandas`.
    3.  Locate where you saved the `analyze_seo.py` file from this project and copy its **absolute path** (e.g., `C:/Projects/youtube-seo-automation/analyze_seo.py`).

##  MANUAL STEP 5: Testing Endpoints Manually (Verification)
*   **Command:** Test the YouTube API via your browser or terminal to verify your key works:
    ```bash
    curl "https://www.googleapis.com/youtube/v3/videos?part=statistics&id=dQw4w9WgXcQ&key=YOUR_YOUTUBE_API_KEY"
    ```
*   **Expected Output:** A JSON object showing viewCount and likeCount. If you get a 403 error, your API key is invalid or the YouTube Data API v3 wasn't enabled.

##  MANUAL STEP 6: Connecting n8n Workflow
*   **Steps:**
    1.  In n8n (`http://localhost:5678`), create a New Workflow.
    2.  Click the top-right options menu (•••) and select **Import from File**.
    3.  Select the `n8n_workflow.json` provided in this project.
    4.  **Crucial Configurations:**
        *   **Open the Set Video URL Node:** Click on the `youtube_url` value and replace `https://www.youtube.com/watch?v=YOUR_VIDEO_ID` with the actual URL of the YouTube video you want to analyze!
        *   **Open the YouTube API Request Node:** Look under **Query Parameters** and ensure all three of these exist (Click "Add Parameter" if missing):
            *   Name: `id` | Value: `={{ $json.video_id }}`
            *   Name: `part` | Value: `snippet,statistics`
            *   Name: `key` | Value: `YOUR_YOUTUBE_API_KEY` (Paste your real Google API key here)
        *   **Open the Pass to Python Analysis Node (Execute Command):** Change the path `C:/FULL/PATH/TO/analyze_seo.py` to the real absolute path on your PC.
        *   **Open the OpenRouter API Request Node:** Under Headers, paste exactly: `Bearer YOUR_OPENROUTER_API_KEY`.
*   **Wait, how does n8n connect to Python?**
    It uses a **Code** node to write the raw YouTube JSON to a temporary file, completely bypassing Windows quoting errors. Then it uses the **Execute Command** node to run `python analyze_seo.py`, which reads the file, processes metrics with Pandas, and cleanly prints the processed data to `stdout` for the final AI node!

---

##  n8n Workflow Breakdown

1.  **Manual Trigger:** Starts the workflow on click.
2.  **Set Video URL:** Sets a string value (e.g., `https://www.youtube.com/watch?v=...`)
3.  **Extract Video ID (Function):** Uses a simple Regex `/(?:v=|\/)([0-9A-Za-z_-]{11}).*/` to isolate the 11-char ID.
4.  **YouTube API Request (HTTP Request):** Calls `GET https://www.googleapis.com/youtube/v3/videos`. Extracts snippet and statistics.
5.  **Write Node Data to Temp File (Code):** Securely bypasses OS limitations by jumping the JSON out to a local file.
6.  **Pass to Python Analysis (Execute Command):** Runs `python analyze_seo.py`, reads the file, cleans the JSON object.
7.  **Construct OpenRouter Payload (Code):** Perfectly formats the JavaScript JSON execution layer safely escaping quotes.
8.  **OpenRouter API Request (HTTP Request):** Calls `POST https://openrouter.ai/api/v1/chat/completions` with the system prompt and Pandas metrics, sending it to free highly capable LLMs.
9.  **Output Markdown Report (Set):** Extracts the final Markdown text from the OpenRouter JSON response string.

---

## Python Script & OpenRouter API

*   **Python Logic:**
    *   *Engagement rate* = (likes + comments) / views
    *   *Basic keyword extraction* = Strips common stopwords and finds the top 5 words in title/description.
    *   *Weak title check* = Flags titles under 20 or over 65 characters.
*   **OpenRouter Prompt Request Body (JSON sent to OpenRouter):**
    ```json
    {
      "model": "google/gemma-3-12b-it:free",
      "messages": [
        {
          "role": "user",
          "content": "You are an SEO expert. Analyze this video data: [Python JSON Output]..."
        }
      ]
    }
    ```


