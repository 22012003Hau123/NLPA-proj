import tkinter as tk
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import requests
import http.client
import json
import os
import urllib.parse
from fpdf import FPDF
import PyPDF2
import pdfplumber
import random
from libser_engine.engine import accumulate, Extract
import time
import random
import re
import sys

listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
import openai

# Set your OpenAI API key here
openai.api_key = "your appi"
messages = [{"role": "system", "content": "You are a psychologist"}]

def chatfun(user_input):
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    ChatGPT_reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply

def answer_question(question):
    # Thêm câu hỏi của người dùng vào lịch sử tin nhắn
    messages.append({"role": "user", "content": question})
    # Gọi hàm chatfun để nhận câu trả lời từ GPT-3.5
    response = chatfun(question)
    # Trả về câu trả lời của trợ lý ảo
    return response

def download_pdf_from_link(url):
    try:
        output_path = 'pdf/' + '150' + '.pdf'
        response = requests.get(url, timeout=100, verify=False, allow_redirects=False)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as file:
                file.write(response.content)
            return output_path
        else:
            print(f"Failed to download PDF. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF: {e}")
        return False

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

    return text

def chunk_string(text):
    chunk_size = 350
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def get_pdf(subjects):
    extracter = accumulate(query=subjects, filetype='pdf')
    book_link = extracter.all()

    if book_link != []:
        download_book = download_pdf_from_link(book_link[1])
        if download_book is not False:
            doc_text = extract_text_from_pdf(download_book)
            chunked_text = chunk_string(doc_text)
            return chunked_text
    else: 
        print("Can't find book link")

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            engine.say(text)
            engine.runAndWait()


def get_news(n):
    api_key = '22ca28b2899e4c76bed618fbe80ea2fd'
    base_url = f'https://newsapi.org/v2/top-headlines?country=us&pageSize=20&apiKey={api_key}'
    response = requests.get(base_url)
    news_data = response.json()
    articles = news_data['articles']
    news_headlines = [article['title'] for article in articles[:n]]  # Chỉ lấy 20 tiêu đề đầu tiên
    return news_headlines
  


def send_sms(message, to):
    # Dictionary mapping destination choices to phone numbers
    destination_numbers = {'andy': '84965801476', 'two': '84909625012'}

    # Kiểm tra xem destination có trong dictionary không
    if to in destination_numbers:
        to_number = destination_numbers[to]
        conn = http.client.HTTPSConnection("1vl3xx.api.infobip.com")
        payload = json.dumps({
            "messages": [
                {
                    "destinations": [{"to": to_number}],
                    "from": "ServiceSMS",
                    "text": message
                }
            ]
        })
        headers = {
            'Authorization': 'App 4cb9994e9e1be3a4933e76181a2935a5-562306fa-ae6a-46a8-8fa7-0d1646557cfc',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        conn.request("POST", "/sms/2/text/advanced", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))
    else:
        talk("Invalid destination choice.")

def get_weather(city):
    api_key = 'afefff632f6a14dc7f5a30bbeae5c5a5'
    base_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(base_url)
    weather_data = response.json()
    return weather_data
    
def talk(text):
    engine.say(text)
    engine.runAndWait()

def take_command():
    try:
        with sr.Microphone() as source:
            print('listening.....')
            talk('i am listening...')
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            print(command)
            if 'alexa' in command:
                command = command.replace('alexa', '')
                print(command)
    except:
        pass
    return command 

def run_alexa():
    command = take_command()
    print(command)
    result_label.config(text="You said: " + command)
    if 'play' in command:
        song = command.replace('play', '')
        talk('playing ' + song)
        pywhatkit.playonyt(song)
    elif 'weather' in command:
        city = command.replace('weather in', '').strip()
        weather_data = get_weather(city)
        if weather_data['cod'] == 200:
            temperature = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            wind_speed = weather_data['wind']['speed']
            visibility = weather_data.get('visibility', 'unknown')
            description = weather_data['weather'][0]['description']
            talk(f'The temperature in {city} is {temperature} degrees Celsius with {description}.')
            talk(f'The humidity is {humidity} percent.')
            talk(f'The wind speed is {wind_speed} meters per second.')
            talk(f'The visibility is {visibility} meters.')
        else:
            talk('Sorry, I could not fetch the weather information.')
    elif 'time' in command:
        time = datetime.datetime.now().strftime('%I:%M %p')
        talk('Current time is ' + time)
    elif 'who is' in command:
        person = command.replace('who is', '')
        info = wikipedia.summary(person, 1)
        print(info)
        talk(info)
    elif 'date' in command:
        talk('sorry, I have a headache')
    elif 'are you single' in command:
        talk('I am in a relationship with wifi')
    elif 'joke' in command:
        talk(pyjokes.get_joke())
    elif 'send message' in command:
        talk('Whom do you want to send the message to?')
        to = take_command()  # Lấy tên đích đến từ giọng nói
        print('send to ................')
        talk('What message do you want to send?')
        message = take_command()  # Lấy nội dung tin nhắn từ giọng nói
        send_sms(message, to)
        talk('send successfully')  
    elif 'get news' in command:
    # Tìm số lượng bài báo được yêu cầu
        words = command.split()
        try:
            num_articles_index = words.index('news') + 1
            num_articles = int(words[num_articles_index])
        except (ValueError, IndexError):
        # Nếu không tìm thấy số lượng bài báo hoặc không có số nào được chỉ định, mặc định là 5
            num_articles = 5

        news_headlines = get_news(num_articles)
        for headline in news_headlines:
            talk(headline)
    elif 'answer' in command:
        question = command.replace('answer', '').strip()
        response = answer_question(question)  # Sử dụng hàm answer_question để trả lời câu hỏi
        talk(response)
    elif 'download' in command and 'book' in command:
        book_name = command.replace('download', '').replace('book', '').strip()
        get_pdf(book_name)
        talk(f'Downloading {book_name} now.')
    elif 'read' in command and 'pdf' in command:
        pdf_directory = 'D:\\NLPAproject\\pdf'  # Thay đổi đường dẫn này nếu cần
        pdf_files = [file for file in os.listdir(pdf_directory) if file.endswith('.pdf')]
        if pdf_files:
            file_path = os.path.join(pdf_directory, pdf_files[0])
            pdf_text = read_pdf(file_path)
            engine.say(pdf_text)
            engine.runAndWait()   
        else:
            print("No PDF files found in the directory.")
    elif 'stop and out' in command:
            talk('Goodbye bye bye!')
            sys.exit()  # Exit the while loop and stop the program
    else:
        talk('Please say the command again.')

# Function to recognize speech command
def recognize_speech():
    run_alexa()

# Create the main application window
root = tk.Tk()
root.title("VoiceBot Assistant")

# Customizing the window size and background color
root.geometry("400x200")
root.configure(bg="#f0f0f0")

# Create a frame for organizing widgets with custom padding and background color
frame = tk.Frame(root, padx=20, pady=20, bg="#f0f0f0")
frame.pack(expand=True, fill="both")

# Customizing the font style
font_style = ("Helvetica", 14)

# Create a label to display the microphone icon
mic_label = tk.Label(frame, text="🎤", font=("Segoe UI", 20), bg="#f0f0f0")
mic_label.grid(row=0, column=0, pady=(0, 10))

# Create a label to display the result
result_label = tk.Label(frame, text="", font=font_style, bg="#f0f0f0")
result_label.grid(row=0, column=1, pady=(0, 10), padx=(10, 0))

# Customizing the button appearance
button_color = "#66BB6A"  # Light green color for the button
button_hover_color = "#4CAF50"  # Darker shade of green for button hover effect

# Creating a custom button class for more advanced styling options
class CustomButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        tk.Button.__init__(self, master, **kwargs)
        self.config(
            bg=button_color,
            activebackground=button_hover_color,
            fg="white",
            font=font_style,
            padx=20,
            pady=10,
            bd=0,  # Removing button border
            relief="flat",  # Flat appearance
            highlightthickness=0  # Removing focus highlight
        )

# Create a button to trigger speech recognition using the CustomButton class
recognize_button = CustomButton(frame, text="Speak", command=recognize_speech)
recognize_button.grid(row=1, column=0, columnspan=2, pady=(0, 10))

# Start the Tkinter event loop
root.mainloop()
