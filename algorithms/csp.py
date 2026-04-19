# Importing the necessary tools for our itinerary planner
from typing import List, Dict, Any, Optional  # For better code documentation
from itertools import product  # For combining possibilities
import json  # To work with our data files
import random  # To shuffle destinations for variety
from copy import deepcopy  # For safe copying of complex objects
from pprint import pprint  # For pretty printing outputs
from functools import lru_cache  # For potential optimization
from algorithms.helper_funct import (  # Our transportation calculation helpers
    select_transport,
    price_per_km,
    plane_mode_calculation,
)


def find_state_info_csp(current_place, next_place, priority):
    # Initialize costs
    transport_cost = 0
    total_cost = 0

    # Handle case where current_place might be a list
    if isinstance(current_place, list):
        if current_place:
            current_place = current_place[0]
        else:
            raise ValueError("Empty list provided as current_place")

    # Get coordinates safely

    current_gps = (
        current_place["gps"]
        if isinstance(current_place, dict)
        else current_place["gps"]
    )
    next_gps = next_place["gps"] if isinstance(next_place, dict) else next_place["gps"]
    current_gps = tuple(current_gps) if isinstance(current_gps, list) else current_gps
    next_gps = tuple(next_gps) if isinstance(next_gps, list) else next_gps

    # Calculate transport
    distance, travel_time, mode = select_transport(current_gps, next_gps, priority)

    # Handle plane case
    if mode == "plane":

        current_airport = (
            current_place.get("airport_coordinates")
            if isinstance(current_place, dict)
            else current_place.get("airport_coordinates")
        )
        next_airport = next_place.get("airport_coordinates")

        if current_airport and next_airport:
            distance, travel_time, transport_cost = plane_mode_calculation(
                current_gps, next_gps, current_airport, next_airport
            )

    else:
        transport_cost = price_per_km(mode) * distance

    # Add entry fee or hotel cost
    if isinstance(next_place, dict):
        if "stars" in next_place:  # Hotel
            total_cost = next_place.get("price_per_night", 0) + transport_cost
        else:  # Destination
            total_cost = next_place.get("entry_fee", 0) + transport_cost

    return total_cost, transport_cost, travel_time, mode, distance


def nearby_restaurants_csp(state):
    full_list = []
    with open("Dataset/restaurants.json", "r", encoding="utf-8") as file:
        restaurants = json.load(file)
    # Load destination-restaurant mappings
    with open("Dataset/destination_restaurant.json", "r", encoding="utf-8") as file:
        destination_restaurant = json.load(file)

    # Create lookup tables for performance
    restaurant_lookup = {r["restaurant_id"]: r for r in restaurants}
    dest_to_restaurants = {}

    for entry in destination_restaurant:
        dest_id = entry["destination_id"]
        rest_id = entry["restaurant_id"]
        dest_to_restaurants.setdefault(dest_id, []).append(rest_id)

    # Iterate over each day's destinations
    for day in state:
        day_list = []
        for destination in day:
            if "entry_fee" in destination:
                dest_id = destination["destination_id"]
                nearby_ids = dest_to_restaurants.get(dest_id, [])
                if nearby_ids:
                    selected_rest_id = random.choice(nearby_ids)
                    restaurant_info = restaurant_lookup.get(selected_rest_id)
                    if restaurant_info:
                        day_list.append(restaurant_info)
        full_list.append(day_list)

    return full_list


class ItineraryCSP:
    def __init__(
        self,
        current_location,
        destinations,
        hotels,
        budget,
        categories,
        hotel_stars,
        priority,
        max_dests_per_day,
        travel_history,
    ):
        """The main planner that holds all our trip constraints and preferences"""
        # Storing all the user's requirements and preferences
        self.destinations = destinations  # All possible places to visit
        self.hotels = hotels  # All available lodging options
        self.budget = budget  # The total spending limit
        self.categories = categories  # Types of attractions user likes
        self.hotel_stars = hotel_stars  # Preferred hotel quality range
        self.priority = priority  # What to optimize (cost vs time)
        self.max_dests_per_day = max_dests_per_day  # Daily activity limit
        self.travel_history = travel_history  # Places already seen
        self.current_location = current_location  # Starting point
        self.transport_info = {}  # Will store our transportation details
        self.total_cost = 0
        # Setting up the framework for our 7-day itinerary:
        self.variables = ["l0"]  # Always starts with current location

        # Create slots for each day's activities and accommodations
        for day in range(1, 8):  # 7 days of travel
            # Create destination slots for each day
            for dest_slot in range(1, max_dests_per_day + 1):
                self.variables.append(f"d({day},{dest_slot})")
            # Add a hotel slot for each night
            self.variables.append(f"h{day}")

        # Generate all possible options for each slot
        self.original_domains = self._create_domains()
        # Keep a working copy we can modify
        self.current_domains = deepcopy(self.original_domains)

        # All the rules our itinerary must follow:
        self.constraints = [
            self._already_visited_constraint,  # No repeat visits
            self._budget_time_constraint,  # Stay within means and time
            self._aquapark_beach_constraint,  # Special cases
            self._category_constraint,  # Only preferred types
            self._hotel_constraint,  # Hotel quality control
        ]

    def _create_domains(self):
        """Generates all possible options for each time slot"""
        domains = {}
        # Starting point is always current location
        domains["l0"] = [
            {
                "type": "current_location",
                "data": {
                    "name": "Current location of the user",
                    "gps": self.current_location["gps"],
                },
            }
        ]

        # Filter out places already visited
        filtered_destinations = [
            dest
            for dest in self.destinations
            if dest["name"] not in self.travel_history
        ]

        # Create options for each destination time slot
        for day in range(1, 8):
            for dest_slot in range(1, self.max_dests_per_day + 1):
                domains[f"d({day},{dest_slot})"] = [
                    {"type": "destination", "data": dest}
                    for dest in filtered_destinations
                ]

            # Create options for each night's hotel stay
            domains[f"h{day}"] = [
                {"type": "hotel", "data": hotel} for hotel in self.hotels
            ]
        return domains

    def _already_visited_constraint(self, assignment):
        """Ensures we don't visit the same place twice"""
        visited = set()
        # Check all destination slots across all days
        for day in range(1, 8):
            for dest_slot in range(1, self.max_dests_per_day + 1):
                var = f"d({day},{dest_slot})"
                if var in assignment:
                    dest_name = assignment[var]["data"]["name"]
                    if dest_name in visited:  # Found a duplicate!
                        return False
                    else:
                        visited.add(dest_name)  # Mark as visited
        return True  # All unique destinations!

    def _budget_time_constraint(self, assignment):
        """The accountant - tracks costs and time spent"""
        self.transport_info = {}  # Reset transport details
        total_cost = 0  # Start with empty wallet
        daily_times = {day: 0 for day in range(1, 8)}  # 8 hours/day max
        debug_missing_transport = []  # Track missing transport calculations

        # Helper to easily add expenses
        def add_cost(cost, fee=0):
            nonlocal total_cost
            total_cost += cost + fee
            return total_cost

        # 1. First journey: home to first destination
        if "l0" in assignment and "d(1,1)" in assignment:
            try:
                _, cost, time, mode, distance = find_state_info_csp(
                    assignment["l0"]["data"],
                    assignment["d(1,1)"]["data"],
                    self.priority,
                )
                self.transport_info["transport_d(1,1)"] = (cost, time, mode, distance)
                daily_times[1] += time
                add_cost(cost, assignment["d(1,1)"]["data"].get("entry_fee", 0))
            except Exception as e:
                debug_missing_transport.append(f"l0→d(1,1): {str(e)}")

        # 2. Between same-day destinations
        for day in range(1, 8):
            for slot in range(1, self.max_dests_per_day):
                current_var = f"d({day},{slot})"
                next_var = f"d({day},{slot+1})"

                if current_var in assignment and next_var in assignment:
                    try:
                        _, cost, time, mode, distance = find_state_info_csp(
                            assignment[current_var]["data"],
                            assignment[next_var]["data"],
                            self.priority,
                        )
                        self.transport_info[f"transport_{next_var}"] = (
                            cost,
                            time,
                            mode,
                            distance,
                        )
                        daily_times[day] += time
                        add_cost(cost, assignment[next_var]["data"].get("entry_fee", 0))
                    except Exception as e:
                        debug_missing_transport.append(
                            f"{current_var}→{next_var}: {str(e)}"
                        )

        # 3. Last destination → Hotel (same day)
        for day in range(1, 8):
            last_dest_var = f"d({day},{self.max_dests_per_day})"
            hotel_var = f"h{day}"

            if last_dest_var in assignment and hotel_var in assignment:
                try:
                    _, cost, time, mode, distance = find_state_info_csp(
                        assignment[last_dest_var]["data"],
                        assignment[hotel_var]["data"],
                        self.priority,
                    )
                    self.transport_info[f"transport_{hotel_var}"] = (
                        cost,
                        time,
                        mode,
                        distance,
                    )
                    daily_times[day] += time
                    add_cost(
                        cost, assignment[hotel_var]["data"].get("price_per_night", 0)
                    )
                except Exception as e:
                    debug_missing_transport.append(
                        f"{last_dest_var}→{hotel_var}: {str(e)}"
                    )

        # 4. Hotel → Next day's first destination
        for day in range(1, 7):
            hotel_var = f"h{day}"
            next_day_var = f"d({day+1},1)"

            if hotel_var in assignment and next_day_var in assignment:
                try:
                    _, cost, time, mode, distance = find_state_info_csp(
                        assignment[hotel_var]["data"],
                        assignment[next_day_var]["data"],
                        self.priority,
                    )
                    self.transport_info[f"transport_{next_day_var}"] = (
                        cost,
                        time,
                        mode,
                        distance,
                    )
                    daily_times[day + 1] += time
                    add_cost(cost, assignment[next_day_var]["data"].get("entry_fee", 0))
                except Exception as e:
                    debug_missing_transport.append(
                        f"{hotel_var}→{next_day_var}: {str(e)}"
                    )

        self.total_cost = total_cost
        self.total_time = 0
        for time in daily_times.values():
            self.total_time += time

        return (
            all(time <= 100 for time in daily_times.values())
            and total_cost <= self.budget
        )

    def _aquapark_beach_constraint(self, assignment):
        """Special rule for water-related attractions"""
        for day in range(1, 8):
            categories = []
            # Collect all categories for this day's destinations
            for slot in range(1, self.max_dests_per_day + 1):
                var = f"d({day},{slot})"
                if var in assignment:
                    categories.append(assignment[var]["data"].get("category", ""))

            # Check if we have special attractions with restrictions
            has_special = any(cat in ["Beach", "Aquapark"] for cat in categories)
            if has_special and len(categories) > 1:
                return False  # Can't mix these with other attractions
        return True

    def _category_constraint(self, assignment):
        """Ensures we only visit preferred types of places"""
        for var in assignment:
            if var.startswith("d("):
                category = assignment[var]["data"].get("category", "")
                if category not in self.categories:
                    return False  # Found an unwanted category
        return True

    def _hotel_constraint(self, assignment):
        """Quality control for accommodations"""
        min_stars, max_stars = self.hotel_stars
        for var in assignment:
            if var.startswith("h"):
                stars = assignment[var]["data"].get("stars", 0)
                if not (min_stars <= stars <= max_stars):
                    return False  # Hotel doesn't meet standards
        return True

    def _is_consistent(self, assignment):
        """Master checker for all rules"""
        return all(constraint(assignment) for constraint in self.constraints)

    def _backtrack(self, assignment):
        """The puzzle solver - tries different combinations"""
        # First check if we've planned all required days
        all_complete = True
        for day in range(1, 8):
            has_dest = any(
                f"d({day},{slot})" in assignment
                for slot in range(1, self.max_dests_per_day + 1)
            )
            has_hotel = f"h{day}" in assignment
            if not (has_dest and has_hotel):
                all_complete = False
                break

        if all_complete:  # Found a complete itinerary!
            return assignment

        varia = deepcopy(self.variables)
        for day in range(1, 8):

            # Collect all categories for this day's destinations
            var = f"d({day},1)"
            if var in assignment and assignment[var]["data"] in ["Beach", "Aquapark"]:
                for slot in range(2, self.max_dests_per_day + 1):
                    del varia[f"d({day},{slot})"]

        # Find the next empty slot to fill
        var = next((v for v in varia if v not in assignment), None)
        if not var:
            return None  # No solution found down this path

        # Try all possible options for this slot
        for value in self.current_domains[var]:
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self._is_consistent(new_assignment):  # If this choice follows rules
                result = self._backtrack(new_assignment)  # Try next slot
                if result is not None:  # If it led to a solution
                    return result
        return None  # No valid options for this path

    def solve(self):
        """Starts the itinerary planning process"""
        return self._backtrack({})


def load_data():
    """Our data loader - reads attraction and hotel info"""
    try:
        # Load and shuffle destinations for variety
        with open("Dataset/destinations.json", encoding="utf-8") as f:
            destinations = json.load(f)
            # random.shuffle(destinations)

        # Load and shuffle hotels
        with open("Dataset/hotels.json", encoding="utf-8") as f:
            hotels = json.load(f)
            # random.shuffle(hotels)

        return destinations, hotels
    except FileNotFoundError as e:
        print(f"Missing data files: {e}")
        return None, None
    except json.JSONDecodeError as e:
        print(f"Problem reading data files: {e}")
        return None, None


def test_itinerary_planner():
    """Our test driver - sets up a sample trip"""
    # Try loading real data first
    destinations, hotels = load_data()
    # Set up our dream trip parameters
    current_location = {"name": "Home", "gps": [35.90606, 7.76013]}  # Starting point
    budget = 90000  # Spending limit
    categories = ["Historical Landmark", "Museum", "Nature", "Beach"]  # Interests
    hotel_stars = (2, 4)  # Accommodation standards
    priority = "cost"  # Optimization focus
    max_dests_per_day = 2  # Daily pace
    travel_history = ["Tipaza Roman Ruins"]  # Already seen

    # Print our trip parameters
    print("=== BUILDING YOUR DREAM ITINERARY ===")
    print(f"Budget: {budget}")
    print(f"Interests: {categories}")
    print(f"Hotel standards: {hotel_stars[0]} to {hotel_stars[1]} stars")
    print(f"Optimizing for: {priority}\n")

    # Create our trip planner with these parameters
    csp = ItineraryCSP(
        current_location=current_location,
        destinations=destinations,
        hotels=hotels,
        budget=budget,
        categories=categories,
        hotel_stars=hotel_stars,
        priority=priority,
        max_dests_per_day=max_dests_per_day,
        travel_history=travel_history,
    )

    # Generate and display the itinerary
    solution = csp.solve()
    result = resolve(solution, csp)
    print(result)


def resolve(places, csp):
    itinerary = []
    for day in range(1, 8):
        daylist = []
        # Add all destinations for the day
        for slot in range(1, csp.max_dests_per_day + 1):  # Fixed to include last slot
            var = f"d({day},{slot})"
            if var in places:
                daylist.append(places[var]["data"])
        # Add hotel for the day
        hotel_var = f"h{day}"
        if hotel_var in places:
            daylist.append(places[hotel_var]["data"])
        itinerary.append(daylist)

    total_cost = csp.total_cost
    total_time = csp.total_time
    travel_cost = 0
    accommodation_cost = 0
    entry_fees = 0
    partial_details = []

    for day in range(1, 8):
        # Process destinations transport info
        day_list = []
        for slot in range(1, csp.max_dests_per_day + 1):
            var = f"d({day},{slot})"
            transport_var = f"transport_{var}"
            if var in places and transport_var in csp.transport_info:
                place_info = csp.transport_info[transport_var]
                distance = place_info[3]
                time = place_info[1]
                trans_cost = place_info[0]
                travel_cost += trans_cost
                mode = place_info[2]
                day_list.append([distance, round(time, 0), round(trans_cost, 2), mode])
                if "entry_fee" in places[var]["data"]:
                    entry_fees += places[var]["data"]["entry_fee"]

        # Process hotel transport info
        hotel_var = f"h{day}"
        transport_hotel_var = f"transport_{hotel_var}"
        if hotel_var in places and transport_hotel_var in csp.transport_info:
            place_info = csp.transport_info[transport_hotel_var]
            distance = place_info[3]
            time = place_info[1]
            trans_cost = place_info[0]
            travel_cost += trans_cost
            mode = place_info[2]
            day_list.append([distance, round(time, 0), round(trans_cost, 2), mode])
            if "price_per_night" in places[hotel_var]["data"]:
                accommodation_cost += places[hotel_var]["data"]["price_per_night"]
        partial_details.append(day_list)
    nearby_restaurants = nearby_restaurants_csp(itinerary)

    result = {
        "itinerary": itinerary,
        "total_cost": round(total_cost, 2),
        "total_time": round(total_time, 2),
        "accommodation_cost": round(accommodation_cost, 2),
        "entry_fees": round(entry_fees, 2),
        "travel_cost": round(travel_cost, 2),
        "partial_details": partial_details,
        "nearby_restaurants": nearby_restaurants,
    }

    return result  # Added missing return statement


def run_csp(
    fav_categories,
    budget,
    places_per_d,
    starting_location,
    priority,
    history,
    hotel_min_stars,
    hotel_max_stars,
):

    destinations, hotels = load_data()

    # Set up our dream trip parameters
    current_location = {"name": "Home", "gps": starting_location}  # Starting point

    categories = fav_categories  # Interests
    hotel_stars = (hotel_min_stars, hotel_max_stars)  # Accommodation standards

    max_dests_per_day = places_per_d  # Daily pace
    travel_history = history  # Already seen
    # Create our trip planner with these parameters
    csp = ItineraryCSP(
        current_location=current_location,
        destinations=destinations,
        hotels=hotels,
        budget=budget,
        categories=categories,
        hotel_stars=hotel_stars,
        priority=priority,
        max_dests_per_day=max_dests_per_day,
        travel_history=travel_history,
    )

    # Generate and display the itinerary
    solution = csp.solve()

    result = resolve(solution, csp)
    return result


if __name__ == "__main__":
    test_itinerary_planner()
