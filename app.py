# Required imports
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import googlemaps
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure API keys and clients
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))


class TravelGuide:
    def __init__(self):
        self.openai_client = client
        self.gmaps = gmaps

    def get_travel_recommendations(self, destination, duration, interests):
        # Create a detailed prompt for OpenAI
        prompt = f"""Create a detailed travel guide for {destination} for {duration} days.
        Interests: {interests}
        Please include:
        1. Best time to visit
        2. Top attractions
        3. Day-wise itinerary
        4. Local food recommendations
        5. Travel tips
        6. Estimated budget
        Format the response in a structured way."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable travel guide."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating recommendations: {str(e)}"

    def get_places_info(self, destination):
        try:
            # Search for places using Google Maps API
            places_result = self.gmaps.places(destination)
            
            # Get first place details
            if places_result['results']:
                place_id = places_result['results'][0]['place_id']
                place_details = self.gmaps.place(place_id)
                
                return {
                    'name': place_details['result'].get('name'),
                    'address': place_details['result'].get('formatted_address'),
                    'rating': place_details['result'].get('rating'),
                    'photos': place_details['result'].get('photos', []),
                    'location': place_details['result']['geometry']['location']
                }
            return None
        except Exception as e:
            return f"Error fetching place info: {str(e)}"


# Initialize TravelGuide
travel_guide = TravelGuide()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    destination = data.get('destination')
    duration = data.get('duration')
    interests = data.get('interests')

    # Get AI recommendations
    ai_recommendations = travel_guide.get_travel_recommendations(
        destination, duration, interests
    )

    # Get place information
    place_info = travel_guide.get_places_info(destination)

    return jsonify({
        'recommendations': ai_recommendations,
        'place_info': place_info
    })


if __name__ == '__main__':
    app.run(debug=True, port=5010)