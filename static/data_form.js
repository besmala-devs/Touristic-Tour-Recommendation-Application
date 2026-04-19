document.addEventListener("DOMContentLoaded", () => {
  // Tour page functionality
  if (window.location.pathname.includes("/tour")) {
    setupTourPage()
  }
})


// Generate tour
function generateTour() {
    document.getElementById('generate-tour-btn').innerHTML = "Generating...";
    // Validate form
    if (!validateCurrentTab()) return

    // Collect form data
    const locationObj = JSON.parse(localStorage.getItem("currentLocation") || "{}");
    const formData = {
        currentLocation: [locationObj.lat, locationObj.lng],
        selectedDestinations: JSON.parse(localStorage.getItem("selectedDestinations") || "[]"),
        preferences: {
            categories: getSelectedCategories(),
            budget: document.getElementById("total-budget").value,
            hotelStars: {
                min: document.getElementById("min-stars").value,
                max: document.getElementById("max-stars").value,
            },
            priority: document.querySelector('input[name="priority"]:checked').value,
            algorithm: document.querySelector('input[name="algorithm"]:checked').value,
            destinationsPerDay: document.getElementById("destinations-per-day").value,
        },
    }
    
    // Save to localStorage
    localStorage.setItem("tourPreferences", JSON.stringify(formData))

    // Send data to Flask using fetch (AJAX)
    fetch('http://127.0.0.1:5000/generate_tour', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData), // Convert formData to JSON
    })
    .then(response => response.json()) // Parse the JSON response from Flask
    .then(data => {
        console.log("Response from Flask:", data);
        localStorage.setItem("tourismResult", JSON.stringify(data))

        document.getElementById('generate-tour-btn').innerHTML = 'Generate Tour <i class="fas fa-chevron-right"></i>';
        // Redirect to tour page
        window.location.href = "/tour"
    })
    .catch(error => console.error("Error sending data to Flask:", error));
    document.getElementById('generate-tour-btn').innerHTML = 'Generate Tour <i class="fas fa-chevron-right"></i>';
}

// Get selected categories
function getSelectedCategories() {
    const checkboxes = document.querySelectorAll(".category-checkbox:checked")
    const categories = []

    checkboxes.forEach((checkbox) => {
        categories.push(checkbox.value)
    })

    return categories
}


// Tour page functionality
function setupTourPage() {
    // Load preferences
    const preferences = JSON.parse(localStorage.getItem("tourPreferences") || "{}")

    if (Object.keys(preferences).length > 0) {
        displayPreferencesSummary(preferences)
    }

    // Setup day view buttons
    const viewDayButtons = document.querySelectorAll(".view-day-btn")
    viewDayButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const dayNumber = button.getAttribute("data-day")
            const dayTab = document.querySelector(`.tab-button[data-tab="day-${dayNumber}"]`)

            if (dayTab) {
                dayTab.click()
            }
        })
    })

    // Clear preferences button
    const clearPreferencesBtn = document.getElementById("clear-preferences-btn")
    if (clearPreferencesBtn) {
        clearPreferencesBtn.addEventListener("click", () => {
            localStorage.removeItem("tourPreferences")
            window.location.href = "/"
        })
    }
}




// Display preferences summary
function displayPreferencesSummary(preferences) {
    const preferencesContainer = document.getElementById("preferences-summary")
    const badgesContainer = document.getElementById("preferences-badges")

    if (preferencesContainer && badgesContainer) {
        // Clear previous badges
        badgesContainer.innerHTML = ""

        // Current location
        start = JSON.parse(localStorage.getItem("currentLocation") || "{}");
        if (start) {
            addBadge(badgesContainer, "location-arrow", `Starting from: ${[start.lat, start.lng]}`)
        }

        // Selected destinations
        const tourPreferences = JSON.parse(localStorage.getItem("tourPreferences"));
        if (tourPreferences && tourPreferences.preferences.destinationsPerDay) {
            addBadge(badgesContainer, "map-marker-alt", `${tourPreferences.preferences.destinationsPerDay} destinations per day`)
        }

        // Categories
        if (preferences.preferences && preferences.preferences.categories) {
            addBadge(badgesContainer, "compass", `${preferences.preferences.categories.length} categories selected`)
        }

        // Hotel stars
        if (preferences.preferences && preferences.preferences.hotelStars) {
            addBadge(
                badgesContainer,
                "star",
                `${preferences.preferences.hotelStars.min}-${preferences.preferences.hotelStars.max} star hotels`,
            )
        }

        // Priority
        if (preferences.preferences && preferences.preferences.priority) {
            const priorityText = preferences.preferences.priority === "time" ? "Speed" : "Lower cost"
            addBadge(badgesContainer, "clock", `Priority: ${priorityText}`)
        }

        // Algorithm
        if (preferences.preferences && preferences.preferences.algorithm) {
            addBadge(badgesContainer, "microchip", `Algorithm: ${preferences.preferences.algorithm.toUpperCase()}`)
        }

        // Show container
        preferencesContainer.classList.remove("hidden")
    }
}

// Add badge to container
function addBadge(container, icon, text) {
    const badge = document.createElement("div")
    badge.className = "badge"
    badge.innerHTML = `<i class="fas fa-${icon}"></i> ${text}`
    container.appendChild(badge)
}