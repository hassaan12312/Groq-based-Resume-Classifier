import gradio as gr
import PyPDF2
from groq import Groq
import os
import random
from langchain.chains.conversation.base import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate


from dotenv import load_dotenv
load_dotenv()
os.environ['GROQ_API_KEY'] = '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'

def send_to_groq(pdf_content, job_desc):
    
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY environment variable")

    chat = ChatGroq(temperature=0, model="llama3-70b-8192", api_key=api_key)

    system_message = "Strictly follow my instructions, give response in just 5 lines state whether the person is suitable for the job and why"
    human_message = f"Job Description: {job_desc}\nResume Details: {pdf_content}"
    prompt = ChatPromptTemplate.from_messages([("system", system_message), ("human", human_message)])
    response = chat.invoke(human_message)

    suitability_info = response.content
    return suitability_info



def extract_pdf_content(input_file, job_desc):
    # Create a PDF reader object
    pdf_reader = PyPDF2.PdfReader(input_file)

    # Initialize an empty string to store the extracted text
    full_text = ""

    # Iterate through each page in the PDF
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        page_text = page.extract_text()
        full_text += page_text

    return send_to_groq(full_text, job_desc)


with gr.Row() as demo:
    with gr.Column():
        pdf_file = gr.File(label = 'Upload File')
    with gr.Column():
        job_desc = gr.Textbox(label = 'Job Description', placeholder = 'Enter Job Description......', lines = 10)
    
gr.Interface(fn = extract_pdf_content, inputs = [pdf_file,job_desc], outputs = gr.Textbox(label = 'Output')).launch()