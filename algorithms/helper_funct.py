import math
def  select_transport(coordinates1, coordinates2, priority="cost"):
    coordinates1 = tuple(coordinates1) if isinstance(coordinates1, list) else coordinates1
    coordinates2 = tuple(coordinates2) if isinstance(coordinates2, list) else coordinates2
    R = 6371.0
    lat1_rad = math.radians(coordinates1[0])
    lon1_rad = math.radians(coordinates1[1])
    lat2_rad = math.radians(coordinates2[0])
    lon2_rad = math.radians(coordinates2[1])
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    if priority == "cost":
        if distance < 3:
            mode = "feet"
            speed = 5
        elif distance > 100:
            mode = "taxi"
            speed = 100
        elif distance > 50:
            
            mode = "bus"
            speed = 70
        else:
            mode = "taxi"
            speed = 80
    else:
        if distance < 3:
            mode = "feet"
            speed = 5
        elif distance > 450:
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
def plane_mode_calculation(place1, place2, airport1, airport2):
    distance = select_transport(airport1, airport2, "time")[0]
    time = (distance / 600)*60
    distance_place1_airport1, duration1, mode1 = select_transport(place1, airport1, "time")
    distance_place2_airport2, duration2, mode2 = select_transport(place2, airport2, "time")
    distance = distance + distance_place1_airport1 + distance_place2_airport2
    time = time + duration1 + duration2
    cost =(distance_place1_airport1 * price_per_km(mode1) + \
        (distance_place2_airport2 * price_per_km(mode2)) + \
        (distance * price_per_km("plane")))
    
    return distance, round(time * 60, 0), cost
def find_state_info(current_place, next_place, priority):
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
        
        current_gps = current_place["gps"] if isinstance(current_place, dict) else current_place["gps"]
        next_gps = next_place["gps"] if isinstance(next_place, dict) else next_place["gps"]
        current_gps = tuple(current_gps) if isinstance(current_gps, list) else current_gps
        next_gps = tuple(next_gps) if isinstance(next_gps, list) else next_gps
            

        # Calculate transport
        distance, travel_time, mode = select_transport(current_gps, next_gps, priority)
        
        # Handle plane case
        if mode == "plane" :
            
                current_airport = current_place.get("airport_coordinates") if isinstance(current_place, dict) else current_place.get("airport_coordinates")
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
        
        return total_cost, transport_cost, travel_time, mode

def price_per_km(mode):  # Changed to instance method
    if mode == "feet":
        return 0
    if mode == "plane":
        return 17.5
    elif mode == "bus":
        return 2.3
    elif mode == "taxi":
        return 25

def g_n_function(self, state,place, travel_time, travel_cost):
        """
        Calculate path cost considering:
        - Travel time and cost (normalized)
        - User satisfaction with destination/hotel
        - User's priority (cost vs time)
        It takes the arguments : 
        - self : reference to the problem
        - state : to get the previous total_path_cost
        - place : the destination or the hotel  and the total path cost
        - travel_time : the time of the transport from the previous place(destination/hotel)
        - travel_cost : the total price cost for this state (transport_cost + fees/price_per_night)
        """
        # Normalize values to comparable scales
        normalized_time = travel_time / 240  # assuming 4 hour max between locations
        normalized_cost = travel_cost / (self.budget / (7 / self.dests_per_day))  # vs daily budget
        
        # Calculate how much user would like this place
        if place.get("stars"):
            # Hotel rating check
            stars = place["stars"]  
            if stars <= self.hotel_stars[1] and stars >= self.hotel_stars[0]: 
                satisfaction_score = 1  # within preferred range
            else:
                satisfaction_score = 0.5  # outside range
        else:
            # Destination rating check
            if place["category"] in self.categories:
                wanted = 1  # preferred category
            else:
                wanted = 0.3  # less preferred
            satisfaction_score = (place["rating"]/5) * wanted 

        # Convert satisfaction to cost (higher satisfaction = lower cost)
        dissatisfaction_cost = 1 - satisfaction_score
        day_penalty = (-0.1*state.day) 
        
        # Weight factors based on user priority
        if self.priority == "cost":  
            return 0.5 * normalized_cost + 0.3 * normalized_time + 0.2 * dissatisfaction_cost + state.total_path_cost + day_penalty
        else:  # time priority
            return 0.5 * normalized_time + 0.3 * normalized_cost + 0.2 * dissatisfaction_cost + state.total_path_cost + day_penalty
        
        
        
def satisfaction_score_destination(destination,categories=None):
    rating = destination["rating"]
    category = destination["category"]
    if category in categories :
        wanted = 2
    else:
        wanted = 1
    return (rating/5) * wanted 

#hotel
def satisfaction_score_hotel(hotel,hotel_stars):
    min_stars , max_stars = hotel_stars
    stars=hotel["stars"]
    if stars <= max_stars and stars >= min_stars:
        wanted = 2
    else:
        wanted = 1
    return  (stars/5) * wanted   
        