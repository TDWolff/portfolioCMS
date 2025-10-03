import subprocess
import os
import csv
from dotenv import load_dotenv

load_dotenv()

startPath = os.getenv('START_PATH')
stopPath = os.getenv('STOP_PATH')
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'instances', 'websites.csv')

if not os.path.exists(CSV_FILE_PATH):
    print("Websites CSV file does not exist.")

def getNamesFromCSV():
    names = []
    try:
        with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                names.append(row['name'])
    except Exception as e:
        print(f"Error reading CSV for names: {e}")
    return names
        
def checkIDInCSVNames(input_name):
    try:
        with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['name'].lower() == input_name.lower():
                    return True, row['name']
    except Exception as e:
        print(f"Error checking ID in CSV names: {e}")
    return False, None

def start(id):
    try:
        if not id:
            return {"success": False, "error": "No ID provided"}
        exists, valid_name = checkIDInCSVNames(id)
        if not exists:
            return {"success": False, "error": f"ID '{id}' not found in CSV"}
        #change first line in start.sh to use the valid_name
        with open(startPath, 'r') as file:
            lines = file.readlines()
        if lines:
            lines[0] = f"cd {valid_name}\n"  # Adjust this line as needed
            with open(startPath, 'w') as file:
                file.writelines(lines)
        # start the server using the startPath script
        result = subprocess.run(['bash', startPath], check=True, capture_output=True, text=True)
        return {"success": True, "message": "Server started successfully", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": f"Failed to start server: {e.stderr}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
def stop(id):
    try:
        if not id:
            return {"success": False, "error": "No ID provided"}
        exists, valid_name = checkIDInCSVNames(id)
        if not exists:
            return {"success": False, "error": f"ID '{id}' not found in CSV"}
        
        # stop the server using the stopPath script
        result = subprocess.run(['bash', stopPath], check=True, capture_output=True, text=True)
        return {"success": True, "message": "Server stopped successfully", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": f"Failed to stop server: {e.stderr}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}