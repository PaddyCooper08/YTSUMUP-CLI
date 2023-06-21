import requests
from youtube_transcript_api import YouTubeTranscriptApi
import re
import os
import sys
import typer

is_loading = False

def init():
  global answer
  answer = False


def get_video_id(url):
  match = re.search(r"=(\w+)$", url)
  if match:
    return match.group(1)
  else:
    return None


def get_script(video_id, length, word_length=None):
  response = YouTubeTranscriptApi.get_transcript(str(video_id))
  concatenated_text = ''
  for item in response:
    concatenated_text += item['text'] + ' '

  script = concatenated_text.strip()
  if length == 1:
    min_length = int(len(script.split()) / 16)
    max_length = min_length + 25
  elif length == 2:
    min_length = int(len(script.split()) / 12)
    max_length = min_length + 50
  elif length == 3:
    min_length = int(len(script.split()) / 8)
    max_length = min_length + 100
  elif length == 4:
    min_length = word_length
    max_length = word_length + 1
  else:
    min_length = 0
    max_length = 0

  return script, max_length, min_length


def get_summary(script, min_length, max_length):
  API_KEY = os.getenv("API_KEY")
  AUTH = f"Bearer {API_KEY}"
  API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
  headers = {"Authorization": AUTH}

  def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

  output = query({
    "inputs": script,
    "parameters": {
      "min_length": min_length,
      "max_length": max_length
    }
  })

  try:
    return output[0]['summary_text']
  except:
    typer.echo(output)
    sys.exit()


def process_video(url: str, option: int, word_length: int):
  # Process the video URL and chosen option
  id = get_video_id(url=url)
  data = get_script(video_id=id, length=option, word_length=word_length)

  global is_loading
  is_loading = True  # Start the loading animation
  summary = get_summary(script=data[0], min_length=data[2], max_length=data[1])
  
  if answer:
    check_grammar(script=summary)
    
  else:
    is_loading = False
    typer.echo(summary)


def check_grammar(script):
  API_KEY = os.getenv("API_KEY")
  AUTH = f"Bearer {API_KEY}"
  API_URL = "https://api-inference.huggingface.co/models/pszemraj/flan-t5-large-grammar-synthesis"
  headers = {"Authorization": AUTH}

  def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

  output = query({
    "inputs": script,
  })

  if 'generated_text' in output[0]:
    typer.echo(output[0]['generated_text'])
    
  else:
    typer.echo("Failed to generate grammar-corrected text.")
