import subprocess
import shutil
import os

# Whitelist of allowed applications: maps user-friendly name to executable/command
# Using Windows start mechanism so works even if app isn't in PATH
WHITELIST = {
    "chrome": "chrome",
    "edge": "msedge",
    "notepad": "notepad",
    "calculator": "calc",
    "vscode": "Code",          # VS Code executable
    "file explorer": "explorer",
    "vs code": "Code",         # alias
}

def open_app(name):
    """
    Attempt to open an application by name.
    Returns a dict with 'success' boolean and 'message' string.
    """
    # Normalize input for matching (case-insensitive, strip whitespace)
    name_lower = name.strip().lower()

    # Check if app is in whitelist
    if name_lower in WHITELIST:
        # Special handling for Chrome and Edge due to PATH issues
        if name_lower == "chrome":
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Google\Chrome\Application\chrome.exe")
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    try:
                        subprocess.Popen([path])
                        return {
                            "success": True,
                            "message": f"Opening {name}."
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "message": f"Failed to open {name}: {str(e)}"
                        }
            return {
                "success": False,
                "message": f"App '{name}' is not found on this system."
            }
        elif name_lower == "edge":
            possible_paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    try:
                        subprocess.Popen([path])
                        return {
                            "success": True,
                            "message": f"Opening {name}."
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "message": f"Failed to open {name}: {str(e)}"
                        }
            return {
                "success": False,
                "message": f"App '{name}' is not found on this system."
            }
        else:
            # For other apps, use the original shutil.which + start mechanism
            app_command = WHITELIST[name_lower]
            # Check if the executable actually exists on the system
            if shutil.which(app_command) is None:
                return {
                    "success": False,
                    "message": f"App '{name}' is not found on this system."
                }
            try:
                # Use Windows start command to launch application
                subprocess.Popen(["start", app_command], shell=True)
                return {
                    "success": True,
                    "message": f"Opening {name}."
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Failed to open {name}: {str(e)}"
                }
    else:
        return {
            "success": False,
            "message": f"App '{name}' is not allowed."
        }