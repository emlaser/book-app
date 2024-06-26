from flask import Flask, render_template, request, jsonify
import time
import random
from openai import OpenAI
import logging
import datetime
import re

# http://127.0.0.1:5000/
# todo rethink - I've learned how this works. Define the routes and run in the command line first. Then connect with the index.html. There are two routes one that POSTS the chat_history and the other (2) that GETS the threads and the chat_history. 
# todo move the js to its own folder.
# todo print out all the values so I'm sure what data they hold. 
# todo Check my mapping to the JS to make sure what's sent over when. 
# todo can the assistant still be personalized with a UI? Can it still ask a name, etc.?
# todo clear out this code and start fresh walking through the lessons as they are. Establish a boilerplate w/flask. Maybe clear out js also. Def move later to another file. The lesson will be about understanding GET and POST in this context. The way this app works is that we GET the ... and then interact with the user and POST what they add, then we GET the thread (takes time), and then when the user asks another question... we POST to the API again. This continues until the user is done and they close the window. A nice would be that the chat is saved so they can view it later. 

# Can comment out because it doesn't allow me to see the url it's running on
log = logging.getLogger("assistant")

logging.basicConfig(filename = "assistant.log", level = logging.INFO)

from openai import OpenAI

client = OpenAI()

app = Flask(__name__)

# Initialize the Assistant and Thread globally
assistant_id = ""
thread_id = ""

chat_history = [
    # todo Change this to prompt for user name, etc.
    {"role": "system", "content": "You are a helpful assistant."},
]

@app.route("/get_ids", methods=["GET"])
def get_ids():
    return jsonify(assistant_id=assistant_id, thread_id=thread_id)


@app.route("/get_messages", methods=["GET"])
def get_messages():
    if thread_id != "":
        # In get_messages function, a little different though
        # order="asc" sorts the messages in ascending order https://platform.openai.com/docs/api-reference/assistants/listAssistants#assistants-listassistants-order
        thread_messages = client.beta.threads.messages.list(thread_id, order="asc")
        messages = [
            {
                # Todo where does msg come from? This code breaks up the thread_messages where data is extracted elsewhere
                "role": msg.role,
                "content": msg.content[0].text.value,
            }
            for msg in thread_messages.data
        ]
        return jsonify(success=True, messages=messages)
    else:
        return jsonify(success=False, message="No thread ID")
  
# todo - COMPLETED - try refactoring the function, removing the conditional to use my assistant_id
# turning on logging worked the asssitant id printed to the command line and showed in the log
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
        # What is the capital of France?
        # Why are fat women so ugly?
        
    chat_history.append({"role": "user", "content": user_input})

    # Send the message to the assistant
    message_params = {"thread_id": thread_id, "role": "user", "content": user_input}
    
    # Within the stand alone While Loop that takes in user_input and eventually exits. Different parameters though. And this is greyed out, so is it being used? There's a thread_messages in the get_messages function
    thread_message = client.beta.threads.messages.create(**message_params)

    # Run the assistant
    # This run is within the process_run function. They way this code is written may be just fine for a UI. May not need while true since there's nothing to become false - didn't run.
    run = client.beta.threads.runs.create(
        thread_id=thread_id, assistant_id=assistant_id
    )
    # Wait for the run to complete and get the response
    # in a while loop within the process_run function (includes phrases to print out while the run is running)
    # todo replace with 23-33 from assistant.py
    while run.status != "completed":
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
    
    # within get_message function - checks if run is completed
    # this code also has this in an additional place in the get_messages function. 
    # It's written a bit diffferently. Here .data[0] is extracted. In ours, extracting data[0] is part of a longer line
    response = client.beta.threads.messages.list(thread_id).data[0]

    # very curious about this code. Is it to evaluate if the response is only text and so return only text?
    text_content = None

    # Iterate through the content objects to find the first text content
    for content in response.content:
        if content.type == "text":
            text_content = content.text.value
            break  # Exit the loop once the first text content is found

    # Check if text content was found
    if text_content:
        # this is the wrong place for moderation. No need to moderate the content from the assistant
        chat_history.append({"role": "assistant", "content": text_content})
        return jsonify(success=True, message=text_content)
    else:
        # Handle the case where no text content is found
        return jsonify(success=False, message="No text content found")

# Broken route? 405? So does the route in the original openai-quickstart-python assistant-flask
@app.route("/reset", methods=["POST"])
def reset_chat():
    global chat_history
    # todo change this also to the message we want to see
    chat_history = [{"role": "system", "content": "You are a helpful assistant."}]

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
