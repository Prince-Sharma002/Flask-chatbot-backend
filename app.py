import json
from difflib import get_close_matches
import pyautogui
from datetime import datetime
from generateFacts import extract_facts_with_titles, save_facts_to_json


def calculate_time():
    # Get the current date and time
    current_datetime = datetime.now()

    # Extract the current time
    current_time = current_datetime.time()

    # Format the current time as a string
    formatted_time = current_time.strftime("%H:%M:%S")

    return ("Current Time is " , formatted_time)


def load_chat_data( file_path : str ):
    with open( file_path, 'r' ) as file:
        data : dict = json.load(file)
    return data

def save_chat_data( file_path : str , data : json):
    with open( file_path , 'w' ) as file:
        json.dump( data , file , indent=2 )


def find_best_match( user_question : str , questions : list[str] ):
    matches : list  = get_close_matches(user_question , questions , n= 1 )
    if( matches ):
        return matches[0]
    return None

def get_answer_for_question( question : str , knowledge_base : dict):
    for q in knowledge_base['questions']:
        if  q['question'] == question:
            return q['answer']
        
def chatbot(user_input: str):
    knowledge_base: dict = load_chat_data(r"C:\Users\RAJ ENTERPRISES\Downloads\chatbot\flask-server\extracted_facts.json")
    
    best_matches: str = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])
    if best_matches: 
        answer: str = get_answer_for_question(best_matches, knowledge_base)
        print(f'{answer}')
        return f'{answer}' 
    elif user_input.lower() == "skip":
        print(f'{"alright sir"}')
        return f'{"alright sir"}'
    elif "time" in user_input.lower():
        return calculate_time()
    elif "switch" in user_input.lower(): 
        pyautogui.hotkey('alt', 'tab') 
        return "switching tab"
    elif "close tab" in user_input.lower():
        pyautogui.hotkey('ctrl', 'w')
        return "closing tab"
    elif 'ans is' in user_input.lower():
        user_data = user_input.split("-")
        get_question = user_data[1].strip()
        get_answer = user_data[2].strip()
        knowledge_base['questions'].append({"question": get_question, "answer": get_answer})
        save_chat_data(r"C:\Users\RAJ ENTERPRISES\Downloads\chatbot\flask-server\extracted_facts.json", knowledge_base)
        print("Bot: Thank you! I learned a new response")
        return "Thank you! I learned a new response"
    else:
        return "ok give me answer"

# while True:
#     user_input : str = input("User: ")
#     if( user_input.lower() == "quit" ):
#         break
#     chatbot(user_input)


from flask import Flask, request, jsonify
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)


@app.route('/chat', methods=['POST'])
def handle_chat():
    data = request.json
    user_input = data['input']
    response = chatbot(user_input)  # Call your chatbot function
    return jsonify({'response': response})


@app.route('/generate-facts', methods=['POST'])
def generate_facts():
    data = request.json
    input_text = data.get('text', '')

    if not input_text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        extracted_facts = extract_facts_with_titles(input_text)
        save_facts_to_json(extracted_facts)
        return jsonify({'facts': extracted_facts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


