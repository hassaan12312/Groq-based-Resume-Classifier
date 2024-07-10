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

def select_relevant_candidates(pdf_content, job_desc):
    
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY environment variable")

    chat = ChatGroq(temperature=0, model="llama3-70b-8192", api_key=api_key)

    system_message = "Give candidate name and either yes or no to select"
    human_message = f"Job Description: {job_desc}\nResume Details: {pdf_content}"
    prompt = ChatPromptTemplate.from_messages([("system", system_message), ("human", human_message)])
    response = chat.invoke(human_message)

    suitability_info = response.content
    return suitability_info

def rate_relevant_candidates(pdf_content, job_desc):
    
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY environment variable")

    chat = ChatGroq(temperature=0, model="llama3-70b-8192", api_key=api_key)

    system_message = "Give the candidate name and a score out of 100 for suitability"
    human_message = f"Job Description: {job_desc}\nResume Details: {pdf_content}"
    prompt = ChatPromptTemplate.from_messages([("system", system_message), ("human", human_message)])
    response = chat.invoke(human_message)

    suitability_info = response.content
    return suitability_info

def contains_word_from_list(word_list, a_string):
    return any(word in a_string for word in word_list)

def extract_pdf_content(input_file):
    pdf_reader = PyPDF2.PdfReader(input_file)
    full_text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        page_text = page.extract_text()
        full_text += page_text
    return full_text

def process_directory(directory_path, job_desc, no_of_candidates):
    message = ""
    no_of_candidates = int(no_of_candidates)
    
    count = 0
    not_selected = ['not a good match', 'not appear to be a good fit', 'not a good fit', 
                    'does not match the job description','does not appear to have the necessary skills',
                    'does not appear to have the necessary experience', 'lack', 'not directly related','does not meet the requirements',
                    'does not demonstrate', 'do not align with the requirements', 'not a suitable candidate']
    selected_candidates_filenames = []
    try:
        pdf_files = [file for file in os.listdir(directory_path) if file.lower().endswith(".pdf")]
        for pdf_file in pdf_files:
            pdf_path = os.path.join(directory_path, pdf_file)
            with open(pdf_path, "rb") as pdf_file_obj:
                content = extract_pdf_content(pdf_file_obj)
                suitability_result = select_relevant_candidates(content, job_desc)
                suitability_result = suitability_result.lower()
                count += 1
                print("Number of pdf files read: ", count)
                
                if contains_word_from_list(not_selected, suitability_result):
                    continue
                
                else:
                    selected_candidates_filenames.append(pdf_path)
        
        count2 = 0
        qualified_candidates_filenames = {}
        
        for pdf_file in selected_candidates_filenames:
            with open(pdf_file, "rb") as pdf_file_obj:
                content = extract_pdf_content(pdf_file_obj)
                suitability_result = rate_relevant_candidates(content, job_desc)
                suitability_result = suitability_result.lower()
                count2 += 1
                print("Number of pdf files read: ", count2)
                
                if any(word in suitability_result for word in ['perfect fit', 'qualified', 'capable']):
                    qualified_candidates_filenames[pdf_file] = 0
                elif any(word in suitability_result for word in ['strong fit', 'promise', 'promising', 'asset']):
                    qualified_candidates_filenames[pdf_file] = 1
                else:
                    qualified_candidates_filenames[pdf_file] = 2

            

        sorted_dict = dict(sorted(qualified_candidates_filenames.items(), key=lambda item: item[1]))
        
        if len(sorted_dict) <= no_of_candidates:
            key_list = list(sorted_dict.keys())
            message = "The file paths of the top candidates are:\n"
            for i in range(len(key_list)):
                message += key_list[i] + "\n"
        else:
            key_list = list(sorted_dict.keys())[:no_of_candidates]
            message = "The file paths of the top candidates are:\n"
            for i in range(len(key_list)):
                message += key_list[i] + "\n"
        
        return message
        
    except FileNotFoundError:
        print(f"Directory not found: {directory_path}")
        return
            
    
#-----------------------main------------------------
with gr.Row() as demo:
    with gr.Column():
        directory_to_read = gr.Textbox(label = 'Directory path', placeholder = 'Enter Directory path......')
    with gr.Column():
        no_of_candidates = gr.Textbox(label = 'Number of candidates', placeholder = 'Enter number of candidates......')
    with gr.Column():
        job_desc = gr.Textbox(label = 'Job Description', placeholder = 'Enter Job Description......', lines = 10)
    
gr.Interface(fn = process_directory, inputs = [directory_to_read, job_desc, no_of_candidates], outputs = gr.Textbox(label = 'Output')).launch()