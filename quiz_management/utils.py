import os
import re


def extract_youtube_video_id(url):
    """
    Extracts the 11-character YouTube Video ID from a given URL.
    Returns None if no match is found.
    """
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None


def find_file_by_prefix(directory, prefix, extension=".mp3"):
    """
    Searches a directory for a file starting with a specific prefix
    and ending with a specific extension.
    Returns the full path as a string or None.
    """
    for file in os.listdir(directory):
        if file.startswith(prefix) and file.endswith(extension):
            return str(directory / file)
    return None


def clean_ai_json_response(response_text):
    """
    Cleans a raw AI response string to extract pure JSON.
    Removes markdown code blocks (```json ... ```).
    """
    cleaned_text = response_text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
    return cleaned_text