from flask import Flask, render_template, request, jsonify
import time
import random
from openai import OpenAI
import logging
import datetime
import re

# Commented out because it doesn't allow me to see the url it's running on
log = logging.getLogger("assistant")

logging.basicConfig(filename = "assistant.log", level = logging.INFO)

from openai import OpenAI

client = OpenAI()

app = Flask(__name__)

# Initialize the Assistant and Thread globally
assistant_id = ""
thread_id = ""

chat_history = [
    {"role": "system", "content": "You are a helpful assistant."},
]

@app.route("/get_ids", methods=["GET"])
def get_ids():
    return jsonify(assistant_id=assistant_id, thread_id=thread_id)


@app.route("/get_messages", methods=["GET"])
def get_messages():
    if thread_id != "":
        # In get_messages function, a little different though
        thread_messages = client.beta.threads.messages.list(thread_id, order="asc")
        messages = [
            {
                "role": msg.role,
                "content": msg.content[0].text.value,
            }
            for msg in thread_messages.data
        ]
        return jsonify(success=True, messages=messages)
    else:
        return jsonify(success=False, message="No thread ID")

# Can create an assistant either here or using an id from the assistant playground on openai by adding the assistant_id
# So I could add the assistant_id for my study buddy here
# And I could refactor this to only use retrieve and the assistant_id from playground
# def create_assistant():
#     global assistant_id
#     if assistant_id == "":
#         my_assistant = client.beta.assistants.create(
#             instructions="You are a helpful assistant. If asked about math or computing problems, write and run code to answer the question.",
#             name="MyQuickstartAssistant",
#             model="gpt-3.5-turbo",
#             tools=[{"type": "code_interpreter"}],
#         )
#         assistant_id = my_assistant.id
#     else:
#         # todo: use your assistant_id here
#         # my_assistant = client.beta.assistants.retrieve(assistant_id)
#         my_assistant = client.beta.assistants.retrieve(assistant_id = "asst_FUTO5sCQkGFaK9UAjLCGaWuq")
#         assistant_id = my_assistant.id

#     # todo: print out the assistant_id to see if it's from the playground
#     print(assistant_id)
#     return my_assistant
  
# todo try refactoring the function, removing the conditional to use my assistant_id
# todo complete: this works, but it relies on me believing. Looking for a way to print out the id so I can check it.
# todo try turning logging back on 
# turning on logging worked the asssitant id printed to the command line and showed in the log
def create_assistant():
    global assistant_id
    my_assistant = client.beta.assistants.retrieve(assistant_id = "asst_FUTO5sCQkGFaK9UAjLCGaWuq")
    assistant_id = my_assistant.id
    print(assistant_id)
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
    content = request.json["message"]
    chat_history.append({"role": "user", "content": content})

    # Send the message to the assistant
    message_params = {"thread_id": thread_id, "role": "user", "content": content}

    # Within the stand alone While Loop that takes in user_input and eventually exits. Different parameters though. And this is greyed out, so is it being used? There's a thread_messages in the get_messages function
    thread_message = client.beta.threads.messages.create(**message_params)

    # Run the assistant
    # This run is within the process_run function
    run = client.beta.threads.runs.create(
        thread_id=thread_id, assistant_id=assistant_id
    )
    # Wait for the run to complete and get the response
    # in a while loop within the process_run function (includes phrases to print out while the run is running)
    while run.status != "completed":
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
    # within get_message function - checks if run is completed
    # this code also has this in an additional place in the get_messages function. 
    # It's written a bit diffferently. Here .data[0] is extracted. In ours, extracting data[0] is part of a longer line
    response = client.beta.threads.messages.list(thread_id).data[0]

    text_content = None

    # Iterate through the content objects to find the first text content
    for content in response.content:
        if content.type == "text":
            text_content = content.text.value
            break  # Exit the loop once the first text content is found

    # Check if text content was found
    if text_content:
        chat_history.append({"role": "assistant", "content": text_content})
        return jsonify(success=True, message=text_content)
    else:
        # Handle the case where no text content is found
        return jsonify(success=False, message="No text content found")

# Broken route? 405? So does the route in the original openai-quickstart-python assistant-flask
@app.route("/reset", methods=["POST"])
def reset_chat():
    global chat_history
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
