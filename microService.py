# average_calculator_microservice.py
from flask import Flask, jsonify
import requests
from collections import deque

app = Flask(__name__)

PORT = 9876
WINDOW_SIZE = 10
REQUEST_TIMEOUT = 0.5 

AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzQ0Mzg2NjM3LCJpYXQiOjE3NDQzODYzMzcsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6IjAwMjkxYjI1LTYyOWQtNDFhOC05MjFjLTIxMWM3YWY1YjUwMSIsInN1YiI6InBhdml0aHJhcHJhYmh1MjAwNEBnbWFpbC5jb20ifSwiZW1haWwiOiJwYXZpdGhyYXByYWJodTIwMDRAZ21haWwuY29tIiwibmFtZSI6InBhdml0aHJhIGEgcHJhYmh1Iiwicm9sbE5vIjoiNGNiMjJjczA4MyIsImFjY2Vzc0NvZGUiOiJuWllEcUgiLCJjbGllbnRJRCI6IjAwMjkxYjI1LTYyOWQtNDFhOC05MjFjLTIxMWM3YWY1YjUwMSIsImNsaWVudFNlY3JldCI6IlRUWWtRanBKQVJjTnlualMifQ.gD5SDQE7vKQqEL9vylUGHlzpbDhlkwBVe90Nbs_Lj4I"

TEST_SERVICE_URL = "http://20.244.56.144/evaluation-service"
API_ENDPOINTS = {
    'p': f"{TEST_SERVICE_URL}/primes",
    'f': f"{TEST_SERVICE_URL}/fibo",
    'e': f"{TEST_SERVICE_URL}/even",
    'r': f"{TEST_SERVICE_URL}/rand"
}

number_store = {
    'p': deque(maxlen=WINDOW_SIZE), 
    'f': deque(maxlen=WINDOW_SIZE),  
    'e': deque(maxlen=WINDOW_SIZE),
    'r': deque(maxlen=WINDOW_SIZE)
}

def calculate_average(numbers):
    # Calculate the average of a list of numbers
    if not numbers:
        return 0
    return round(sum(numbers) / len(numbers), 2)

@app.route('/numbers/<number_id>', methods=['GET'])
def get_numbers(number_id):
    # Main API endpoint to get numbers and calculate average
    # Validate number ID
    if number_id not in ['p', 'f', 'e', 'r']:
        return jsonify({"error": "Invalid number ID. Use p, f, e, or r."}), 400
    
    # Store current state before fetching new numbers
    window_prev_state = list(number_store[number_id])
    
    try:
        headers = {
            'Authorization': f'Bearer {AUTH_TOKEN}'
        }
        try:
            response = requests.get(
                API_ENDPOINTS[number_id],
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                new_numbers = response.json().get('numbers', [])
                
                for num in new_numbers:
                    if num not in number_store[number_id]:
                        number_store[number_id].append(num)
            elif response.status_code == 401 or response.status_code == 403:
                print(f"Authorization error: {response.status_code}")
            else:
                print(f"API error: {response.status_code}")
        
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print(f"Request failed: {e}")
        
        current_numbers = list(number_store[number_id])
        average = calculate_average(current_numbers)
        
        response_data = {
            "windowPrevState": window_prev_state,
            "windowCurrState": current_numbers,
            "numbers": current_numbers,
            "avg": average
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=PORT, debug=False)