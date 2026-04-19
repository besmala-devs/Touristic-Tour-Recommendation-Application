import json
import random
import math



def Distance_Time_Priority(coordinates1, coordinates2, priority="cost"):
    R = 6371.0  # radius of earth
    # converting to radians
    lat1_rad = math.radians(coordinates1[0])
    lon1_rad = math.radians(coordinates1[1])
    lat2_rad = math.radians(coordinates2[0])
    lon2_rad = math.radians(coordinates2[1])
    # calculating the differences between the coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    # Auto-select transport mode based on priority
    if distance < 3:
        mode = "walk"
        speed = 5 # average speed when walking
    else:    
        if priority == "cost":
            if distance > 100:
                mode = "bus"
                speed = 70
            elif distance > 50:
                mode = "taxi"
                speed = 100  # Taxis often drive faster
            else:
                mode = "taxi"
                speed = 80  # Taxis often drive slower in cities
        else:
            if distance > 450:
                mode = "plane"
                speed = 600
            elif distance > 50:
                mode = "taxi"
                speed = 100
            else:
                mode = "taxi"
                speed = 80

    time = distance / speed
    return round(distance, 3), round(time * 60, 0), mode


def price_per_km(mode):
    if mode == "plane":
        return 17.5  # price per km for plane
    elif mode == "bus":
        return 7.5  # price per km for bus
    elif mode == "taxi":
        return 25  # price per km for taxi
    else:
        return 0 # nothing for walking



#this function is used to calculate the distance and time between in case of travel plane
#by calculating the distance from place 1 to its airport, then from its airport to the airport
# of the second place, and then from that airport to the second place
def travel_with_plane(priority, place1, place2, airport1=None, airport2=None):
    distance = Distance_Time_Priority(airport1, airport2)[0]
    time = distance / 600  # speed of plane in km/h
    distance_place1_airport1, duration1, mode1 = Distance_Time_Priority(place1, airport1, priority)
    distance_place2_airport2, duration2, mode2 = Distance_Time_Priority(place2, airport2, priority)
    distance = distance + distance_place1_airport1 + distance_place2_airport2
    time = time * 60 + duration1 + duration2
    cost = distance_place1_airport1 * price_per_km(mode1) + distance_place2_airport2 * price_per_km(mode2) + distance * price_per_km("plane")
    
    return distance, round(time, 0), cost


# Load the dataset (attractions and hotels) from JSON files
def get_dataset():
    with open("Dataset/destinations.json", "r", encoding="utf-8") as file_attractions:
        attractions = json.load(file_attractions)
    with open("Dataset/hotels.json", "r", encoding="utf-8") as file_hotels:
        hotels = json.load(file_hotels)
    return attractions, hotels



def total_cost_time(itinerary, start, priority):
    total_cost = 0
    total_time = 0
    current_coordinates = start
    distance, time, mode = Distance_Time_Priority(current_coordinates, itinerary[0][0]["gps"], "cost")
    total_cost += distance * price_per_km(mode)
    total_time += time
    current_coordinates = itinerary[0][0]["gps"]
    previous = itinerary[0][0]
    place_for_hotel = None
    cost = 0
    time = 0
    for i, day in enumerate(itinerary):
        for j, place in enumerate(day):
            if i==0 and j==0:
                continue
            cost = 0
            if "price_per_night" in place:
                place_for_hotel = previous
                
            transport = Distance_Time_Priority(current_coordinates, place["gps"], priority)[2]
            if transport == "plane":
                if "price_per_night" in previous:
                    distance, time, cost = travel_with_plane(
                        priority,
                        current_coordinates,
                        place["gps"],
                        place_for_hotel["airport_coordinates"],
                        place["airport_coordinates"],
                    )
                else:# "price_per_night" not in place:
                    distance, time, cost = travel_with_plane(
                        priority,
                        current_coordinates,
                        place["gps"],
                        previous["airport_coordinates"],
                        place["airport_coordinates"],
                    )
                    
                if "price_per_night" in place:
                    cost += place.get("price_per_night", 0)
                else:
                    cost += place.get("entry_fee", 0)
                    
            else:
                distance, time = Distance_Time_Priority(current_coordinates, place["gps"], priority)[0:2]
                cost += price_per_km(transport) * distance
                if "price_per_night" in place:
                    cost += place.get("price_per_night", 0)
                else:
                    cost += place.get("entry_fee", 0)
                    
            total_cost += cost
            total_time += time
            current_coordinates = place["gps"]
            previous = place
            
    return total_cost, total_time


def get_destination_hotel():
    with open("Dataset/destination_hotel.json", 'r') as file:
        dest_hotel = json.load(file)
    dest_to_hotels = {}
    for mapping in dest_hotel:
        dest_id = mapping["destination_id"]
        hotel_id = mapping["hotel_id"]
        dest_to_hotels.setdefault(dest_id, []).append(hotel_id)
        
    return dest_to_hotels


class State:
    def __init__(self, itinerary, value=0, total_cost=0, total_time=0):
        self.itinerary = itinerary  # list of list
        self.value = value  # Fitness evaluation score
        self.total_cost = total_cost  # Total travel + entry costs
        self.total_time = total_time  # Total time spent traveling

    def __str__(self):
        return f"State(Value: {self.value:.2f}, Cost: {self.total_cost:.2f}, Time: {self.total_time:.2f})"

    def __repr__(self):
        return self.__str__()



class TourismRecommandation:
    def __init__(self, fav_categories, budget, places_per_d, starting_location, priority, history, hotel_min_stars=1, hotel_max_stars=5):
        self.budget = budget
        self.places_per_day = places_per_d
        self.fav_categories = fav_categories
        self.start_location = starting_location  # coordinates of the starting location
        self.priority = priority
        self.min_rating_hotel = hotel_min_stars
        self.max_rating_hotel = hotel_max_stars
        self.visited_history = history
        self.initial_state = self.generate_initial_state()
        

    def generate_initial_state(self):
        attractions, hotels = get_dataset()
        attractions = attractions.copy()
        attractions = [destination for destination in attractions if destination["name"] not in self.visited_history] #remove visited places
        remaining_budget = self.budget
        current_coordinates = self.start_location
        previous = None
        itinerary = []
        day = []
        day_counter = 0
        selected_places = set()
        random.shuffle(attractions)

        for place in attractions:
            if day_counter >= 7:
                break

            if id(place) in selected_places:
                continue

            transport = Distance_Time_Priority(current_coordinates, place["gps"], self.priority)[2]
            if transport == "plane" and previous is not None:
                distance, time, cost = travel_with_plane(
                    self.priority,
                    current_coordinates,
                    place["gps"],
                    previous["airport_coordinates"],
                    place["airport_coordinates"],
                )
                total_cost = cost + place.get("entry_fee", 0)
            else:
                distance = Distance_Time_Priority(current_coordinates, place["gps"], self.priority)[0]
                total_cost = (
                    place.get("entry_fee", 0) + price_per_km(transport) * distance
                )

            if place["category"] in self.fav_categories and total_cost <= remaining_budget:
                if place["category"].lower() in ["aquapark", "beach"]:
                    itinerary.append([place])
                    selected_places.add(id(place))
                    remaining_budget -= total_cost
                    previous = place
                    current_coordinates = place["gps"]
                    day_counter += 1
                else:
                    day.append(place)
                    selected_places.add(id(place))
                    remaining_budget -= total_cost
                    previous = place
                    current_coordinates = place["gps"]
                    if len(day) == self.places_per_day:
                        itinerary.append(day)
                        day = []
                        day_counter += 1

        available_places = [p for p in attractions if id(p) not in selected_places]

        # Fill missing days
        while day_counter < 7 and available_places:
            random.shuffle(available_places)
            random_day = []

            while len(random_day) < self.places_per_day and available_places:
                random_place = available_places.pop()
                if random_place["category"].lower() in ["aquapark", "beach"]:
                    if len(random_day) == 0:
                        itinerary.append([random_place])
                        selected_places.add(id(random_place))
                        day_counter += 1
                        break
                    else:
                        continue
                else:
                    random_day.append(random_place)
                    selected_places.add(id(random_place))

            if random_day and len(random_day) == self.places_per_day:
                itinerary.append(random_day)
                day_counter += 1
                
        
        #appending nearby hotels of the last destination for each day randomly
        dest_to_hotels = get_destination_hotel()
        hotel_lookup = {hotel["hotel_id"]: hotel for hotel in hotels}
        for day in itinerary:
            last_place = day[-1]
            last_place_id = last_place["destination_id"]
            if last_place_id and last_place_id in dest_to_hotels:
                hotels_ids = dest_to_hotels[last_place_id]
                random_hotel_id = random.choice(hotels_ids)
                hotel = hotel_lookup.get(random_hotel_id)
                if hotel:
                    day.append(hotel)
                    
            
        x, y = total_cost_time(itinerary, self.start_location, self.priority)
        eval = self.evaluate(State(itinerary, 0))
        return State(itinerary, eval, round(x, 2), round(y, 2))
    
    

    def evaluate(self, state):
        total_time = 0
        total_cost = 0
        match_type = 0
        total_rating = 0
        itinerary = (
            state.itinerary
        )  # itinerary is now a list of days (each day is a list of places)
        num_places = sum(len(day) for day in itinerary)  # total number of places
        total_cost, total_time = total_cost_time(state.itinerary, self.start_location, self.priority)

        for day in itinerary:
            for place in day:
                if "price_per_night" in place:
                    if place["stars"] <= self.max_rating_hotel and place["stars"] >= self.min_rating_hotel:
                        match_type += 1
                    total_rating += place["stars"]
                else:
                    if place["category"] in self.fav_categories:
                        match_type += 1
                    total_rating += place["rating"]
                
        if num_places == 0:
            return 0  # avoid division by zero
        max_travel_time_per_day = 300  # in minutes (threshold)

        # Normalize values and multiply by weight 25 (to make results clear and not to small)
        match_score = 25 * (match_type / num_places)
        rating_score = 25 * (total_rating / num_places / 5)
        time_penalty = 25 * (total_time / (max_travel_time_per_day * 7))
        cost_penalty = 25 * (total_cost / self.budget)

        return match_score + rating_score - time_penalty - cost_penalty



    def generate_neighbors(self, state):
        attractions, hotels = get_dataset()
        itinerary = state.itinerary
        attractions = attractions.copy()
        attractions = [place for place in attractions if place["name"] not in self.visited_history] #remove visited places
        neighbors = []

        def create_state(new_nested_itinerary):
            return State(new_nested_itinerary, self.evaluate(State(new_nested_itinerary, 0)))

        def deep_copy(itinerary):
            return [day[:] for day in itinerary]

        def is_single_place(place):
            return place.get("category", "").lower() in ["aquapark", "beach"]

        def is_attraction(place):
            return "category" in place  # Hotel doesn't have 'category'
        
        def replace_hotel_with_another_nearby(day):
            if len(day) < 1:
                return
            last_attraction = day[-1] if "price_per_night" not in day[-1] else day[-2]
            if "destination_id" not in last_attraction:
                    return

            dest_to_hotels = get_destination_hotel()
            hotel_lookup = {hotel["hotel_id"]: hotel for hotel in hotels}
            hotel_ids = dest_to_hotels.get(last_attraction["destination_id"], [])

            # Remove existing hotel if present
            if "price_per_night" in day[-1]:
                day.pop()
                
            if not hotel_ids:
                return

            new_hotel_id = random.choice(hotel_ids)
            hotel = hotel_lookup.get(new_hotel_id)
            if hotel:
                day.append(hotel)
        

        # Replacing places with other places of the same category
        for _ in range(30):
            new_itinerary = deep_copy(itinerary)
            day_idx = random.randint(0, len(new_itinerary) - 1)
            day = new_itinerary[day_idx]

            # Only look at attractions
            day_attractions = [p for p in day if is_attraction(p)]
            if not day_attractions:
                continue

            place_idx = random.randint(0, len(day_attractions) - 1)
            current_place = day_attractions[place_idx]

            similar_places = [
                p
                for p in attractions
                if "category" in p and p["category"] == current_place["category"]
                and all(p != place for day in itinerary for place in day)
            ]
            if similar_places:
                new_place = random.choice(similar_places)
                # Replace the exact item in the itinerary
                original_idx = day.index(current_place)
                day[original_idx] = new_place
                replace_hotel_with_another_nearby(day)
                neighbors.append(create_state(new_itinerary))
                

        # Swap 2 places (only attractions)
        for _ in range(20):
            new_itinerary = deep_copy(itinerary)
            valid_places = [
                (day_idx, place_idx)
                for day_idx, day in enumerate(new_itinerary)
                for place_idx, place in enumerate(day)
                if is_attraction(place) and not is_single_place(place)
            ]
            if len(valid_places) < 2:
                continue
            (day1, place1), (day2, place2) = random.sample(valid_places, 2)
            new_itinerary[day1][place1], new_itinerary[day2][place2] = (
                new_itinerary[day2][place2],
                new_itinerary[day1][place1],
            )
            replace_hotel_with_another_nearby(new_itinerary[day1])
            replace_hotel_with_another_nearby(new_itinerary[day2])
            neighbors.append(create_state(new_itinerary))
            

        # Replace places with random attractions (not hotels or single-place types)
        for _ in range(20):
            new_itinerary = deep_copy(itinerary)
            day_idx = random.randint(0, len(new_itinerary) - 1)
            day = new_itinerary[day_idx]

            day_attractions = [p for p in day if is_attraction(p) and not is_single_place(p)]
            if not day_attractions:
                continue

            place = random.choice(day_attractions)
            place_idx = day.index(place)

            random_place = random.choice(
                [
                    p
                    for p in attractions
                    if all(p != place for day in itinerary for place in day)
                    and not is_single_place(p)
                ]
            )
            day[place_idx] = random_place
            replace_hotel_with_another_nearby(day)
            neighbors.append(create_state(new_itinerary))

        
        return neighbors

    
    

# Steepest ascent hill climbing search
def SteepestAscent_HillClimbing(problem, max_iterations=100):
    current_state = problem.initial_state
    print("\n--- Starting Steepest Ascent Hill Climbing Search ---")
    for iteration in range(max_iterations):
        neighbors = problem.generate_neighbors(current_state)
        if not neighbors:
            print("No neighbors generated. Terminating.")
            break

        sorted_neighbors = sorted(neighbors, key=lambda x: x.value, reverse=True)
        chosen_neighbor = sorted_neighbors[0]
        if chosen_neighbor.value > current_state.value:
            print(
                f"\nIteration {iteration+1}: Improved score from {round(current_state.value, 2)} to {round(chosen_neighbor.value, 2)}"
            )
            current_state = chosen_neighbor
        else:
            print(
                f"\nIteration {iteration+1}: No better neighbor found. Stopping search."
            )
            break

    print("\n--- Final Result After Steepest Ascent Hill Climbing ---")
    x, y = total_cost_time(current_state.itinerary, problem.start_location, problem.priority)
    current_state = State(current_state.itinerary, current_state.value, round(x, 2), round(y, 0))
    return current_state




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


def distance_cost_time_one_place(start, state, priority):
    full_list = []
    day_list = []
    current_coor = start
    distance = 0
    cost = 0
    time = 0
    previous = None
    for day in state.itinerary:
        for place in day:
            if "price_per_night" in place:
                place_of_hotel = previous
            transport = Distance_Time_Priority(current_coor, place['gps'], priority)[2]
            
            if transport == "plane":
                if "price_per_night" in previous:
                    distance, time, cost = travel_with_plane(priority, previous['gps'], place['gps'], place_of_hotel["airport_coordinates"], place["airport_coordinates"])
                else:
                    distance, time, cost = travel_with_plane(priority, previous['gps'], place['gps'], previous["airport_coordinates"], place["airport_coordinates"])
            else:
                distance, time = Distance_Time_Priority(current_coor, place["gps"], priority)[0:2]
                cost = distance * price_per_km(transport) #+ place.get("entry_fee", 0) + place.get("price_per_night", 0)
        
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
    restaurant_lookup = {r['restaurant_id']: r for r in restaurants}
    dest_to_restaurants = {}

    for entry in destination_restaurant:
        dest_id = entry['destination_id']
        rest_id = entry['restaurant_id']
        dest_to_restaurants.setdefault(dest_id, []).append(rest_id)

    # Iterate over each day's destinations
    for day in state.itinerary:
        day_list = []
        for destination in day:
            if "entry_fee" in destination:
                dest_id = destination['destination_id']
                nearby_ids = dest_to_restaurants.get(dest_id, [])
                if nearby_ids:
                    selected_rest_id = random.choice(nearby_ids)
                    restaurant_info = restaurant_lookup.get(selected_rest_id)
                    if restaurant_info:
                        day_list.append(restaurant_info)
        full_list.append(day_list)

    return full_list
    
        

def run_hill_climbing(fav_categories, budget, places_per_d, starting_location, priority, history, hotel_min_stars, hotel_max_stars):
    tourism = TourismRecommandation(
        fav_categories=fav_categories,
        budget=budget,
        places_per_d=places_per_d,
        starting_location=starting_location,
        priority=priority,
        history=history,
        hotel_min_stars=hotel_min_stars,
        hotel_max_stars=hotel_max_stars
    )
    
    initial_state = tourism.initial_state
    final_state = SteepestAscent_HillClimbing(tourism, 100)
    
    accomodation, entry_fees = get_accomodation_entryfees(final_state)
    travel_cost = round(final_state.total_cost - accomodation - entry_fees, 0)
    single_place_details = distance_cost_time_one_place(starting_location, final_state, priority)
    restaurants = nearby_restaurants(final_state)

    result = {
        "itinerary": final_state.itinerary,
        "total_cost": final_state.total_cost,
        "total_time": final_state.total_time,
        "accommodation_cost": accomodation,
        "entry_fees": entry_fees,
        "travel_cost": travel_cost,
        "partial_details": single_place_details,
        "nearby_restaurants": restaurants
    }
    return result