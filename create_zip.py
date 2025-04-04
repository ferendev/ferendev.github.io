import os
import zipfile
import re

def zip_addon_folder(addon_name, version_file_name):
    # Get the current user's AppData\Roaming folder
    appdata_roaming = os.path.join(os.environ['APPDATA'])
    folder_path = os.path.join(appdata_roaming, 'Kodi', 'addons', addon_name)
    addon_xml_path = os.path.join(folder_path, 'addon.xml')

    # Read the version number from addon.xml
    with open(addon_xml_path, 'r', encoding='utf-8') as file:
        first_line = file.readline().strip()
        version_match = re.search(r'version="([\d\.]+)"', first_line)
        if not version_match:
            raise ValueError("Version number not found in addon.xml")
        version_number = version_match.group(1)

    # Define the output directory and ensure it exists
    output_dir = os.path.join(os.getcwd(), 'packages')
    os.makedirs(output_dir, exist_ok=True)

    # Define the zip file name
    zip_name = os.path.join(output_dir, f'{addon_name}-{version_number}.zip')

    # Create the zip file
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            # Skip .git and __pycache__ folders
            if '.git' in dirs:
                dirs.remove('.git')
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')

            for file in files:
                # Skip .gitignore files
                if file == '.gitignore':
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.join(addon_name, os.path.relpath(file_path, folder_path))
                zipf.write(file_path, arcname)

    print(f"Zip file created: {zip_name}")

    # Update the version file
    version_file_path = os.path.join(output_dir, version_file_name)
    with open(version_file_path, 'w', encoding='utf-8') as version_file:
        version_file.write(version_number)

    return zip_name

def update_index_files(latest_fenlight_zip):
    # Update the index.html file in the packages folder
    index_file_path = os.path.join(os.getcwd(), 'packages', 'index.html')
    with open(index_file_path, 'w', encoding='utf-8') as index_file:
        if latest_fenlight_zip:
            index_file.write(f'<!DOCTYPE html>\n<a href="{os.path.basename(latest_fenlight_zip)}">{os.path.basename(latest_fenlight_zip)}</a>\n')

    # Update the index.html file in the script's folder
    script_index_file_path = os.path.join(os.getcwd(), 'index.html')
    with open(script_index_file_path, 'w', encoding='utf-8') as script_index_file:
        if latest_fenlight_zip:
            script_index_file.write(f'<!DOCTYPE html>\n<a href="packages/{os.path.basename(latest_fenlight_zip)}">{os.path.basename(latest_fenlight_zip)}</a>\n')

def get_latest_zip_from_version_file(version_file_name, addon_name):
    version_file_path = os.path.join(os.getcwd(), 'packages', version_file_name)
    if os.path.exists(version_file_path):
        with open(version_file_path, 'r', encoding='utf-8') as version_file:
            version_number = version_file.read().strip()
            return os.path.join(os.getcwd(), 'packages', f'{addon_name}-{version_number}.zip')
    return None

def extract_latest_changes(changelog_path):
    with open(changelog_path, 'r', encoding='utf-8') as changelog_file:
        lines = changelog_file.readlines()
        latest_changes = []
        for line in lines:
            if line.strip() == '':
                break
            latest_changes.append(line.strip())
        return '\n'.join(latest_changes)

def main():
    latest_fenlight_zip = None

    # Check if plugin.video.fenlight folder exists
    fenlight_folder_path = os.path.join(os.environ['APPDATA'], 'Kodi', 'addons', 'plugin.video.fenlight')
    if os.path.exists(fenlight_folder_path):
        latest_fenlight_zip = zip_addon_folder('plugin.video.fenlight', 'fenlight_version')
        
        # Extract the latest changes from changelog.txt
        changelog_path = os.path.join(fenlight_folder_path, 'resources', 'text', 'changelog.txt')
        if os.path.exists(changelog_path):
            latest_changes = extract_latest_changes(changelog_path)
            changes_file_path = os.path.join(os.getcwd(), 'packages', 'fenlight_changes')
            with open(changes_file_path, 'w', encoding='utf-8') as changes_file:
                changes_file.write(latest_changes)
    else:
        latest_fenlight_zip = get_latest_zip_from_version_file('fenlight_version', 'plugin.video.fenlight')

    # Update the index.html files
    update_index_files(latest_fenlight_zip)

if __name__ == "__main__":
    main()