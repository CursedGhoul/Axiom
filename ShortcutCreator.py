# pip install pywin32
import os
import glob
import win32com.client

def find_icon_image(filename, start_directory):
    # Search for the image 'AxiomLogo.ico' starting from the Downloads directory (instead of PNG)
    print(f"Searching for {filename} starting from {start_directory}...")
    matches = glob.glob(os.path.join(start_directory, '**', filename), recursive=True)
    if matches:
        print(f"Found icon file: {matches[0]}")
        return matches[0]
    else:
        print(f"Icon file {filename} not found.")
        return None

def find_file(file_name, start_directory):
    # Search for AxiomFileManager.py starting from the Downloads directory
    print(f"Searching for {file_name} starting from {start_directory}...")
    for root, dirs, files in os.walk(start_directory):
        if file_name in files:
            print(f"Found script file: {os.path.join(root, file_name)}")
            return os.path.join(root, file_name)
    print(f"{file_name} not found in {start_directory}.")
    return None

def create_shortcut_with_pywin32(target_path, shortcut_path, icon_path):
    try:
        # Create the Shell object
        shell = win32com.client.Dispatch('WScript.Shell')
        
        # Debug print paths
        print(f"Creating shortcut for target: {target_path}")
        print(f"Saving shortcut to: {shortcut_path}")
        print(f"Using icon from: {icon_path}")
        
        # Create the shortcut
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = target_path  # Path to the target script
        shortcut.IconLocation = icon_path  # Path to the icon
        shortcut.save()  # Save the shortcut
        
        print(f"Shortcut created at: {shortcut_path}")
    except Exception as e:
        print(f"Error creating shortcut with pywin32: {e}")

def get_desktop_path():
    # First, check if the Desktop is in OneDrive
    one_drive_desktop_path = os.path.join(os.path.expanduser('~'), 'OneDrive', 'Desktop')
    
    # Check if OneDrive Desktop path exists
    if os.path.exists(one_drive_desktop_path):
        print(f"Found Desktop in OneDrive at: {one_drive_desktop_path}")
        return one_drive_desktop_path
    
    # If not found, fallback to the default Desktop path
    default_desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    print(f"Using default Desktop path: {default_desktop_path}")
    return default_desktop_path

def main():
    # Get the path of the Downloads directory
    downloads_path = os.path.join(os.environ['USERPROFILE'], 'Downloads').replace("\\", "/")
    
    # Find the icon file (AxiomLogo.ico) starting from the Downloads directory
    icon_path = find_icon_image("AxiomLogo.ico", downloads_path)
    if icon_path is None:
        return
    
    # Find the AxiomFileManager.py file starting from the Downloads directory
    script_path = find_file('AxiomFileManager.py', downloads_path)
    if script_path is None:
        return
    
    # Get the correct Desktop path (either in OneDrive or default)
    desktop_path = get_desktop_path().replace("\\", "/")
    
    # Path where the shortcut will be created
    shortcut_name = 'Axiom.lnk'
    shortcut_path = os.path.join(desktop_path, shortcut_name).replace("\\", "/")
    
    # Ensure the Desktop path exists
    if not os.path.exists(desktop_path):
        print(f"Error: The Desktop path does not exist: {desktop_path}")
        return
    
    # Create the shortcut using pywin32
    create_shortcut_with_pywin32(script_path, shortcut_path, icon_path)

if __name__ == "__main__":
    main()
