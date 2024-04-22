from flask import Flask, render_template, request, jsonify
import time
from openai import OpenAI
import logging
import datetime
import re

# http://127.0.0.1:5000/
# todo Make this code more like the Skillcrush lesson...
log = logging.getLogger("assistant")

logging.basicConfig(filename = "assistant.log", level = logging.INFO)

# todo add the rest of logging... but where? :) 

from openai import OpenAI

client = OpenAI()

app = Flask(__name__)

# Initialize the Assistant and Thread globally
assistant_id = ""
thread_id = ""

# chat_history = [{"role": "system", "content": "You are a helpful assistant."}]

chat_history = [
    # todo Change this to prompt for user name, etc.
    # When I do, the Assistant just reprints my name. Exit does work though. If I ask it to call me by my name it will. What about adding it instead of "user"? If the user writes "My name is ..." It responsds "Hello Lisa! How can I assist you today?"
    {"role": "system", "content": "Hey there! How can i assist you with your learning today?"},
]

@app.route("/get_ids", methods=["GET"])
def get_ids():
    return jsonify(assistant_id=assistant_id, thread_id=thread_id)


@app.route("/get_messages", methods=["GET"])
def get_messages():
    if thread_id != "":
        thread_messages = client.beta.threads.messages.list(thread_id, order="asc")
        messages = [
            {
                "role": msg.role,
                "content": msg.content[0].text.value,
            }
            for msg in thread_messages.data
        ]
        # todo throwing and indexerror - log out thread_messages.data. Should this be in a POST request instead?
        # if thread_messages.data[0].content[0].text.annotations:
        #     pattern = r'【\d+†source】'
        #     message = re.sub(pattern, '', message)
        
        return jsonify(success=True, messages=messages)
    else:
        return jsonify(success=False, message="No thread ID")
  
# todo - COMPLETED - try refactoring the function, removing the conditional to use my assistant_id
def create_assistant():
    global assistant_id
    my_assistant = client.beta.assistants.retrieve(assistant_id = "asst_FUTO5sCQkGFaK9UAjLCGaWuq")
    assistant_id = my_assistant.id
    # print(assistant_id)
    return my_assistant


def create_thread():
    global thread_id
    if thread_id == "":
        thread = client.beta.threads.create()
        thread_id = thread.id
    else:
        thread = client.beta.threads.retrieve(thread_id)
        thread_id = thread.id

    return thread

def log_run(run_status):
    if run_status in ["cancelled", "failed", "expired"]:
        log.error(str(datetime.datetime.now()) + " Run " + run_status + "\n")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", chat_history=chat_history)

# Broken route? 405? So does the route in the original openai-quickstart-python assistant-flask
@app.route("/chat", methods=["POST"])
def chat():
    # todo - COMPLETED - added moderation to chat 
    user_input = request.json["message"]

    moderation_result = client.moderations.create(
        input = user_input
    )
    while moderation_result.results[0].flagged == True:
        moderation_result = client.moderations.create(
            input = user_input
        )

        chat_history.append({"role": "assistant", "content": user_input})
        return jsonify(success=True, message="Assistant: Sorry, your message violated our community guidelines. Please try another prompt.")
        
    chat_history.append({"role": "user", "content": user_input})

    # Send the message to the assistant
    message_params = {"thread_id": thread_id, "role": "user", "content": user_input}
    
    thread_message = client.beta.threads.messages.create(**message_params)

    run = client.beta.threads.runs.create(
        thread_id = thread_id, 
        assistant_id = assistant_id
    )

    while run.status != "completed":
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id = thread_id, run_id = run.id)
    
    # todo map this to line 41 of chatbot-v3. Can this be trimmed down to .list, .value, and then return jsonify?
    response = client.beta.threads.messages.list(thread_id).data[0]

    text_content = None

    # Iterate through the content objects to find the first text content
    for content in response.content:
        if content.type == "text":
            text_content = content.text.value
            break  # Exit the loop once the first text content is found
          
    log_run(run.status)
    
    # Check if text content was found
    if text_content:
        chat_history.append({"role": "assistant", "content": text_content})
        return jsonify(success=True, message=text_content)
    else:
        # Handle the case where no text content is found
        return jsonify(success=False, message="No text content found")
      
    

@app.route("/reset", methods=["POST"])
def reset_chat():
    global chat_history
    # chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
    # todo change this also to the message we want to see
    chat_history = [{"role": "system", "content": "Hey there! How can i assist you with your learning today?"}]

    global thread_id
    thread_id = ""
    create_thread()
    return jsonify(success=True)


# Create the assistants and thread when we first load the flask server
@app.before_request
def initialize():
    app.before_request_funcs[None].remove(initialize)
    create_assistant()
    create_thread()
    



if __name__ == "__main__":
    app.run()
