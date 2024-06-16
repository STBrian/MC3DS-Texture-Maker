import os, time, requests, zipfile, shutil, platform, psutil
from packaging import version

GITHUB_API_URL = "https://api.github.com/repos/STBrian/MC3DS-Texture-Maker/releases"
DOWNLOAD_FOLDER = "update_data"
if os.path.exists('.\\mc3ds-tm-gui.exe'):
    FLAG_01 = 1
    OLD_EXE_NAME = "mc3ds-tm-gui.exe"
EXECUTABLE_NAME = "MC3DS-Texture-Maker.exe"
EXECUTABLE_PATH = os.path.join(DOWNLOAD_FOLDER, EXECUTABLE_NAME)

def get_latest_release_url():
    response = requests.get(GITHUB_API_URL)
    response.raise_for_status()
    releases = response.json()
    os_platform = "windows" if platform.system().lower() == "windows" else "linux"

    latest_release = None
    latest_version = version.parse("0.0.0")

    for release in releases:
        try:
            release_version = version.parse(release["tag_name"].lstrip('v'))
        except version.InvalidVersion:
            # Skip invalid version strings
            continue

        for asset in release["assets"]:
            if os_platform in asset["name"].lower() and asset["name"].endswith(".zip"):
                if release_version > latest_version:
                    latest_release = asset["browser_download_url"]
                    latest_version = release_version

    if not latest_release:
        raise Exception("No compatible release found")

    return latest_release

def download_and_extract_zip(url, extract_to):
    response = requests.get(url)
    response.raise_for_status()
    zip_path = os.path.join(extract_to, "latest_release.zip")
    with open(zip_path, "wb") as f:
        f.write(response.content)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(zip_path)

def read_bytes(file_path, num_bytes=0x1F4):
    with open(file_path, "rb") as f:
        return f.read(num_bytes)

def find_and_terminate_process(name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == name:
            proc.terminate()
            proc.wait()

def main():
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    print(f"Fetching Latests Release...")
    latest_release_url = get_latest_release_url()
    print(f"Extracting Latest Release into Temp Directory...")
    download_and_extract_zip(latest_release_url, DOWNLOAD_FOLDER)

    if os.path.exists(EXECUTABLE_PATH):
        print("Reading Downloaded File...")
        new_executable_bytes = read_bytes(EXECUTABLE_PATH)
    else:
        raise Exception("Downloaded executable not found")

    existing_executable_path = os.path.join(".", EXECUTABLE_NAME)
    if os.path.exists(existing_executable_path):
        print("Reading Original File...")
        existing_executable_bytes = read_bytes(existing_executable_path)
    else:
        existing_executable_bytes = b''

    if new_executable_bytes != existing_executable_bytes:
        find_and_terminate_process(EXECUTABLE_NAME)
        shutil.copytree(DOWNLOAD_FOLDER, ".", dirs_exist_ok=True)
        shutil.rmtree(DOWNLOAD_FOLDER, ignore_errors=True)

        print(f"Downloaded Latest Version of {EXECUTABLE_NAME.replace('.exe','')}.")
        time.sleep(5)

if __name__ == "__main__":
    main()
