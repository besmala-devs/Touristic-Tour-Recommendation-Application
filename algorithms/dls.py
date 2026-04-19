import heapq, random
from typing import List, Dict, Tuple, Optional
from algorithms.problem_formulation import TourItineraryProblem, State
import json

with open("Dataset/destinations.json", "r", encoding="utf-8") as file:
    destinations = json.load(file)
with open("Dataset/hotels.json", "r", encoding="utf-8") as file:
    hotels = json.load(file)
with open("Dataset/destination_hotel.json", "r", encoding="utf-8") as file:
    destination_hotel = json.load(file)
from algorithms.helper_funct import (
    select_transport,
    find_state_info,
    price_per_km,
    g_n_function,
)


def travel_with_plane(priority, place1, place2, airport1=None, airport2=None):
    distance = select_transport(airport1, airport2, priority)[0]
    time = distance / 600  # speed of plane in km/h
    distance_place1_airport1, duration1, mode1 = select_transport(
        place1, airport1, priority
    )
    distance_place2_airport2, duration2, mode2 = select_transport(
        place2, airport2, priority
    )
    distance = distance + distance_place1_airport1 + distance_place2_airport2
    time = time * 60 + duration1 + duration2
    cost = (
        distance_place1_airport1 * price_per_km(mode1)
        + distance_place2_airport2 * price_per_km(mode2)
        + distance * price_per_km("plane")
    )

    return distance, round(time, 0), cost


def distance_cost_time_one_place(start, state, priority):
    full_list = []
    day_list = []
    current_coor = start['gps']
    distance = 0
    cost = 0
    time = 0
    previous = None
    for day in state.itinerary:
        for place in day:
            if "price_per_night" in place:
                place_of_hotel = previous
            transport = select_transport(current_coor, place["gps"], priority)[2]
            if transport == "plane":
                if "price_per_night" in previous:
                    distance, time, cost = travel_with_plane(
                        priority,
                        previous["gps"],
                        place["gps"],
                        place_of_hotel["airport_coordinates"],
                        place["airport_coordinates"],
                    )
                else:
                    distance, time, cost = travel_with_plane(
                        priority,
                        previous["gps"],
                        place["gps"],
                        previous["airport_coordinates"],
                        place["airport_coordinates"],
                    )
            else:
                distance, time = select_transport(current_coor, place["gps"], priority)[
                    0:2
                ]
                cost = distance * price_per_km(
                    transport
                )  # + place.get("entry_fee", 0) + place.get("price_per_night", 0)

            day_list.append([distance, round(time, 0), round(cost, 2), transport])
            previous = place
            current_coor = place["gps"]
        full_list.append(day_list)
        day_list = []

    return full_list


def nearby_restaurants(state):
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
    for day in state.itinerary:
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


def get_accomodation_entryfees(state):
    accomodation = 0
    entry_fees = 0
    for day in state.itinerary:
        for destination in day:
            if "price_per_night" in destination:
                accomodation += destination["price_per_night"]
            else:
                entry_fees += destination["entry_fee"]
    return accomodation, entry_fees



def dls(problem):
    initial_state = problem.initial_state()
    depth_limit = problem.dests_per_day * 7
    Frontier = [(initial_state, 0, 0)]  # (state, g_value, depth)
    Explored = set()

    while Frontier:
        current_state, g_value, current_depth = Frontier.pop()

        # Skip if already explored or over budget
        if current_state in Explored :
            continue

        Explored.add(current_state)

        # Check if goal state reached
        if problem.goal_test(current_state):
            print("Goal state found!")
            return current_state

        # Skip if depth limit reached
        if current_depth >= depth_limit:
            continue

        # Explore possible next destinations
        possible_children = problem.possible_destinations(current_state)

        for child in possible_children:
            total_cost, transport_cost, travel_time, mode = find_state_info(
                current_state.current_location, 
                child, 
                problem.priority
            )
            
            new_g_value = g_n_function(
                problem,
                current_state, 
                child, 
                travel_time, 
                total_cost # pass the total cost to the g_n_ not the transp
            )
            
            new_state = problem.update_state(
                current_state.copy(),
                child,
                new_g_value,
                mode,
                transport_cost,
                travel_time
            )
            
            Frontier.append((new_state, new_g_value, current_depth + 1))

    print("\nNo solution found within depth limit")
    print(f"Explored {len(Explored)} states")
    print(f"Maximum depth reached: {depth_limit}")
    return None
    

def run_dls(fav_categories, budget, places_per_d, starting_location, priority, history, hotel_min_stars, hotel_max_stars):
    start_location = {"gps":starting_location}

    problem = TourItineraryProblem(
        "ucs",
        start_location,
        destinations,
        fav_categories,
        budget,
        places_per_d,
        history,
        hotels,
        (hotel_min_stars, hotel_max_stars),# (min , max)
        destination_hotel,
        priority  # "cost" or "time"
    )

    final_result = dls(problem)
    restaurants = nearby_restaurants(final_result)
    # Sum all travel costs and times
    total_travel_cost = sum(trip[1] for trip in final_result.transport_info)
    total_travel_time = sum(trip[2] for trip in final_result.transport_info)
    accommodation, entry_fees = get_accomodation_entryfees(final_result)
    single_place_details = distance_cost_time_one_place(
        problem.current_location, final_result, problem.priority
    )
    result = {
        "itinerary": final_result.itinerary,
        "total_cost": final_result.total_cost,
        "total_time": total_travel_time,
        "accommodation_cost": accommodation,
        "entry_fees": entry_fees,
        "travel_cost": round(total_travel_cost, 0),
        "partial_details": single_place_details,
        "nearby_restaurants": restaurants,
    }

    if result:
        for day, plan in enumerate(result["itinerary"]):
            print(f"\nDay {day + 1}:")
            for stop in plan:
                if "stars" in stop:
                    print(f"Hotel: {stop['name']} ({stop['stars']} stars)")
                else:
                    print(
                        f"Destination: {stop['name']} ({stop['category']}) ({stop['region']})"
                    )

        print(f"\nTotal cost: {result['total_cost']:.2f} DZD")
        print(f"Total time: {result['total_time']} hours")
        print(f"Accommodation cost: {result['accommodation_cost']:.2f} DZD")
        print(f"Entry fees: {result['entry_fees']:.2f} DZD")
        print(f"Travel cost: {result['travel_cost']:.2f} DZD")
        print(f"Partial details: {result['partial_details']}")
        print(f"Nearby restaurants: {result['nearby_restaurants']}")
        
    return result

"""
if __name__ == "__main__":
   fav_categories =['Museum', 'Beach', 'Religious Site']
   budget = 100000
   places_per_d= 2
   starting_location= [36.7296512, 3.047424]
   priority='cost'
   history=[]
   hotel_min_stars=3
   hotel_max_stars=5
   run_dls(fav_categories, budget, places_per_d, starting_location, priority, history, hotel_min_stars, hotel_max_stars)
"""