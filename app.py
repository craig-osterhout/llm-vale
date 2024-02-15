# Import the os module to change the working directory and access environment variables
import os

# Import the subprocess module to run 'vale' as a subprocess
import subprocess

# Import the JSON module to parse the JSON output from 'vale'
import json

# Import the generative AI module from the Google package
import google.generativeai as genai

# Set the API key for the generative AI model from the environment variable
api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)
# Create a generative model
model = genai.GenerativeModel('gemini-pro')

# Change the working directory to '/docs'. This should be where .vale.ini is located
os.chdir('/docs')

# Create an empty dictionary to store the combined output of all the vale runs
combined_output = {}

# Specify the base directory where the search starts
base_directory = '/docs/content/guides/use-case/'

# Find all markdown files and execute 'vale' on each
for line in subprocess.run(['find', base_directory, '-name', '*.md'], stdout=subprocess.PIPE).stdout.decode().splitlines():
    print(line)
    # Execute 'vale'
    output = subprocess.run(['vale', '--output', 'JSON', line], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    # Access the stdout of the completed process
    output_json = output.stdout
    # Load the JSON from the stdout
    output_dict = json.loads(output_json)

    # Merge the current file's output into the combined_output dictionary
    combined_output = {**combined_output, **output_dict}

# Define a function to ask Gemini for a suggestion
def ask_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text

# Iterate through the combined_output dictionary
for filename, issues in combined_output.items():

    # Open the file and read the content
    with open(filename, 'r') as file:
        file_content = file.read()
        lines = file_content.splitlines()
    # Iterate through the issues
    for issue in issues:
        line_num = issue['Line'] -  1  # Subtract  1 because line numbers start at  1, not  0
        line_content = lines[line_num].strip()  # Extract the line content
        question = "You are an expert technical writer and are reviewing documentation. Vale identified an issue in the markdown file. Can you suggest a fix for the issue that vale identified? If the message says `has no definition`, that means vale thinks it's a spelling error. Do not suggest to fix it by adding it to the dictionary. In this case, it is up to you to check if it's a spelling error based on the context of the file content. Do not suggest creating a definition and do not look for a definition in the content, and instead use your knowledge of the content to determine if it's a spelling error. If the issue is passive voice, provide the reworded line with no passive voice. If no update is needed, please print 'NO UPDATE NEEDED' first and then always justify why pre-fixed with 'JUSTIFICATION:'. If you are not sure, please print 'HUMAN INPUT REQUESTED'. If a change is needed, please provided the entire line with the change. Only provide the updated text if there is a change. Do not provide any additional reasoning or context."

        prompt = f"File content: {file_content}. Issue identified by vale: {issue}. Text of line with issue: {line_content}. {question}"
        answer = ask_gemini(prompt)

        # If the response contains 'HUMAN INPUT', keep asking for a response
        # Was just testing to see if it would work. But it requests human input for stuff that it should be able to handle.
        while 'HUMAN INPUT' in answer:
            answer = ask_gemini(prompt)

        print("\n-----------------------------------")
        print ("**VALE OUTPUT**")
        print(issue)
        print ("\n")
        print("**LINE**\n" + line_content + "\n")
        print("**LLM OUTPUT**\n" + answer)
