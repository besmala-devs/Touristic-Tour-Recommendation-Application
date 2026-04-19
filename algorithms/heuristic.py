from algorithms.helper_funct import (
    select_transport
)


def heuristic(problem, current_state):
    current_dest = current_state.current_location
    unvisited = []
    for destination in problem.destinations:
        if (
            destination["name"]
            not in [loc["name"] for day in current_state.itinerary for loc in day]
            and destination["name"] not in [entry["name"] for entry in current_state.day_plan]
            and destination["name"] not in problem.travel_history
        ):
            unvisited.append(destination)

    penalty = 0
    total_cost = 0
    total_time = 0
    number_of_remaining_destination = (
        7 - current_state.day
    ) * problem.dests_per_day + (problem.dests_per_day - len(current_state.day_plan))
    while number_of_remaining_destination != 0:
        min_dist = float("inf")
        min_time = float("inf")
        if number_of_remaining_destination % problem.dests_per_day == 0:
            for unvisited_dest in unvisited:
                distance ,time,mode= select_transport(
                    tuple(current_dest["gps"]), tuple(unvisited_dest["gps"]),problem.priority
                )
                if distance < min_dist:
                    min_dist = distance
                    min_time = time
                    current_dest = unvisited_dest

            if current_dest["category"] in ["Beach", "Aquapark"]:
                number_of_remaining_destination -= (problem.dests_per_day - 1)
            else:
                number_of_remaining_destination -= 1
            if current_dest["category"] not in problem.categories:
                penalty += 1
            if problem.priority == "cost":    
                total_cost += (
                    current_dest["entry_fee"]
                    + min_dist * 7.5 )
                total_time+= round((min_dist / 80) * 60, 0)
            else:
                total_cost += (
                    current_dest["entry_fee"]
                    + min_dist * 25 )
                total_time+= min_time  
            

        elif number_of_remaining_destination % problem.dests_per_day == 1:
            hotels = []
            linked_hotel_ids = {
                entry["hotel_id"]
                for entry in problem.destination_hotel
                if entry["destination_id"] == current_dest["destination_id"]
            }

            for hid in linked_hotel_ids:
                for hotel in problem.hotels:
                    if hotel["hotel_id"] == hid:
                        hotels.append(hotel)
            for Hotel in hotels:
                distance ,time, mode = select_transport(tuple(current_dest["gps"]), tuple(Hotel["gps"]),problem.priority)
                if distance < min_dist:
                    min_dist = distance
                    min_time = time
                    current_dest = Hotel

            if current_dest["stars"] not in problem.hotel_stars:
                penalty += 1
            number_of_remaining_destination -= 1
            if problem.priority == "cost":    
                total_cost += (
                    current_dest["price_per_night"]
                    + min_dist * 7.5 )
                total_time+= min_time
            else:
                total_cost += (
                    current_dest["price_per_night"]
                    + min_dist * 25 )
                total_time+= min_time
            
        else:
            for unvisited_dest in unvisited:
                if unvisited_dest["category"] in ["Beach", "Aquapark"]:
                    continue

                distance ,time,mode= select_transport(
                    tuple(current_dest["gps"]), tuple(unvisited_dest["gps"]),problem.priority
                )
                if distance < min_dist:
                    min_dist = distance
                    min_time = time
                    current_dest = unvisited_dest

            if current_dest["category"] not in problem.categories:
                penalty += 1
            number_of_remaining_destination -= 1    
            if problem.priority == "cost":    
                total_cost += (
                    current_dest["entry_fee"]
                    + min_dist * 7.5 )
                total_time+= min_time
            else:
                total_cost += (
                    current_dest["entry_fee"]
                    + min_dist * 25 )
                total_time+= min_time
            

    
    normalized_time = total_time / 240  # assuming 4 hour max between locations
    normalized_cost = total_cost / (problem.budget / (7 / problem.dests_per_day))  # vs daily budget
    if problem.priority == "cost":  
        return normalized_cost
    else:  # time priority
        return normalized_time
    
    
