from functions import video_to_audio, identify, convert_to_wav, audio_to_text, generate_pdf, word_count
from transformers import pipeline

def main(file):
  try:
    result = identify(file)
    if result == 0:
      pass
    elif result == 1:
      audio_to_text(file)
    elif result == 2:
      video_to_audio(file)
      audio_to_text("audio.mp3")
    else:
      return None
    try:
      with "result.txt" as f:
        data = f.read()
      summarizer = pipeline("summarization")
      length = word_count(data)
      summary = summarizer(data,max_length = int(length*0.75) ,min_length = int(length*0.5),do_sample=False)
      generate_pdf(summary[0]['summary_text'])

    except Exception as e:
      print(f"Error: {e}")

  except Exception as e:
    print(f"Error: {e}")

main()