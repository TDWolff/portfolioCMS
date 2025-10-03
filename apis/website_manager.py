import csv
import os
from apis.websiteQuery import testWebsite

# Use absolute path based on the current file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(BASE_DIR, 'instances', 'websites.csv')

print(f"CSV_FILE_PATH: {CSV_FILE_PATH}")  # Debug logging

def normalize_url(url):
    """Normalize URL by removing trailing slash for comparison"""
    if url and url.endswith('/'):
        return url.rstrip('/')
    return url

def ensure_csv_exists():
    """Create CSV file and directory if they don't exist"""
    instances_dir = os.path.join(BASE_DIR, 'instances')
    print(f"Ensuring directory exists: {instances_dir}")  # Debug
    
    # Create directory with proper permissions
    os.makedirs(instances_dir, mode=0o755, exist_ok=True)
    
    if not os.path.exists(CSV_FILE_PATH):
        print(f"Creating CSV file: {CSV_FILE_PATH}")  # Debug
        try:
            with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['name', 'url', 'status'])
                writer.writerow(['homepage', 'https://torinwolff.com', 'active'])
            
            # Set file permissions
            os.chmod(CSV_FILE_PATH, 0o666)
            print(f"CSV file created successfully: {CSV_FILE_PATH}")
        except Exception as e:
            print(f"Error creating CSV file: {e}")
            raise
    else:
        print(f"CSV file already exists: {CSV_FILE_PATH}")

def get_all_websites():
    """Get all websites from CSV"""
    ensure_csv_exists()
    websites = []
    
    print(f"Reading from CSV: {CSV_FILE_PATH}")  # Debug
    
    try:
        if not os.path.exists(CSV_FILE_PATH):
            print(f"CSV file does not exist: {CSV_FILE_PATH}")
            return websites
            
        with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Clean up any whitespace and filter out malformed rows
                cleaned_row = {k.strip(): v.strip() if v else v for k, v in row.items() if k}
                if all(cleaned_row.get(key) for key in ['name', 'url', 'status']):
                    websites.append(cleaned_row)
                else:
                    print(f"Skipping malformed row: {row}")
                    
        print(f"Loaded {len(websites)} websites from CSV")  # Debug
    except FileNotFoundError:
        print(f"CSV file not found: {CSV_FILE_PATH}")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        
    return websites

def add_website(name, url):
    """Add a new website to CSV"""
    ensure_csv_exists()
    
    # Clean the inputs
    name = name.strip()
    url = normalize_url(url.strip())
    
    print(f"Adding website: {name} -> {url}")  # Debug
    
    # Test the website first
    is_active = testWebsite(url)
    status = 'active' if is_active else 'inactive'
    
    try:
        # Check if file ends with newline, if not add one
        if os.path.exists(CSV_FILE_PATH):
            with open(CSV_FILE_PATH, 'r', encoding='utf-8') as file:
                content = file.read()
                if content and not content.endswith('\n'):
                    with open(CSV_FILE_PATH, 'a', encoding='utf-8') as append_file:
                        append_file.write('\n')
        
        # Append new website
        with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([name, url, status])
            
        print(f"Successfully added website: {name}")  # Debug
        
        # Verify the write by reading it back
        websites = get_all_websites()
        added_website = next((w for w in websites if w['name'] == name and w['url'] == url), None)
        if added_website:
            print(f"Verified: Website {name} was added successfully")
            return added_website
        else:
            print(f"Warning: Website {name} was not found after adding")
            return {'name': name, 'url': url, 'status': status}
            
    except Exception as e:
        print(f"Error adding website: {e}")
        raise

def update_website_status(name, url):
    """Update website status by testing the URL"""
    ensure_csv_exists()
    websites = get_all_websites()
    updated = False
    
    # Normalize the input URL for comparison
    normalized_url = normalize_url(url)
    
    print(f"Looking for website: name='{name}', url='{url}', normalized='{normalized_url}'")  # Debug
    print(f"Available websites: {websites}")  # Debug
    
    for website in websites:
        # Compare with normalized URLs
        if website['name'] == name and normalize_url(website['url']) == normalized_url:
            print(f"Found matching website: {website}")  # Debug
            is_active = testWebsite(url)  # Use original URL for testing
            print(f"Test result for {url}: {is_active}")  # Debug
            old_status = website['status']
            website['status'] = 'active' if is_active else 'inactive'
            print(f"Status changed from '{old_status}' to '{website['status']}'")  # Debug
            updated = True
            break
    
    if updated:
        # Rewrite the entire CSV file with proper formatting
        with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'url', 'status'])
            writer.writeheader()
            writer.writerows(websites)
    else:
        print(f"No matching website found for name='{name}', url='{normalized_url}'")  # Debug
    
    return websites

def delete_website(name, url):
    """Delete a website from CSV"""
    ensure_csv_exists()
    websites = get_all_websites()
    normalized_url = normalize_url(url)
    websites = [w for w in websites if not (w['name'] == name and normalize_url(w['url']) == normalized_url)]
    
    # Rewrite the CSV file with proper formatting
    with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'url', 'status'])
        writer.writeheader()
        writer.writerows(websites)
    
    return websites

def edit_website(old_name, old_url, new_name, new_url):
    """Edit a website in CSV"""
    ensure_csv_exists()
    websites = get_all_websites()
    
    # Normalize URLs for comparison
    normalized_old_url = normalize_url(old_url)
    normalized_new_url = normalize_url(new_url.strip())
    
    for website in websites:
        if website['name'] == old_name and normalize_url(website['url']) == normalized_old_url:
            website['name'] = new_name.strip()
            website['url'] = normalized_new_url
            # Test the new URL
            is_active = testWebsite(normalized_new_url)
            website['status'] = 'active' if is_active else 'inactive'
            break
    
    # Rewrite the CSV file with proper formatting
    with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'url', 'status'])
        writer.writeheader()
        writer.writerows(websites)
    
    return websites

def repair_csv_file():
    """Repair malformed CSV file"""
    if not os.path.exists(CSV_FILE_PATH):
        return
    
    try:
        # Read the current file content
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Split by common separators and try to reconstruct
        lines = content.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        
        # Try to extract valid data
        valid_websites = []
        for line in lines:
            if line.strip() and 'name,url,status' not in line:
                parts = line.split(',')
                if len(parts) >= 3:
                    # Take the first part as name, last as status, middle parts as URL
                    name = parts[0].strip()
                    status = parts[-1].strip()
                    url = normalize_url(','.join(parts[1:-1]).strip())
                    
                    if name and url and status:
                        valid_websites.append({'name': name, 'url': url, 'status': status})
        
        # Rewrite the file properly
        with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'url', 'status'])
            writer.writeheader()
            writer.writerows(valid_websites)
        
        print(f"Repaired CSV file with {len(valid_websites)} websites")
        
    except Exception as e:
        print(f"Error repairing CSV: {e}")
        # If repair fails, recreate with default data
        ensure_csv_exists()