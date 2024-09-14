# Room Allocation Project

## Overview

This project is a room allocation system using vs code, which allows users to upload group and hostel information via CSV files, processes the data, and allocates rooms based on gender and availability.

## Prerequisites

Ensure you have the following installed on your system:

- Python 3.x
- pip (Python package manager)
- Virtualenv (optional but recommended)

## Setup Instructions

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/Angelpriyall/iit-techfest/tree/main

 

### 2. Navigate to the Project Directory
Move into the project directory:

bash
Copy code
cd your-repository
###3. Create and Activate a Virtual Environment (Optional but Recommended)
Creating a virtual environment helps manage dependencies:

On Windows:
bash
Copy code
python -m venv venv
venv\Scripts\activate
On macOS/Linux:
bash
Copy code
python3 -m venv venv
source venv/bin/activate
4. Install Project Dependencies
Install the required Python packages using:

bash
Copy code
pip install -r requirements.txt
5. Set Up Environment Variables
Create a .env file in the root directory of the project and add the following variables:

env
Copy code
SECRET_KEY=your_secret_key
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_password
Replace your_secret_key, your_email@example.com, and your_password with your actual values.

6. Run the Application
Start the Flask application by running:

bash
Copy code
python app.py
The application will start in development mode, and you can access it at:

arduino
Copy code
http://127.0.0.1:5000
7. Access the Application
Open a web browser and navigate to http://127.0.0.1:5000.

8. Logging In
Use the following credentials to log in:

Username: angelpriyal
Password: hello

### Key Points Covered:

- **Overview:** Introduction to what the project does.
- **Setup Instructions:** Step-by-step guide to set up and run the project, including creating a virtual environment, installing dependencies, and running the Flask app.
- **Usage Instructions:** How to access and use the application, including login details and CSV file formats.
- **Troubleshooting:** Basic steps for resolving common issues.
- **Contributing:** Information on how others can contribute to the project.
- **License:** Placeholder for license information. 

This format ensures that anyone who clones my repository can quickly understand how to set up and use