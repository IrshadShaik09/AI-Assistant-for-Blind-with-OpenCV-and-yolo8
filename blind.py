from tkinter import *
from tkinter import messagebox
from ultralytics import YOLO
from ultralytics.yolo.v8.detect.predict import DetectionPredictor
import pyttsx3
import cv2
import openai
import speech_recognition as sr
from collections import defaultdict

root = Tk()
root.title("AI Assistant for Visually Impaired")
openai.api_key = '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'
engine = pyttsx3.init()

def convert_speech_to_text():
    # Create a recognizer object
    recognizer = sr.Recognizer()

    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        print("Speak something...")
        audio = recognizer.listen(source)

    try:
        # Use Google Speech Recognition to convert audio to text
        text = recognizer.recognize_google(audio)
        return text

    except sr.UnknownValueError:
        print("Sorry, I could not understand your speech.")
        return ""

    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""
    
def chat_with_gpt(prompt):
    # Define the parameters for the API call
    parameters = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role': 'user', 'content': prompt}]
    }

    # Call the OpenAI API
    response = openai.ChatCompletion.create(**parameters)

    # Extract the model's reply from the API response
    reply = response.choices[0].message.content

    return reply

def count_items(input_list):
    result = defaultdict(int)
    for item in input_list:
        result[item] += 1
    return dict(result)

def open_camera():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        cv2.imshow("Camera", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('c'):
            cv2.imwrite("frame.png", frame)
            messagebox.showinfo("Camera", "Image captured successfully!")
            break
    
    cap.release()
    cv2.destroyAllWindows()

def analyze_objects():
    list1=[]
    model = YOLO("yolov8s.pt")
    results=model.predict(source="frame.png",show=True,save_txt=True) 

    for result in results:
        cls = result.boxes.cls
        for c in cls:
            list1.append(result.names[int(c)])

    list2 = count_items(list1)
    print(list2)

    for objectname in list2:
        engine.say(objectname)

    user_prompt = "Given list of objects, guess the place or describe the environment. " + str(list2)
    response = chat_with_gpt(user_prompt)
    print("ChatGPT:", response)
    engine.say(response)
    engine.runAndWait()
    output_label.config(text=response)

    user_prompt = "Please describe the following objects (with quantity) and provide a brief description for each: " + str(list2)
    response = chat_with_gpt(user_prompt)
    print("ChatGPT:", response)
    output_label.config(text=response)

    while True:
        user_input = input("User: ")   +". Given list of objects are: "+str(list2)         #convert_speech_to_text()
        if user_input == "exit":
            break
        user_prompt = user_input
        try:
            response = chat_with_gpt(user_prompt)
            print("ChatGPT:", response)
            engine.say(response)
            engine.runAndWait()
            output_label.config(text=response)
        except:
            print("ChatGPT: limit reached.")
            output_label.config(text="ChatGPT: limit reached.")
            engine.say("limit reached")
            engine.runAndWait()
#Create Tkinter GUI
root.geometry("400x300")

#Create buttons
camera_btn = Button(root, text="Open Camera", command=open_camera)
camera_btn.pack(pady=10)

analyze_btn = Button(root, text="Analyze Objects", command=analyze_objects)
analyze_btn.pack(pady=10)

output_label = Label(root, text="")
output_label.pack(pady=10)

#Start Tkinter main loop
root.mainloop()