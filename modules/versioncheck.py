import requests
from packaging import version

def check_for_updates(current_version, repo_owner, repo_name):
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Error: {err}")
        return None
    
    release_data = response.json()
    latest_version_str = release_data.get("tag_name", "").lstrip("vV-")
    print(latest_version_str)

    if latest_version_str:
        latest_version = version.parse(latest_version_str)
        current_version = version.parse(current_version)

        if latest_version > current_version:
            print(f"A new version ({latest_version_str}) is available! Consider updating.")
            return True
        else:
            print("Your application is up to date.")
            return False
    else:
        print("Unable to fetch the latest version information.")
        return False


def main ():
    # Example usage:
    current_version = "0.0.0"  # Replace this with your current version
    repo_owner = "loki077"
    repo_name = "SITL-Launcher"
    check_for_updates(current_version, repo_owner, repo_name)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')