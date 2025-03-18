# text_summarizer.py

import os
import requests
import tempfile
import traceback
from openai import AzureOpenAI
from dotenv import load_dotenv
import PyPDF2  # PyPDF2 ile PDF'den metin çekmek (alternatif: pypdf, pdfplumber)

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-07-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

def extract_text_from_pdf(pdf_file_path):
    """
    Basitçe PyPDF2 ile PDF'in tüm sayfalarını oku ve metin olarak döndür.
    """
    text = ""
    with open(pdf_file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def chunk_text(text, chunk_size=2000, overlap=200):
    """
    Metni belirli token/cümle sayıları için parçalara ayırmak (örnek basitçe).
    Burada chunk_size'ı kabaca karakter cinsinden hesaplayabiliriz.
    Overlap: Parçalar arasında tekrar (context korumak için).
    Daha sofistike bir yaklaşım: cümle cümle token sayısı ölçmek.

    NOT: '2000 karakter' = ~ 500 token civarı çok kabaca.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap  # bir miktar overlap
    return chunks

def summarize_chunk(chunk, style="short"):
    """
    Tek bir metin parçasını ChatGPT ile özetler.
    style: "short", "5_sentences", "key_points" vb. parametreye göre prompt ayarlanabilir
    """
    if style == "short":
        prompt = f"Özetle: {chunk}\nLütfen kısa, öz ve anlaşılır bir özet yaz."
    elif style == "5_sentences":
        prompt = (
            f"Özetle: {chunk}\n"
            "Lütfen en fazla 5 cümlelik Türkçe bir özet yaz."
        )
    elif style == "key_points":
        prompt = f"Özetle: {chunk}\nLütfen en önemli maddeleri listele."
    else:
        prompt = f"Özetle: {chunk}\n"

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_DEPLOYMENT_NAME"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def summarize_text(text, style="short"):
    """
    Uzun bir metni chunk'layarak parça parça özet al, sonra özetleri birleştir.
    Ardından final birleştirilmiş özeti yeniden özetleyebilirsin (iterative).
    """
    # 1) Metni chunk'la
    chunks = chunk_text(text, chunk_size=2000, overlap=200)
    partial_summaries = []

    # 2) Her chunk'ı özetle
    for i, c in enumerate(chunks):
        summary = summarize_chunk(c, style=style)
        partial_summaries.append(summary)

    # 3) Parça özetlerini birleştirip tekrar özet
    combined_text = "\n".join(partial_summaries)
    final_summary = summarize_chunk(combined_text, style="short")  # Tekrar 'short' seçtik
    return final_summary

def summarize_pdf_from_url(pdf_url, style="short"):
    """
    PDF URL'sini indir, metni çıkar, chunk'la ve özetle. Sonucu döndür.
    """
    try:
        # PDF'i geçici dizine indir
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            response = requests.get(pdf_url)
            if response.status_code != 200:
                return "Cannot download PDF from the given URL."
            tmp_file.write(response.content)
            tmp_file.flush()
            temp_pdf_path = tmp_file.name

        # PDF metnini çıkart
        text = extract_text_from_pdf(temp_pdf_path)
        if not text.strip():
            return "PDF içeriği okunamadı veya boş görünüyor."

        # Metni özetle
        final_summary = summarize_text(text, style=style)
        return final_summary

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ Error in summarize_pdf_from_url:\n{error_details}")
        return f"Error while summarizing PDF: {str(e)}"
