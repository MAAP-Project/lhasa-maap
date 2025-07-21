#!/usr/bin/env python3
"""
Script to set up .netrc file from MAAP secrets manager.

This script automates the creation of netrc authentication files by retrieving
credentials from the MAAP (Multi-Mission Algorithm and Analysis Platform) secrets manager
instead of relying on environment variables.

Reads the following secrets from MAAP secrets manager and writes them to ~/.netrc:
- urs_username: NASA Earthdata username
- urs_password: NASA Earthdata password  
- pps_email: PPS EOSDIS email
- pps_password: PPS EOSDIS password

The netrc file enables automatic authentication for NASA data services without
requiring manual credential entry for each data access request.
"""

import os
import sys
from platform import system
from maap.maap import MAAP


def get_netrc_path():
    """
    Get the appropriate netrc file path based on the operating system.
    
    The netrc filename convention differs between operating systems:
    - Windows uses '_netrc' (underscore prefix)
    - Unix/Linux/macOS use '.netrc' (dot prefix)
    
    Returns:
        str: Full path to the netrc file in the user's home directory
    """
    # Determine the correct netrc filename based on OS
    netrc_name = "_netrc" if system() == "Windows" else ".netrc"
    # Return the full path in the user's home directory
    return os.path.join(os.path.expanduser("~"), netrc_name)


def read_secrets():
    """
    Read and validate required secrets from MAAP secrets manager.
    
    Connects to the MAAP secrets manager and retrieves the four required
    authentication secrets needed for NASA data services. Validates that
    all secrets exist and are accessible.
    
    Returns:
        dict: Dictionary containing secret names as keys and secret values as values
        
    Exits:
        Terminates the program with exit code 1 if:
        - MAAP client initialization fails
        - Any required secrets are missing or inaccessible
    """
    # Define the required secret names for NASA data access
    required_secrets = ["urs_username", "urs_password", "pps_email", "pps_password"]
    secret_values = {}  # Dictionary to store retrieved secret values
    missing_secrets = []  # List to track any missing secrets
    
    # Initialize the MAAP client for accessing secrets manager
    try:
        maap = MAAP()
    except Exception as e:
        print(f"Error: Failed to initialize MAAP client: {e}")
        sys.exit(1)
    
    # Retrieve each required secret from the secrets manager
    for secret in required_secrets:
        try:
            # Call the MAAP secrets API to get the secret value
            response = maap.secrets.get_secret(secret)
            
            # Check if the response indicates the secret doesn't exist (404 error)
            if isinstance(response, dict) and 'code' in response and response['code'] == 404:
                missing_secrets.append(secret)
            else:
                # Secret exists, store its value
                secret_values[secret] = response
        except Exception as e:
            # Handle any other errors during secret retrieval
            print(f"Error retrieving secret '{secret}': {e}")
            missing_secrets.append(secret)
    
    # If any secrets are missing, provide helpful error message and exit
    if missing_secrets:
        print(f"Error: Missing required secrets: {', '.join(missing_secrets)}")
        print("Please add the following secrets to MAAP secrets manager:")
        print("- urs_username: NASA Earthdata username")
        print("- urs_password: NASA Earthdata password")
        print("- pps_email: PPS EOSDIS email")
        print("- pps_password: PPS EOSDIS password")
        print("\nUse: maap.secrets.add_secret('secret_name', 'secret_value')")
        sys.exit(1)
    
    return secret_values


def write_netrc_file(secret_values, file_path):
    """
    Write the netrc file with the provided credentials.
    
    Creates a netrc file with the proper format for NASA Earthdata and PPS
    authentication. The file includes machine-specific login credentials
    for automated authentication.
    
    Args:
        secret_values (dict): Dictionary containing the secret values
        file_path (str): Full path where the netrc file should be written
        
    Exits:
        Terminates the program with exit code 1 if:
        - Permission denied when writing to the file path
        - Any other file writing error occurs
    """
    try:
        # Create netrc content with proper machine entries
        # Format follows netrc specification: machine, login, password per line
        netrc_content = f"""machine urs.earthdata.nasa.gov
  login {secret_values['urs_username']}
  password {secret_values['urs_password']}
machine jsimpsonhttps.pps.eosdis.nasa.gov
  login {secret_values['pps_email']}
  password {secret_values['pps_password']}
"""
        
        # Write the netrc content to the file
        with open(file_path, 'w') as f:
            f.write(netrc_content)
        
        # Set appropriate file permissions (readable/writable by owner only)
        # This is a security requirement for netrc files - they must not be
        # readable by other users since they contain plain text passwords
        os.chmod(file_path, 0o600)
        
        print(f"Successfully created {file_path} with NASA Earthdata and PPS credentials")
        
    except PermissionError:
        # Handle permission errors (e.g., trying to write to protected directory)
        print(f"Error: Permission denied writing to {file_path}")
        sys.exit(1)
    except Exception as e:
        # Handle any other file writing errors
        print(f"Error writing to {file_path}: {e}")
        sys.exit(1)


def main():
    """
    Main function to set up netrc from MAAP secrets manager.
    
    Orchestrates the entire netrc setup process:
    1. Retrieves credentials from MAAP secrets manager
    2. Determines the correct netrc file path for the operating system
    3. Warns if an existing netrc file will be overwritten
    4. Creates the new netrc file with retrieved credentials
    """
    print("Setting up .netrc file from MAAP secrets manager...")
    
    # Retrieve all required secrets from MAAP secrets manager
    secret_values = read_secrets()
    
    # Determine the correct netrc file path for this operating system
    file_path = get_netrc_path()
    
    # Warn the user if an existing netrc file will be overwritten
    if os.path.exists(file_path):
        print(f"Warning: {file_path} already exists and will be overwritten")
    
    # Create the netrc file with the retrieved credentials
    write_netrc_file(secret_values, file_path)


# Entry point: run main() when script is executed directly
if __name__ == "__main__":
    main()