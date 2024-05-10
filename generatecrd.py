import os
import argparse
import git
from github import Github
import re
import subprocess

# Create an argument parser
parser = argparse.ArgumentParser(description='Search for text in a GitHub repository.')
parser.add_argument('--repo', help='GitHub repository address')
parser.add_argument('--token', help='GitHub personal access token')

# Parse the command line arguments
args = parser.parse_args()

# Check if both repository address and token are provided
if not (args.repo and args.token):
    parser.error('Both --repo and --token are required.')

# Extract repository address and token
repo_address = args.repo
access_token = args.token

# Create a Github instance with provided token
g = Github(access_token)

def clone_repo(repo_url, destination_folder):
    try:
        git.Repo.clone_from(repo_url, destination_folder)
        print("Repository cloned successfully!")
    except git.exc.GitCommandError as e:
        print("Error:", e)

def search_text_in_repo(repo_url, text):
    result = ''
    try:
        # Extract owner and repository name from the URL
        match = re.match(r"https://github.com/([^/]+)/([^/]+)", repo_url)
        if match:
            owner = match.group(1)
            repo_name = match.group(2)

            # Get the repository
            repo = g.get_repo(f"{owner}/{repo_name}")

            # Print the header
            print(f"Results for exact match '{text}' in repository '{owner}/{repo_name}':")

            # Recursively search through each directory
            result = search_directory(repo, text, "", found_match=False)

        else:
            print("Invalid GitHub repository URL")

    except Exception as e:
        print("An error occurred:", str(e))
    return result

def search_directory(repo, text, directory, found_match):
    # Get the contents of the directory
    contents = repo.get_contents(directory)
    version = ''
    for content_file in contents:
        if content_file.type == "dir":
            # If it's a directory, recursively search it
            found_match, version = search_directory(repo, text, content_file.path, found_match)
            if found_match:
                # Break if a match is found
                break
        else:
            # If it's a file, check for the text
            file_content = content_file.decoded_content.decode()
            lines = file_content.split('\n')
            for line_number, line in enumerate(lines, start=1):
                if text in line:
                    print(f"File: {content_file.path}, Line: {line_number}")
                    version = line.replace(text, '')
                    found_match = True
                    # Break if a match is found
                    break
            if found_match:
                # Break if a match is found
                break

    return found_match, version

# Example usage
text_to_search = 'apiVersion: apiextensions.k8s.io/'
destination_folder = 'generate_git'
try:
    os.system(f'rm -rf {destination_folder}')
except Exception as e:
    print('')
version = search_text_in_repo(repo_address, text_to_search)
if (version != ''):
    repo_upload = repo_address + '.git'
    clone_repo(repo_upload, destination_folder)
    try:
        os.chdir(destination_folder)
        print(f"Changed directory to: {destination_folder}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    print('version:'+ version[1])
    # Define the command
    command = "controller-gen paths=./... crd:crdVersions="+version[1]+" output:crd:dir=../"
    # Execute the command
    try:
        subprocess.run(command, shell=True, check=True)
        print("Command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
    try:
        os.chdir('../')
        print(f"Changed directory to: {'../'}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    try:
        os.system(f'rm -rf {destination_folder}')
    except Exception as e:
        print('')
