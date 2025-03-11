# Extract audio from a video file
import moviepy
from pydub import AudioSegment
import speech_recognition as sr
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def video_to_audio(file):
  cvt_video = moviepy.editor.VideoFileClip(file)
  ext_audio = cvt_video.audio
  ext_audio.writeaudiofile("audio.mp3")

audio_list = [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a",".wma", ".aiff", ".aif", ".opus"]
video_list = [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv",".webm", ".m4v", ".3gp", ".ts", ".rmvb"]
transcript_list = [".txt", ".doc", ".docx", ".pdf", ".srt", ".vtt",".sbv", ".ass", ".ssa", ".xml", ".json", ".csv"]

def identify(file):
  extension = file.split('.')[1]
  if extension in transcript_list:
    return 0
  elif extension in audio_list:
    return 1
  elif extension in video_list:
    return 2
  else:
    return None

def convert_to_wav(input_file, output_file="output.wav"):
    audio = AudioSegment.from_file(input_file)

    audio.export(output_file, format="wav")
    print(f"Conversion successful! Saved as {output_file}")

def audio_to_text(file):
    extension=file.split('.')[1]
    if extension != 'wav':
      convert_to_wav(file)
    r = sr.Recognizer()
    audio_file = sr.AudioFile("output.wav")
    with audio_file as source:
        audio_text = r.record(source)

    try:
        text = r.recognize_google(audio_text)
        with open("result.txt", "w") as f:
            f.write(text)
        print("Transcription saved to result.txt")
    except sr.UnknownValueError:
        print("Speech Recognition could not understand the audio.")
    except sr.RequestError:
        print("Could not request results from Google API.")

def generate_pdf(content, filename="output.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()

    story = []

    for point in content.strip().split("\n"):
        bullet = Paragraph(f"• {point.strip()}", styles['Normal'])
        story.append(bullet)
        story.append(Spacer(1, 10))

    doc.build(story)
    print(f"PDF '{filename}' generated successfully!")


def word_count(content):
  words = content.split()
  return len(words)

