from flask import Flask, render_template, request, flash
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flashing messages

# Webex API base URL
WEBEX_API_BASE_URL = "https://webexapis.com/v1"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        token = request.form['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Option 0: Test connection with Webex server
        if 'test_connection' in request.form:
            response = requests.get(f'{WEBEX_API_BASE_URL}/people/me', headers=headers)
            if response.status_code == 200:
                flash('Connection successful!')
            else:
                error_message = response.json().get('message', 'Unknown error occurred')
                flash(f'Connection failed: {error_message}')

        # Option 1: Display user information
        elif 'get_user_info' in request.form:
            response = requests.get(f'{WEBEX_API_BASE_URL}/people/me', headers=headers)
            if response.status_code == 200:
                user_info = response.json()
                return render_template('index.html', user_info=user_info)
            else:
                error_message = response.json().get('message', 'Unknown error occurred')
                flash(f'Failed to retrieve user information: {error_message}')

        # Option 2: Display list of rooms
        elif 'list_rooms' in request.form:
            response = requests.get(f'{WEBEX_API_BASE_URL}/rooms', headers=headers)
            if response.status_code == 200:
                rooms_info = response.json().get('items', [])[:5]  # Get the first 5 rooms
                return render_template('index.html', rooms_info=rooms_info)
            else:
                error_message = response.json().get('message', 'Unknown error occurred')
                flash(f'Failed to retrieve rooms: {error_message}')

        # Option 3: Create a room
        elif 'create_room' in request.form:
            room_title = request.form['room_title']
            response = requests.post(f'{WEBEX_API_BASE_URL}/rooms', headers=headers, json={"title": room_title})
            if response.status_code == 200:
                flash('Room created successfully!')
            else:
                error_message = response.json().get('message', 'Unknown error occurred')
                flash(f'Failed to create room: {error_message}')

        # Option 4: Send message to a room
        if 'send_message' in request.form:
            room_id = request.form['room_id']
            message = request.form['message']
            send_message_response = send_message(room_id, message, headers)

            if send_message_response['status'] == 'success':
                flash('Message sent successfully!')
            else:
                flash(f'Failed to send message: {send_message_response["error"]}')

    return render_template('index.html')

def send_message(room_id, message, headers):
    """Function to send a message to a specified Webex room."""
    url = f'{WEBEX_API_BASE_URL}/messages'
    payload = {
        "roomId": room_id,
        "text": message
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        return {'status': 'success'}
    except requests.exceptions.HTTPError as http_err:
        error_message = response.json().get('message', 'Unknown error occurred')
        return {'status': 'error', 'error': error_message}
    except Exception as err:
        return {'status': 'error', 'error': str(err)}

if __name__ == '__main__':
    app.run(debug=True)
