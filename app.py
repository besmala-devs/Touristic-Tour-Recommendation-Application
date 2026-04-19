from flask import Flask, request, jsonify, render_template
from algorithms.hill_climbing import run_hill_climbing
from algorithms.astar import run_astar
from algorithms.problem_formulation import TourItineraryProblem
from algorithms.dls import run_dls
from algorithms.ucs import run_ucs
from algorithms.csp import run_csp
import json

app = Flask(__name__)
with open("Dataset/hotels.json", "r", encoding="utf-8") as f:
    hotels = json.load(f)

with open("Dataset/destinations.json", "r", encoding="utf-8") as f:
    destinations = json.load(f)

with open("Dataset/destination_hotel.json", "r", encoding="utf-8") as f:
    destination_hotel = json.load(f)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/tour")
def tour():
    return render_template("tour.html")


@app.route("/generate_tour", methods=["POST"])
def generate_tour():
    try:
        # Get the JSON data from the request
        form_data = request.get_json()

        print("Form Data received from frontend:", form_data)

        # You can now process the form data as needed

        # For example, access the data like this:

        current_loc = form_data["currentLocation"]
        selected_destinations = form_data["selectedDestinations"]
        preferences = form_data["preferences"]
        print(f"Starting location: {current_loc}")
        current_location = {
            "name": "Zeralda",
            "gps": current_loc,
        }
        algorithm = preferences["algorithm"]

        if algorithm == "Astar":
            problem = TourItineraryProblem(
                search_strategy=preferences["algorithm"],
                current_location=current_location,
                destinations=destinations,
                categories=preferences["categories"],
                budget=int(preferences["budget"]),
                dests_per_day=int(preferences["destinationsPerDay"]),
                travel_history=[d["name"] for d in selected_destinations],
                hotels=hotels,
                hotel_stars=(
                    int(preferences["hotelStars"]["min"]),
                    int(preferences["hotelStars"]["max"]),
                ),
                destination_hotel=destination_hotel,
                priority=preferences["priority"],
            )
            result = run_astar(problem)

        elif algorithm == "Steepest HC":
            result = run_hill_climbing(
                fav_categories=preferences["categories"],
                budget=int(preferences["budget"]),
                places_per_d=int(preferences["destinationsPerDay"]),
                starting_location=current_loc,
                priority=preferences["priority"],
                history=[d["name"] for d in selected_destinations],
                hotel_min_stars=int(preferences["hotelStars"]["min"]),
                hotel_max_stars=int(preferences["hotelStars"]["max"]),
            )

        elif algorithm == "UCS":
            result = run_ucs(
                fav_categories=preferences["categories"],
                budget=int(preferences["budget"]),
                places_per_d=int(preferences["destinationsPerDay"]),
                starting_location=current_loc,
                priority=preferences["priority"],
                history=[d["name"] for d in selected_destinations],
                hotel_min_stars=int(preferences["hotelStars"]["min"]),
                hotel_max_stars=int(preferences["hotelStars"]["max"]),
            )

        elif algorithm == "DLS":
            result = run_dls(
                fav_categories=preferences["categories"],
                budget=int(preferences["budget"]),
                places_per_d=int(preferences["destinationsPerDay"]),
                starting_location=current_loc,
                priority=preferences["priority"],
                history=[d["name"] for d in selected_destinations],
                hotel_min_stars=int(preferences["hotelStars"]["min"]),
                hotel_max_stars=int(preferences["hotelStars"]["max"]),
            )
        elif algorithm == "CSP":
            result = run_csp(
                fav_categories=preferences["categories"],
                budget=int(preferences["budget"]),
                places_per_d=int(preferences["destinationsPerDay"]),
                starting_location=current_loc,
                priority=preferences["priority"],
                history=[d["name"] for d in selected_destinations],
                hotel_min_stars=int(preferences["hotelStars"]["min"]),
                hotel_max_stars=int(preferences["hotelStars"]["max"]),
            )
        # You can do any processing here, then return a response
        return jsonify(
            {
                "status": "success",
                "message": "Tour data received successfully",
                "data": result,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
