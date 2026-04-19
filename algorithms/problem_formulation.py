import heapq # used in UCS
import math
from functools import lru_cache # To improve calculating the distance
from typing import List, Dict, Tuple, Optional
import random
import logging
logging.basicConfig(level=logging.DEBUG)
import json

# Class: State
# Represents the current status of a travel itinerary at any given time.
class State:
    def __init__(
        self,
        current_location,
        budget,
        day_plan=None,  # stores full destination/hotel dicts for current day
        itinerary=None, # list of completed day plans (list of lists)
        total_cost=0.0, # total money spent so far
        total_path_cost=0.0, # accumulated path cost for UCS
        transport_info=None,  # stores tuples (mode, cost, time) for each trip
        day=1,# current day number
        value=0
    ):
        self.current_location = current_location  # where we are right now
        self.budget = budget  # remaining money
        self.day_plan = day_plan  # today's plan
        self.itinerary = itinerary
        self.total_cost = total_cost  # sum of all expenses
        self.total_path_cost = total_path_cost  # UCS cumulative cost
        self.transport_info = transport_info if transport_info is not None else []
        self.day = day  # current day counter
        self.value=value
    def copy(self):
        """Create a deep copy of the state with all attributes in consistent order"""
        return State(
            current_location=self._deep_copy_location(self.current_location),
            budget=self.budget,
            day_plan=[self._deep_copy_location(loc) for loc in self.day_plan],
            itinerary=[[self._deep_copy_location(loc) for loc in day] for day in self.itinerary],
            total_cost=self.total_cost,
            total_path_cost=self.total_path_cost,
            transport_info=[(mode, cost, time) for mode, cost, time in self.transport_info],
            day=self.day
        )

    def _deep_copy_location(self, location):
        """Helper method to safely copy location dictionaries"""
        if not isinstance(location, dict):
            return location
        return {k: v for k, v in location.items()}

    def __eq__(self, other):
        """Check if two states are equal by comparing all attributes"""
        if not isinstance(other, State):
            return False
        return (
            self.current_location == other.current_location and
            self.day == other.day and
            self.day_plan == other.day_plan and
            self.itinerary == other.itinerary and
            self.total_cost == other.total_cost and
            self.budget == other.budget and
            self.transport_info == other.transport_info and 
            self.total_path_cost == other.total_path_cost
        )

    def __hash__(self):
        return hash((
            self.current_location.get('name', ''),
            self.day,
            tuple(loc.get('name', '') for loc in self.day_plan),
            frozenset(
                (loc.get('name', ''), trip[0], trip[1])  # (location_name, transport_mode, transport_cost)
                for day in self.itinerary
                for loc in day
                for trip in self.transport_info
            )
        ))

    def __str__(self):
        """User-friendly string representation of the state"""
        return (
            f"State:\n"
            f"  Current Location: {self.current_location}\n"
            f"  Budget: {self.budget}\n"
            f"  Day: {self.day}\n"
            f"  Day Plan: {self.day_plan}\n"
            f"  Itinerary: {self.itinerary}\n"
            f"  Total Cost: {self.total_cost}\n"
            f"  Total Path Cost: {self.total_path_cost}\n"
            f"  Transport (mode, cost,time) : {self.transport_info}\n"
        )
    
    def __lt__(self, other):
        """Tiebreaker for UCS when priorities are equal - use memory address"""
        return id(self) < id(other)


# Class: TourItineraryProblem
# Defines the travel planning problem and logic for generating states
class TourItineraryProblem:
    def __init__(
        self,
        search_strategy,
        current_location,
        destinations,
        categories,
        budget,
        dests_per_day,
        travel_history,
        hotels,
        hotel_stars,# (min , max)
        destination_hotel,
        priority  # "cost" or "time"
    ):
        """
        Initialize the travel planning problem with:
        - current_location: Starting point (dict with 'gps' and other info)
        - destinations: List of places to visit (each a dict)
        - categories: User's preferred destination types
        - budget: Total trip budget
        - dests_per_day: Max destinations per day
        - travel_history: Places already visited
        - hotels: List of available hotels
        - hotel_stars: Tuple of (min_stars, max_stars) user wants
        - destination_hotel: Mapping between destinations and nearby hotels
        - priority: Whether to optimize for "cost" or "time"
        """
        if budget <= 0:
            raise ValueError("Budget must be positive")
        if not (1 <= int(hotel_stars[0]) <= int(hotel_stars[1]) <= 5):
            raise ValueError("Invalid hotel star range")
        self.current_location = current_location
        self.search_strategy = search_strategy
        self.destinations = destinations or []
        self.hotels = hotels or []
        self.categories = categories
        self.budget = budget
        # Allow one extra spot for the hotel at end of day
        self.dests_per_day = dests_per_day + 1
        self.travel_history = travel_history
        self.hotel_stars = hotel_stars
        self.destination_hotel = destination_hotel
        self.priority = priority

    def initial_state(self):
        """Start the trip from the initial location with full budget"""
        return State(current_location=self.current_location, budget=self.budget, day_plan=[],itinerary=[])

    def possible_destinations(self, state):
        """
        Returns a list of possible next destinations based on the current state.
        Filters out places already visited and checks destination types.
        """
        possible = []

        # If the day has not started yet (no visits planned)
        if len(state.day_plan) == 0:
            for destination in self.destinations:
                if (
                    destination["name"] not in [loc["name"] for day in state.itinerary for loc in day]
                    and destination["name"] not in self.travel_history
                ):
                    possible.append(destination)
            return possible

        # if it is not empty
        # Determine the category of the last place visited 
        last_dest = state.day_plan[-1] 
        
        # we need to choose a hotel (end the day)
        if len(state.day_plan) == self.dests_per_day - 1 or last_dest["category"] in ["Beach", "Aquapark"]:
    
            # Find hotels linked to this destination
            linked_hotel_ids = {
                entry["hotel_id"] for entry in self.destination_hotel if entry["destination_id"] == last_dest["destination_id"]
            }

            for hid in linked_hotel_ids:
                for hotel in self.hotels:
                    if hotel["hotel_id"] == hid:
                        possible.append(hotel)
            return possible

        else:
            # Add more destinations (normal case)
            for destination in self.destinations:
                if (
                    destination["name"] not in [loc["name"] for day in state.itinerary for loc in day]
                    and destination["name"] not in [loc["name"] for loc in state.day_plan]  # Compare names
                    and destination["name"] not in self.travel_history
                    and destination["category"] not in ["Beach", "Aquapark"]
                ):
                    possible.append(destination)
            return possible
    
    def update_state(self, state, next_place, new_total_path_cost, transport_mode, transport_cost, transport_time): 
        """Create new state after moving to next location"""

        if not isinstance(next_place, dict):
            raise ValueError("next_place must be a dictionary")
        # Validate required fields based on place type
        if next_place.get("stars") is not None:  # Hotel case
            required_fields = ["hotel_id", "stars", "price_per_night"]
        else:  # Destination case
            required_fields = ["destination_id", "category", "entry_fee"]
        
        missing_fields = [field for field in required_fields if field not in next_place]
        if missing_fields:
            raise ValueError(f"Missing required fields in next_place: {missing_fields}")
        
        # we update the state attributes 
        new_total_cost = state.total_cost + transport_cost + next_place.get("entry_fee",0) + next_place.get("price_per_night",0)
        new_budget = state.budget - (next_place.get("entry_fee",0) + next_place.get("price_per_night",0) + transport_cost)
        new_transport_info = state.transport_info + [(transport_mode, transport_cost, transport_time)]
        new_itinerary = list(state.itinerary)

        # If next place is a hotel, end the day
        if next_place.get("stars") is not None:
            new_day_plan = state.day_plan + [next_place]
            new_itinerary.append(new_day_plan) 
            return State(
                current_location=next_place,
                day=state.day + 1,  # increment day
                day_plan=[],  # reset for new day
                itinerary=new_itinerary,
                total_cost=new_total_cost,
                total_path_cost=new_total_path_cost,
                budget=new_budget,
                transport_info=new_transport_info,
            )
        else:
            # Continue adding to current day
            new_day_plan = state.day_plan + [next_place]
            return State(
                current_location=next_place,
                day=state.day,  # same day
                day_plan=new_day_plan,
                itinerary=new_itinerary,
                total_cost=new_total_cost,
                total_path_cost=new_total_path_cost,
                budget=new_budget,
                transport_info=new_transport_info,
            )

    def goal_test(self, state):
        """Trip ends after 7 days"""
        return state.day > 7

    