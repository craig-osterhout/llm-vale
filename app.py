import os
import subprocess
import json
import google.generativeai as genai

# Set the API key for the generative AI model from the environment variable
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    api_key = input('Enter your Gemini API Key:')
genai.configure(api_key=api_key)
# Create a generative model
model = genai.GenerativeModel('gemini-pro')

# Specify the base directory where the search starts
base_directory = "/docs/content/guides/"

def find_and_vale(base_directory):
    # Change the working directory to '/docs'. This should be where .vale.ini is located
    os.chdir('/docs')

    # Initialize combined_output as an empty dictionary
    combined_output = {}

    # Run the 'find' command and get the output
    find_output = subprocess.run(['find', base_directory, '-name', '*.md'], stdout=subprocess.PIPE).stdout.decode().splitlines()

    # Iterate over each line in the output
    for line in find_output:
        # Run 'vale' on each line
        output = subprocess.run(['vale', '--output', 'JSON', line], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Load the JSON from the stdout
        output_dict = json.loads(output.stdout)

        # Merge the current file's output into the combined_output dictionary
        combined_output = {**combined_output, **output_dict}

    # Return the combined output
    return combined_output

def ask_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text


def process_acronym_issue(issue, file_content, line_content):
    question = "You are a style fixing tool for technical writers. The provided Text-of-line-with-issue uses an acronym that is not defined. Can you fix the line and provide a definition for the acronym? For example, if the line is, 'You can use LLMs for your project', and the context of the file is about AI, you can provide 'You can use large language models (LLMs) for your project.' as your answer. Only provided the corrected line. Do not provide any other information in your response. I will use your response to automate fixing the issue, so it must be only that. You can refer to the File-content to understand the context of the file."
    prompt = f"File-content: {file_content}. Issue-identified-by-vale: {issue}. Text-of-line-with-issue: {line_content}. Your-instructions: {question}"
    answer = ask_gemini(prompt)
    return answer


def process_adverb_issue(issue, file_content, line_content):
    question = "You are a style fixing tool for technical writers. The provided Text-of-line-with-issue uses an adverb that is may not be necessary. Can you fix the line and provide the line without the adverb? If the adverb is necessary, then provide the line as is. By necessary, I mean removing the adverb would change the meaning or make the sentence read awkward. For example, if the line is 'This simple example is about Docker', you can provide 'This example is about Docker' Or if the line is, `Docker adds new features regularly', then you can provide 'Docker may add new features'. Only provided the corrected line or the line as-is. Always provide the whole line. Do not provide any other information in your response. Do not add additional punctuation. I will use your response to automate fixing the issue, so it must be only that. You can refer to the File-content to understand the context of the file."
    prompt = f"File-content: {file_content}. Issue-identified-by-vale: {issue}. Text-of-line-with-issue: {line_content}. Your-instructions: {question}"
    answer = ask_gemini(prompt)
    return answer

def process_avoid_issue(issue, file_content, line_content):
    question = "You are a style fixing tool for technical writers. The provided Text-of-line-with-issue uses a word that should be avoided. Can you fix the line and provide the line without the word and any associated punctuation? If you remove the first word in the sentence, capitalize the first letter in the next word. Always provide the whole line. Do not provide any other information in your response. I will use your response to automate fixing the issue, so it must be only that. You can refer to the File-content to understand the context of the file"
    prompt = f"File-content: {file_content}. Issue-identified-by-vale: {issue}. Text-of-line-with-issue: {line_content}. Your-instructions: {question}"
    answer = ask_gemini(prompt)
    return answer


if __name__ == "__main__":
    combined_output = find_and_vale(base_directory)
    # Iterate through the combined_output dictionary
    for filename, issues in combined_output.items():
        # Open the file and read the content
        with open(filename, 'r') as file:
            file_content = file.read()
            lines = file_content.splitlines()
        # Iterate through the issues
        for issue in issues:
            answer = ""
            line_num = issue['Line'] -  1  # Subtract  1 because line numbers
            line_content = lines[line_num].strip()  # Extract the line content
            match issue['Check']:
                case "Docker.Acronyms":
                    answer = process_acronym_issue(issue, file_content, line_content)
                case "Docker.Adverbs":
                    continue # It does horrible with this one
                    #answer = process_adverb_issue(issue, file_content, line_content)
                case "Docker.Avoid":
                    answer = process_avoid_issue(issue, file_content, line_content)
                    # not tested
            if answer:
                    print(issue['Message'])
                    print(line_content)
                    print(answer)
                    print("----------------------------------------------")
