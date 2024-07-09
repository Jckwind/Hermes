# Google Drive Upload Tool Instructions

To make the Google Drive upload tool work, follow these instructions:

1. **Create a Service Account**
   - Search "Create Service Account" on Google.
   - Scroll down to the blue button that says "Go to Service Account".
   - Click "Create Project" (in the top right corner).
   - Click the box with the project name (Ideally name it Hermes).

2. **Generate and Download the Key**
   - Click the 3 dots on the right side of the screen and go to "Create Key".
   - Select the option to download the key in JSON format.

3. **Setup the Project**
   - Open up Hermes and put the JSON file in the directory `src/model/google_drive_upload`.

4. **Create and Share a Google Drive Folder**
   - In your Google Drive, create a new folder and name it appropriately.
   - Share the folder with the email address of the service account you created on the Google Cloud Console.
   - Make sure to give it editor permissions.
   - The parent ID folder is the url extention of the folder in your browser