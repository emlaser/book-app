# Setting up to run scripts using the openai API with Python.

The script will be run in a virtual environment. Start by creating a virtual environment:

On a Mac:
`python3 -m venv openai-env`

On Windows:
`python -m venv openai-env`

<br>
After creating the virtual environment, you need to activate it:

On a Mac:
`source openai-env/bin/activate`

On Windows:
`openai-env\Scripts\activate`

<br>
Once the virtual environment is activated, the beginning of your terminal prompt should display (openai-env).

<br>
Install the OpenAI API library by running (in both a Mac and Windows):

`pip install --upgrade openai` 

You'll see an openai-env folder has been added to the directory with all of the installed dependencies.

<br>
To run your code, in the command line run (change the file name if necessary):

On a Mac:
`python3 assistant.py`

On Windows:
`python assistant.py`

<br>
When finished, close the virtual environment by running: 

`deactivate`



