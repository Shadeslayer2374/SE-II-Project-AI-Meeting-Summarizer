import os
import torch
from moviepy import VideoFileClip
from transformers import pipeline
import nltk
from fpdf import FPDF

# Initialize NLTK (only need to do this once)
nltk.download("punkt")
nltk.download("stopwords")

# Check GPU availability
print(f"GPU available: {torch.cuda.is_available()}")
print(f"GPU device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")

def extract_audio(video_path):
    """Extract audio from video file and save as WAV (CPU-only task)"""
    video = VideoFileClip(video_path)
    audio_filename = os.path.join(os.path.dirname(video_path), "temp_audio.wav")
    video.audio.write_audiofile(audio_filename, codec="pcm_s16le")
    return audio_filename

def transcribe_audio(audio_path):
    """Transcribe audio using Whisper model with GPU acceleration"""
    device = 0 if torch.cuda.is_available() else -1  # 0 = GPU, -1 = CPU
    transcriber = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-small",
        device=device  # Uses GPU if available
    )
    result = transcriber(audio_path, return_timestamps=True)
    return result["text"]

def summarize_text(text):
    """Summarize text using BART model with GPU acceleration"""
    device = 0 if torch.cuda.is_available() else -1  # 0 = GPU, -1 = CPU
    summarizer = pipeline(
        "summarization",
        model="facebook/bart-large-cnn",
        device=device  # Uses GPU if available
    )
    
    # Split text into chunks if too long
    max_chunk = 1024
    chunks = [text[i:i + max_chunk] for i in range(0, len(text), max_chunk)]
    
    # Summarize each chunk and combine
    summary = " ".join([
        summarizer(chunk, max_length=100, min_length=30, do_sample=False)[0]["summary_text"]
        for chunk in chunks
    ])
    return summary

def create_pdf(transcription, summary, output_path):
    """Create PDF with transcription and summary (CPU-only task)"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add title
    pdf.cell(200, 10, txt="Video Transcription and Summary", ln=1, align='C')
    pdf.ln(10)
    
    # Add transcription section
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt="Transcription:", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, txt=transcription)
    pdf.ln(10)
    
    # Add summary section
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt="Summary:", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, txt=summary)
    
    pdf.output(output_path)

def process_video_to_pdf(video_path, pdf_output_path):
    """Main function to process video and generate PDF"""
    try:
        # Step 1: Extract audio
        print("Extracting audio...")
        audio_path = extract_audio(video_path)
        
        # Step 2: Transcribe audio
        print("Transcribing audio (this may take a while)...")
        transcription = transcribe_audio(audio_path)
        
        # Step 3: Summarize transcription
        print("Generating summary...")
        summary = summarize_text(transcription)
        
        # Step 4: Create PDF
        print("Creating PDF...")
        create_pdf(transcription, summary, pdf_output_path)
        
        # Clean up temporary audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        print("PDF generated successfully!")
        return True, "PDF generated successfully"
    
    except Exception as e:
        # Clean up partially created files
        if 'audio_path' in locals() and os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(pdf_output_path):
            os.remove(pdf_output_path)
            
        print(f"Error: {str(e)}")
        return False, str(e)

def process_video(video_path, file_id):
    """Process video file and generate PDF summary"""
    pdf_path = os.path.join('temp_uploads', f'summary_{file_id}.pdf')
    success, message = process_video_to_pdf(video_path, pdf_path)
    if not success:
        raise Exception(f"Video processing failed: {message}")
    return pdf_path

def process_audio(audio_path, file_id):
    """Process audio file and generate PDF summary"""
    pdf_path = os.path.join('temp_uploads', f'summary_{file_id}.pdf')
    
    try:
        # Step 1: Transcribe audio
        transcription = transcribe_audio(audio_path)
        
        # Step 2: Summarize transcription
        summary = summarize_text(transcription)
        
        # Step 3: Create PDF
        create_pdf(transcription, summary, pdf_path)
        
        return pdf_path
    
    except Exception as e:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        raise Exception(f"Audio processing failed: {str(e)}")

def process_transcript(transcript_path, file_id):
    """Process text transcript and generate PDF summary"""
    pdf_path = os.path.join('temp_uploads', f'summary_{file_id}.pdf')
    
    try:
        # Read the transcript file
        ext = os.path.splitext(transcript_path)[1].lower()
        
        if ext == '.pdf':
            # For PDF files, you would need to extract text first
            # This is just a placeholder - you'd need proper PDF text extraction
            with open(transcript_path, 'rb') as f:
                text = "PDF text extraction would go here"
        else:  # txt, docx
            with open(transcript_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        # Summarize text
        summary = summarize_text(text)
        
        # Create PDF
        create_pdf(text, summary, pdf_path)
        
        return pdf_path
    
    except Exception as e:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        raise Exception(f"Transcript processing failed: {str(e)}")