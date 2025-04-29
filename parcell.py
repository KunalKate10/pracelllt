import hashlib
import json
import streamlit as st
import requests
from datetime import datetime

class Block:
    def __init__(self, timestamp, data, previous_hash):
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha256()
        sha.update(str(self.timestamp).encode('utf-8') + 
                   str(self.data).encode('utf-8') + 
                   str(self.previous_hash).encode('utf-8'))
        return sha.hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.load_chain()

    def create_genesis_block(self):
        return Block("01/01/2023", "Genesis Block", "0")

    def load_chain(self):
        try:
            with open('blockchain_data.json', 'r') as f:
                data = json.load(f)
                self.chain = [Block(b['Timestamp'], b['Data'], b['Previous Hash']) for b in data]
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # If file doesn't exist, it means we use the genesis block

    def save_chain(self):
        with open('blockchain_data.json', 'w') as f:
            data = [{
                'Timestamp': block.timestamp,
                'Data': block.data,
                'Hash': block.hash,
                'Previous Hash': block.previous_hash
            } for block in self.chain]
            json.dump(data, f, indent=4)
        self.push_to_github()

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(str(datetime.now()), data, previous_block.hash)
        self.chain.append(new_block)
        self.save_chain()

    def push_to_github(self):
        # GitHub repository settings
        repo_owner = "your_github_username"
        repo_name = "your_repo_name"
        file_path = "blockchain_data.json"
        github_token = "your_github_token"
        commit_message = "Update blockchain data"

        with open(file_path, 'r') as file:
            content = file.read()

        # GitHub API URL for updating a file
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"

        # Get the current file's SHA
        response = requests.get(url, headers={'Authorization': f'token {github_token}'})
        sha = response.json().get('sha')

        if sha:
            # Update the file
            data = {
                "message": commit_message,
                "content": content.encode("utf-8").decode("utf-8"),  # Base64 encoded content
                "sha": sha
            }
            response = requests.put(url, json=data, headers={'Authorization': f'token {github_token}'})
        else:
            # Create the file if it doesn't exist
            data = {
                "message": commit_message,
                "content": content.encode("utf-8").decode("utf-8")  # Base64 encoded content
            }
            response = requests.put(url, json=data, headers={'Authorization': f'token {github_token}'})
        
        if response.status_code == 201 or response.status_code == 200:
            st.success("Blockchain data pushed to GitHub successfully!")
        else:
            st.error("Failed to push to GitHub")

# Create a blockchain instance
blockchain = Blockchain()

# Streamlit Interface
st.title("Blockchain Parcel Tracking System")

# Display current blockchain
st.subheader("Current Blockchain")
for block in blockchain.chain:
    st.write(f"Timestamp: {block.timestamp}")
    st.write(f"Data: {block.data}")
    st.write(f"Hash: {block.hash}")
    st.write(f"Previous Hash: {block.previous_hash}")
    st.write("\n")

# Add parcel tracking information
new_data = st.text_input("Add Parcel Tracking Info:")

if st.button("Add Block"):
    if new_data:
        blockchain.add_block(new_data)
        st.success(f"Block with data '{new_data}' added successfully.")
    else:
        st.warning("Please enter parcel tracking data.")
