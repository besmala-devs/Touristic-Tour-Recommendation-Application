tourData = JSON.parse(localStorage.getItem("tourismResult") || "{}")
tourpreferences = JSON.parse(localStorage.getItem("tourPreferences"))
console.log("Tour Data: ");
console.log(tourData);
console.log("Tour preferences:");
console.log(tourpreferences);

const Data = tourData.data;
const bar_percentage_transport = Data.travel_cost / Data.total_cost * 100;
const bar_percentage_hotels = Data.accommodation_cost / Data.total_cost * 100;
const bar_percentage_entryFees = Data.entry_fees / Data.total_cost * 100;
document.getElementById('cost-amount').textContent = `${Math.round(Data.total_cost)} DZD`
document.getElementById('transport-cost').textContent = `${Data.travel_cost} DZD`
document.getElementById('accommodation-cost').textContent = `${Data.accommodation_cost} DZD`
document.getElementById('entry-cost').textContent = `${Data.entry_fees} DZD`

document.querySelector('.progress-transport').style.width = `${bar_percentage_transport}%`;
document.querySelector('.progress-hotels').style.width = `${bar_percentage_hotels}%`;
document.querySelector('.progress-fees').style.width = `${bar_percentage_entryFees}%`;


function attraction_card(number, attraction_name, region, description, entry_fee, rating, image_path='https://static.vecteezy.com/system/resources/previews/049/855/259/non_2x/nature-background-high-resolution-wallpaper-for-a-serene-and-stunning-view-photo.jpg') {
    return `<div class="activity-card">
    <div class="activity-image"
    style="background-image: url(${image_path})">
    <div class="activity-badge">Attraction</div>
    <h3 class="activity-title">${attraction_name}, ${region}</h3>
    </div>
    <div class="activity-content">
    <div class="activity-number-badge">${number}</div>
    <div class="activity-details">
      <p class="activity-description">
        ${description}
      </p>
      <div class="activity-meta">
        <div class="activity-meta-item">
          <i class="fas fa-dollar-sign"></i>
          <span>${entry_fee} DZD</span>
        </div>
        <div class="activity-meta-item">
          <i class="fas fa-star" style="color: rgb(255, 217, 0);"></i>
          <span>${rating}</span>
          <span class="review-count">(128 reviews)</span>
        </div>
      </div>
    </div>
    </div>
    </div>`
}



function transport_card_same_day(mode, cost, time) {
    if(mode == 'taxi') {
        transport_icon = '<i class="fas fa-taxi"></i>';
    }
    else if(mode == 'plane') {
        transport_icon = '<i class="fas fa-plane"></i>';
    }
    else if(mode == 'bus') {
        transport_icon = '<i class="fas fa-bus"></i>';
    }
    else {
        transport_icon = '<i class="fas fa-walking"></i>';
    }

    return `
        <div class="transportation-section">
  <div class="transportation-arrow">
    <i class="fas fa-arrow-down"></i>
    <span>Transportation to Next Destination</span>
  </div>

  <div class="transportation-card">
    <div class="card-header">
      <h4 class="card-title">
        <i class="fas fa-taxi"></i> Local Transportation
      </h4>
      <button class="btn btn-ghost btn-sm edit-transport-btn">
        <i class="fas fa-edit"></i> Edit
      </button>
    </div>
    <div class="card-content">
      <div class="transport-route">
        <div class="transport-from-to">
          <span class="font-medium">Details</span> to
          <span class="font-medium">Welcome Meeting</span>
        </div>
        <div class="transport-badge">
          ${transport_icon} ${mode}
        </div>
      </div>
      <div class="transport-details">
        <div class="transport-detail">
          <i class="fas fa-clock"></i>
          <span>~${time} min</span>
        </div>
        <div class="transport-detail">
          <i class="fas fa-dollar-sign"></i>
          <span>~${cost} DZD</span>
        </div>
        <div class="transport-detail">
          <i class="fas fa-calendar"></i>
          <span>High Availability</span>
        </div>
      </div>
    </div>
    </div>
    </div>`;
}



function hotel_card(hotel_name, stars, region, price_per_night=5000) {
  let stars_section = '';
  for(let i=1; i<=Math.floor(stars); i++) {
    stars_section += '<i class="fas fa-star" style="color: rgb(255, 217, 0);"></i>';
  }
  for(let i=1; i<=5-Math.floor(stars); i++) {
    stars_section += '<i class="fas fa-star"></i>';
  }

    return `
        <div class="accommodation-card">
  <div class="card-header">
    <h3 class="card-title">
      <i class="fas fa-bed"></i> Accommodation for tonight
    </h3>
  </div>
  <div class="card-content">
    <div class="accommodation-details">
      <div class="accommodation-name">${hotel_name}</div>
      <div class="accommodation-stars">
        ${stars_section}
        <span class="stars-text">(${Math.floor(stars)}-star hotel)</span>
      </div>
      <div style="margin-top: 20px; font-weight: bold;">
        <div style="color: blue">Price per night:</div>
        <div>${price_per_night} DZD</div>
      </div>
      <button class="btn btn-outline btn-sm">
        <i class="fas fa-location-arrow"></i> ${region}
      </button>
    </div>
    </div>
    </div>
    `;
}



function transport_card_next_day(start_des, next_des, duration, cost, distance, mode, day) {
    if(mode == 'plane') {
        speed = '550-650';
        transport_icon = '<i class="fas fa-plane" style="color: black;"></i>';
    }
    else if(mode == 'taxi') {
        speed = '80-120';
        transport_icon = '<i class="fas fa-taxi" style="color: black;"></i>';
    }
    else if(mode == 'bus') {
        speed = '70-100';
        transport_icon = '<i class="fas fa-bus" style="color: black;"></i>';
    }
    else {
        speed = 5;
        transport_icon = '<i class="fas fa-walking" style="color: black;"></i>';
    }

    return `
        <div class="next-day-transport-card">
  <div class="card-header">
    <h3 class="card-title" style="color: blue;">
      <i class="fas fa-car"></i> Transportation: Day ${day} to Day ${day+1}
    </h3>
    <button class="btn btn-ghost btn-sm">
      ${transport_icon} ${mode}
    </button>
  </div>
  <div class="card-content">
    <div class="transport-route-large">
      <div class="transport-from">
        <div class="transport-label">From</div>
        <div class="transport-location">${start_des}</div>
      </div>
      <div class="transport-separator">
        <div class="separator-line"></div>
        ${transport_icon}
        <div class="separator-line"></div>
      </div>
      <div class="transport-to">
        <div class="transport-label">To</div>
        <div class="transport-location">${next_des}</div>
      </div>
    </div>

    <div class="transport-details-grid">
      <div class="transport-detail-item">
        <div class="detail-label">
          <i class="fas fa-clock"></i> Duration
        </div>
        <div class="detail-value">~${duration} min</div>
        <div class="detail-subtext">${distance} km at ${speed} km/h</div>
      </div>

      <div class="transport-detail-item">
        <div class="detail-label">
          <i class="fas fa-dollar-sign"></i> Cost
        </div>
        <div class="detail-value">${cost} DZD</div>
        <div class="detail-subtext">Per person, one way</div>
      </div>

      <div class="transport-detail-item">
        <div class="detail-label">
          <i class="fas fa-calendar"></i> Availability
        </div>
        <div class="detail-value">
          <span class="badge badge-success">High</span>
        </div>
        <div class="detail-subtext">Multiple daily departures</div>
      </div>
    </div>
    </div>
    </div>
    `;
}



function transport_from_start_location(mode, next_des, duration, distance, cost) {
  if(mode == 'plane') {
        speed = '550-650';
        transport_icon = '<i class="fas fa-plane" style="color: black;"></i>';
    }
    else if(mode == 'taxi') {
        speed = '80-120';
        transport_icon = '<i class="fas fa-taxi" style="color: black;"></i>';
    }
    else if(mode == 'bus') {
        speed = '70-100';
        transport_icon = '<i class="fas fa-bus" style="color: black;"></i>';
    }
    else {
        speed = 5;
        transport_icon = '<i class="fas fa-walking" style="color: black;"></i>';
    }

  return `
        <div class="next-day-transport-card">
  <div class="card-header">
    <h3 class="card-title" style="color: blue;">
      <i class="fas fa-car"></i> Transportation: To start the trip
    </h3>
    <button class="btn btn-ghost btn-sm">
      ${transport_icon} ${mode}
    </button>
  </div>
  <div class="card-content">
    <div class="transport-route-large">
      <div class="transport-from">
        <div class="transport-label">From</div>
        <div class="transport-location">Current location</div>
      </div>
      <div class="transport-separator">
        <div class="separator-line"></div>
        ${transport_icon}
        <div class="separator-line"></div>
      </div>
      <div class="transport-to">
        <div class="transport-label">To</div>
        <div class="transport-location">${next_des}</div>
      </div>
    </div>

    <div class="transport-details-grid">
      <div class="transport-detail-item">
        <div class="detail-label">
          <i class="fas fa-clock"></i> Duration
        </div>
        <div class="detail-value">~${duration} min</div>
        <div class="detail-subtext">${distance} km at ${speed} km/h</div>
      </div>

      <div class="transport-detail-item">
        <div class="detail-label">
          <i class="fas fa-dollar-sign"></i> Cost
        </div>
        <div class="detail-value">${cost} DZD</div>
        <div class="detail-subtext">Per person, one way</div>
      </div>

      <div class="transport-detail-item">
        <div class="detail-label">
          <i class="fas fa-calendar"></i> Availability
        </div>
        <div class="detail-value">
          <span class="badge badge-success">High</span>
        </div>
        <div class="detail-subtext">Multiple daily departures</div>
      </div>
    </div>
    </div>
    </div>
    `;
}



function add_restaurant(restaurant) {
  restaurant_name = restaurant.name;
  price = restaurant.price_per_meal;
  return `
  <div class="restaurant-card">
  <div class="card-header">
    <h3 class="card-title">
      <i class="fas fa-utensils"></i> Nearby Restaurant
    </h3>
  </div>
  <div class="card-content">
    <div class="restaurant-details">
      <div class="restaurant-name">${restaurant_name}</div>
      <div style="margin-top: 20px; font-weight: bold;">
        <div style="color: blue">Average price per meal:</div>
        <div>${price} DZD</div>
      </div>
    </div>
    </div>
    </div>
    `;
}



let tour = tourData.data
document.addEventListener("DOMContentLoaded", function () {
    if (!tour.itinerary) return;
    
    tour.itinerary.forEach((dayAttractions, dayIndex) => {
        // Skip if there are no attractions or only one (which would be the hotel)
        if (dayAttractions.length < 2) return;

        if(dayIndex == 0) {
          const transport_day_to_day = tour.partial_details[dayIndex][0];
          next_dest = tour.itinerary[dayIndex][0].name + ", " + tour.itinerary[dayIndex][0].region;
          distance = transport_day_to_day[0];
          time = transport_day_to_day[1];
          cost = transport_day_to_day[2];
          transport = transport_day_to_day[3];
          //mode, next_des, duration, distance, cost
          const transport_from_start = transport_from_start_location(transport, next_dest, time, distance, cost);
          document.getElementById(`activities-section${dayIndex + 1}`).innerHTML += transport_from_start;
        }

        // Determine the correct section ID (activities-section for day 1, then activities-section2, etc.)
        const sectionId = `activities-section${dayIndex + 1}`;
        const container = document.getElementById(sectionId);
        const day_container = document.getElementById(`day-itinerary-${dayIndex+1}`);

        // Sanity check for container existence
        if (!container) return;

        // Iterate all attractions except the last one (hotel)
        for (let i = 0; i < dayAttractions.length - 1; i++) {
            const attraction = dayAttractions[i];
            const cardHTML = attraction_card(
                i+1,
                attraction.name,
                attraction.region,
                attraction.description,
                attraction.entry_fee,
                attraction.rating,
                '/static' + attraction.picture
            );
            container.innerHTML += cardHTML;


            const dayRestaurants = tour.nearby_restaurants[dayIndex];
            if (dayRestaurants && dayRestaurants[i]) {
              const nearby_restaurant = dayRestaurants[i];
              container.innerHTML += add_restaurant(nearby_restaurant);
            }


            //distance, time, cost, transport
            destination_travel_details = tour.partial_details[dayIndex][i+1];
            distance = destination_travel_details[0];
            time = destination_travel_details[1];
            cost = destination_travel_details[2];
            transport = destination_travel_details[3];

            const transport_card = transport_card_same_day(transport, cost, time);
            container.innerHTML += transport_card;
        }
        
        const hotel = dayAttractions[dayAttractions.length - 1];
        const hotelcard = hotel_card(
            hotel.name,
            hotel.stars,
            hotel.region,
            hotel.price_per_night
        );
        day_container.innerHTML += hotelcard;

        if (dayIndex+1 <= 6) {
        const transport_day_to_day = tour.partial_details[dayIndex + 1][0];
        dest1 = dayAttractions[dayAttractions.length - 1].name + ", " + dayAttractions[dayAttractions.length - 1].region;
        dest2 = tour.itinerary[dayIndex+1][0].name + ", " + tour.itinerary[dayIndex+1][0].region;
        distance = transport_day_to_day[0];
        time = transport_day_to_day[1];
        cost = transport_day_to_day[2];
        transport = transport_day_to_day[3];
        //start_des, next_des, duration, cost, distance, mode
        const transport_to_nextDay = transport_card_next_day(dest1, dest2, time, cost, distance, transport, dayIndex+1);
        day_container.innerHTML += transport_to_nextDay;
        }
    });
});



document.addEventListener('DOMContentLoaded', function () {
  const itinerary = tour.itinerary;
  let regions_list = [];

  for (let i = 0; i < itinerary.length; i++) {
    let dayRegions = new Set(); // use Set to avoid duplicates
    for (let j = 0; j < itinerary[i].length - 1; j++) {
      const destination = itinerary[i][j];
      dayRegions.add(destination.region); // add region to the Set
    }
    regions_list.push(Array.from(dayRegions)); // convert Set to array and store it
  }

  const day_contents = document.querySelectorAll('.day-card-content .day-title');
  day_contents.forEach((element, index) => {
    const day_regions = regions_list[index];
    element.textContent = "";
    element.textContent += day_regions[0];
    for(let i=1; i<day_regions.length; i++) {
      element.textContent += " & " + day_regions[i];
    }
  });
});
