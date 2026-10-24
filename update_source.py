import json
import requests
import datetime

# Fetch the latest release details from the official repository API endpoint
api_url = "https://github.com"
response = requests.get(api_url)

if response.status_code == 200:
    release_data = response.json()
    tag_name = release_data["tag_name"] # Example: "v6.6.3"
    
    # Clean the version tag name to pull out just the primary numbers
    clean_version = tag_name.replace("v", "") 
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Initialize download paths
    patched_url = ""
    unpatched_url = ""
    
    # Search through the distribution files for matching file patterns
    for asset in release_data.get("assets", []):
        asset_name = asset["name"].lower()
        if "patched" in asset_name and asset_name.endswith(".ipa"):
            patched_url = asset["browser_download_url"]
        elif "patched" not in asset_name and asset_name.endswith(".ipa"):
            unpatched_url = asset["browser_download_url"]

    # Open and process the existing local app source map database document
    try:
        with open("apps.json", "r") as f:
            repo_json = json.load(f)
    except FileNotFoundError:
        print("Error: apps.json file was not found in the root directory folder.")
        exit(1)

    updated = False
    
    # Loop over the app variants listed inside the database file tracking block
    for app in repo_json.get("apps", []):
        # Variant 1: Check for the targeted jailbreak / paid variant
        if "patched" in app.get("localizedDescription", "").lower():
            if app["version"] != clean_version and patched_url:
                app["version"] = clean_version
                app["versionDate"] = current_date
                app["downloadURL"] = patched_url
                app["versionDescription"] = f"Automatically updated to release {tag_name}"
                updated = True
        # Variant 2: Check for the default sideloading distribution package
        else:
            if app["version"] != clean_version and unpatched_url:
                app["version"] = clean_version
                app["versionDate"] = current_date
                app["downloadURL"] = unpatched_url
                app["versionDescription"] = f"Automatically updated to release {tag_name}"
                updated = True

    # Overwrite the updated values clean mapping back down to disk storage
    if updated:
        with open("apps.json", "w") as f:
            json.dump(repo_json, f, indent=2)
        print(f"Success: Database configuration maps updated cleanly to variant version {clean_version}!")
    else:
        print("Status: Local repository file match records are already up to date with the latest release.")
else:
    print(f"Network Alert: Unable to reach GitHub API endpoint index. Error code: {response.status_code}")
