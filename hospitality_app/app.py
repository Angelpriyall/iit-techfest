import re
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_mail import Mail, Message
from dotenv import load_dotenv
import pandas as pd
import os
import logging


load_dotenv()

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for flashing messages
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.secret_key = os.getenv('SECRET_KEY')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

UPLOAD_FOLDER = 'uploads/'
OUTPUT_FOLDER = 'output/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class User(UserMixin):
    def __init__(self, id):
        self.id = id

users = {'angelpriyal': {'password': 'hello'}}  # In a real application, use a database

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_files():
    if request.method == 'POST':
        if 'group_file' not in request.files or 'hostel_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        group_file = request.files['group_file']
        hostel_file = request.files['hostel_file']
        if group_file.filename == '' or hostel_file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        group_path = os.path.join(app.config['UPLOAD_FOLDER'], group_file.filename)
        hostel_path = os.path.join(app.config['UPLOAD_FOLDER'], hostel_file.filename)

        group_file.save(group_path)
        hostel_file.save(hostel_path)

        try:
            output_file = allocate_rooms(group_path, hostel_path)
        except Exception as e:
            logging.error(f'Error processing files: {e}')
            flash(f'Error processing files: {e}')
            return redirect(request.url)

        return send_file(output_file, as_attachment=True)
    else:
        return render_template('upload.html')

def send_email_notification(user_email, output_file):
    msg = Message('Room Allocation Completed',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user_email])
    msg.body = f'The room allocation process has been completed. You can download the results from the following link: {output_file}'
    mail.send(msg)

def allocate_rooms(group_csv_path, hostel_csv_path):
    group_df = pd.read_csv(group_csv_path)
    hostel_df = pd.read_csv(hostel_csv_path)
    allocations = []

    boys_hostels = hostel_df[hostel_df['Gender'] == 'Boys']
    girls_hostels = hostel_df[hostel_df['Gender'] == 'Girls']

    logging.info('Starting room allocation process.')

    for index, group in group_df.iterrows():
        group_id = group['Group ID']
        members = group['Members']
        gender = group['Gender']

        logging.info(f'Allocating Group ID {group_id} with {members} members and gender {gender}')

        allocated = False

        if gender.lower() == 'boys':
            allocated = allocate_group(allocations, boys_hostels, group_id, members)

        elif gender.lower() == 'girls':
            allocated = allocate_group(allocations, girls_hostels, group_id, members)

        else:
            boys, girls = parse_mixed_gender(gender)
            boys_allocated = allocate_mixed_group(allocations, boys_hostels, group_id, boys, 'Boys')
            girls_allocated = allocate_mixed_group(allocations, girls_hostels, group_id, girls, 'Girls')

            if boys_allocated < boys or girls_allocated < girls:
                allocations.append({
                    'Group ID': group_id,
                    'Hostel Name': 'Not Allocated',
                    'Room Number': 'Not Allocated',
                    'Members Allocated': f'{boys_allocated} Boys & {girls_allocated} Girls'
                })
                logging.warning(f'Group ID {group_id} not fully allocated.')

    allocation_df = pd.DataFrame(allocations)
    output_path = os.path.join(OUTPUT_FOLDER, 'allocation.csv')
    allocation_df.to_csv(output_path, index=False)
    logging.info('Room allocation process completed.')
    return output_path

def parse_mixed_gender(gender):
    match = re.match(r'(\d+)\s*Boys\s*&\s*(\d+)\s*Girls', gender, re.IGNORECASE)
    if match:
        boys = int(match.group(1))
        girls = int(match.group(2))
        return boys, girls
    else:
        # Attempt a more flexible parsing
        match = re.match(r'(\d+)\s*Boys\s*and\s*(\d+)\s*Girls', gender, re.IGNORECASE)
        if match:
            boys = int(match.group(1))
            girls = int(match.group(2))
            return boys, girls
        else:
            raise ValueError(f'Invalid gender format: {gender}')

def allocate_group(allocation, hostels, group_id, members):
    for idx, hostel in hostels.iterrows():
        if hostel['Capacity'] >= members:
            allocation.append({
                'Group ID': group_id,
                'Hostel Name': hostel['Hostel Name'],
                'Room Number': hostel['Room Number'],
                'Members Allocated': members
            })
            hostels.at[idx, 'Capacity'] -= members
            logging.info(f'Group ID {group_id} allocated to {hostel["Hostel Name"]} Room {hostel["Room Number"]}')
            return True
    logging.warning(f'Group ID {group_id} could not be allocated.')
    return False

def allocate_mixed_group(allocation, hostels, group_id, members, gender):
    members_allocated = 0
    for idx, hostel in hostels.iterrows():
        if members_allocated < members and hostel['Capacity'] > 0:
            allocate_members = min(members - members_allocated, hostel['Capacity'])
            allocation.append({
                'Group ID': group_id,
                'Hostel Name': hostel['Hostel Name'],
                'Room Number': hostel['Room Number'],
                'Members Allocated': f'{allocate_members} {gender}'
            })
            members_allocated += allocate_members
            hostels.at[idx, 'Capacity'] -= allocate_members
            logging.info(f'{allocate_members} {gender} from Group ID {group_id} allocated to {hostel["Hostel Name"]} Room {hostel["Room Number"]}')
    return members_allocated

if __name__ == '__main__':
    app.run(debug=True)
