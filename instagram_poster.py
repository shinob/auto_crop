#!/usr/bin/env python3  

import os
import sys
from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired
# Import credentials from the config file
import config

class InstagramPoster:
    """
    A class to handle posting photos to Instagram.
    """
    def __init__(self, username=None, password=None):
        """
        Initializes the Instagram client and logs in.
        Credentials can be provided directly or will be fetched from config.py.
        """
        self.username = username or config.INSTAGRAM_USERNAME
        self.password = password or config.INSTAGRAM_PASSWORD

        if self.username == "YOUR_USERNAME_HERE" or self.password == "YOUR_PASSWORD_HERE":
            raise ValueError("Please update your credentials in config.py before running.")

        if not self.username or not self.password:
            raise ValueError("Instagram username and password must be provided or set in config.py.")

        self.cl = Client()
        try:
            self.cl.login(self.username, self.password)
        except TwoFactorRequired:
            # Handle two-factor authentication
            verification_code = input("Enter two-factor verification code: ")
            self.cl.login(self.username, self.password, verification_code=verification_code)
        except Exception as e:
            # Re-raise the exception to be handled by the caller
            raise Exception(f"Instagram login failed: {e}")

    def upload_photo(self, image_path, caption):
        """
        Uploads a photo to Instagram.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image path does not exist: {image_path}")

        try:
            self.cl.photo_upload(image_path, caption)
            print(f"Successfully uploaded {image_path} with caption: {caption}")
            return True
        except Exception as e:
            print(f"An error occurred during upload: {e}")
            return False

def show_usage():
    """Prints the usage message and exits."""
    print(f"Usage: python {sys.argv[0]} <image_path> <caption>")
    print("\nThis script uploads a photo to Instagram.")
    print("  <image_path>: The path to the image file to upload.")
    print("  <caption>: The caption for the Instagram post.")
    sys.exit(1)


def main():
    """
    Main function to handle command-line execution.
    """
    # Get image path and caption from command line arguments
    if len(sys.argv) != 3:
        show_usage()

    image_path = sys.argv[1]
    caption = sys.argv[2]

    try:
        # When run as a script, it uses credentials from config.py
        poster = InstagramPoster()
        poster.upload_photo(image_path, caption)
    except (ValueError, FileNotFoundError, Exception) as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
