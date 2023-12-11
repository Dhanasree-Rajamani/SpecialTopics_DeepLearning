from flask import Flask, render_template, request, jsonify
import re
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import openai
import requests
from googleapiclient.discovery import build

app = Flask(__name__)

YOUTUBE_API_KEY = 'AIzaSyAWZtoP7bZxRWHUaxmzUtmY6csQ0m7KhVE'  # Replace with your YouTube API key
OPENAI_API_KEY = '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'    # Replace with your OpenAI API key

def extract_video_id_from_url(url):
    """
    Extracts the YouTube video ID from a given URL.
    """
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_youtube_video_details(url, youtube_api_key):
    """
    Fetches details of a YouTube video given its URL.
    """
    video_id = extract_video_id_from_url(url)

    # Initialize YouTube API client
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    request = youtube.videos().list(part="snippet", id=video_id)
    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        title = response['items'][0]['snippet']['title']
        author = response['items'][0]['snippet']['channelTitle']
        description = response['items'][0]['snippet']['description']
        return title, author, description
    else:
        return "Video not found", "", ""

def get_video_transcript(video_url):
    try:
        video_id = extract_video_id_from_url(video_url)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Fetch the transcript in English or the first available transcript
        if transcript_list.find_transcript(['en']):
            transcript = transcript_list.find_transcript(['en']).fetch()
        else:
            transcript = transcript_list[0].fetch()

        # Combine the text of the transcript
        combined_transcript = ' '.join([t['text'] for t in transcript])
        return combined_transcript
    except NoTranscriptFound:
        return "No transcript found for this video."

def summarize_text(text, openai_api_key):
    """
    Summarizes the given text using OpenAI's GPT-3.
    """
    openai.api_key = openai_api_key

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
        ],
        max_tokens=1500
    )

    return response['choices'][0]['message']['content'].strip()

def split_text_into_chunks(text, chunk_size=4000):
    """
    Splits text into smaller chunks, each with a maximum of chunk_size characters.
    """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def summarize_large_text(text, openai_api_key,summary_length, summary_depth):
    """
    Splits a large text into chunks and summarizes each chunk.
    """
    chunks = split_text_into_chunks(text, summary_length)    
    summaries = [summarize_text(chunk, openai_api_key) for chunk in chunks[:summary_depth]]
    #summaries = [summarize_text(chunk, openai_api_key) for chunk in chunks]
    return ' '.join(summaries)

# Add this function to get the top comments for a video
def get_top_video_comments(video_id, youtube_api_key):
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    
    # Fetch the top comments for the video (adjust maxResults as needed)
    response = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=10,  # You can change this to get more or fewer comments
        textFormat="plainText"
    ).execute()
    
    comments = []
    for item in response["items"]:
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)
    
    return comments

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/generate_summary', methods=['GET'])
def generate_summary():
    print("Received a request to /generate_summary")
    youtube_url = request.args.get('youtubeUrl')
    summary_length = int(request.args.get('summaryLength', default=500))
    summary_depth = int(request.args.get('summaryDepth', default=3))


    # Fetch video details
    title, author, description = get_youtube_video_details(youtube_url, YOUTUBE_API_KEY)

    # Get summary of the description
    description_summary = summarize_text(description, OPENAI_API_KEY)

    # Fetch the transcript
    transcript = get_video_transcript(youtube_url)

    # Check if a transcript was found
    if transcript != "No transcript found for this video.":
        # Get summary of the transcript
        transcript_summary = summarize_large_text(transcript, OPENAI_API_KEY,summary_length, summary_depth)
    else:
        transcript_summary = "Transcript not available for this video."

    video_id = extract_video_id_from_url(youtube_url)
    youtube_api_url = f"https://www.googleapis.com/youtube/v3/videos?key={YOUTUBE_API_KEY}&part=snippet&id={video_id}"
    youtube_response = requests.get(youtube_api_url)
    youtube_data = youtube_response.json()
    video_id = extract_video_id_from_url(youtube_url)

    # Get the top comments
    top_comments = get_top_video_comments(video_id, YOUTUBE_API_KEY)

    # Summarize the top comments
    top_comments_summary = summarize_text("\n".join(top_comments), OPENAI_API_KEY)


    if 'items' in youtube_data and len(youtube_data['items']) > 0:
        thumbnail_url = youtube_data['items'][0]['snippet']['thumbnails']['medium']['url']
    else:
        thumbnail_url = ""

    return jsonify({'title': title, 'author': author, 'descriptionSummary': description_summary, 'transcriptSummary': transcript_summary, "thumbnailurl": thumbnail_url, 'videoId': video_id, 'topCommentsSummary': top_comments_summary })

if __name__ == '__main__':
    app.run(debug=True)
