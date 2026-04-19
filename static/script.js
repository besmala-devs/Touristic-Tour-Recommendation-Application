document.addEventListener("DOMContentLoaded", () => {
  // Set current year in footer
  document.getElementById("current-year").textContent = new Date().getFullYear()

  // Tab functionality
  setupTabs()

  // Form functionality
  setupFormHandlers()
})

// Tab functionality
function setupTabs() {
  const tabButtons = document.querySelectorAll(".tab-button")

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const tabName = button.getAttribute("data-tab")

      // Remove active class from all buttons and panes
      document.querySelectorAll(".tab-button").forEach((btn) => {
        btn.classList.remove("active")
      })

      document.querySelectorAll(".tab-pane").forEach((pane) => {
        pane.classList.remove("active")
      })

      // Add active class to clicked button and corresponding pane
      button.classList.add("active")

      const tabPane = document.getElementById(`${tabName}-tab`)
      if (tabPane) {
        tabPane.classList.add("active")
      }
    })
  })

  // Next and Previous tab buttons
  const nextTabButtons = document.querySelectorAll(".next-tab")
  nextTabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const nextTabName = button.getAttribute("data-next")
      const nextTabButton = document.querySelector(`.tab-button[data-tab="${nextTabName}"]`)

      if (nextTabButton) {
        // Validate before moving to next tab
        if (validateCurrentTab()) {
          nextTabButton.click()
        }
      }
    })
  })

  const prevTabButtons = document.querySelectorAll(".prev-tab")
  prevTabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const prevTabName = button.getAttribute("data-prev")
      const prevTabButton = document.querySelector(`.tab-button[data-tab="${prevTabName}"]`)

      if (prevTabButton) {
        prevTabButton.click()
      }
    })
  })
}

// Validate current tab
function validateCurrentTab() {
  const activeTab = document.querySelector(".tab-pane.active")

  if (activeTab.id === "preferences-tab") {
    // Check if at least 3 categories are selected
    const selectedCategories = document.querySelectorAll(".category-checkbox:checked")
    if (selectedCategories.length < 3) {
      showError("Please select at least 3 categories of attractions")
      return false
    }
  }

  return true
}

// Show error message
function showError(message) {
  const errorElement = document.getElementById("validation-error")
  const errorMessageElement = document.getElementById("error-message")

  if (errorElement && errorMessageElement) {
    errorMessageElement.textContent = message
    errorElement.classList.remove("hidden")

    // Auto hide after 5 seconds
    setTimeout(() => {
      errorElement.classList.add("hidden")
    }, 5000)
  }
}

// Form handlers
function setupFormHandlers() {
  // Get current location
  const getLocationBtn = document.getElementById("get-location-btn")
  if (getLocationBtn) {
    getLocationBtn.addEventListener("click", getCurrentLocation)
  }

  // Category checkboxes
  const categoryCheckboxes = document.querySelectorAll(".category-checkbox")
  if (categoryCheckboxes.length > 0) {
    categoryCheckboxes.forEach((checkbox) => {
      checkbox.addEventListener("change", updateCategoryStatus)
    })

    // Initial update
    updateCategoryStatus()
  }

  // Hotel stars inputs
  const minStarsInput = document.getElementById("min-stars")
  const maxStarsInput = document.getElementById("max-stars")

  if (minStarsInput && maxStarsInput) {
    minStarsInput.addEventListener("change", updateStarsDisplay)
    maxStarsInput.addEventListener("change", updateStarsDisplay)
  }

  // Destinations per day slider
  const destinationsSlider = document.getElementById("destinations-per-day")
  if (destinationsSlider) {
    destinationsSlider.addEventListener("input", updateDestinationsValue)
    // Initial update
    updateDestinationsValue()
  }

  // Algorithm options
  const algorithmOptions = document.querySelectorAll(".algorithm-option")
  if (algorithmOptions.length > 0) {
    algorithmOptions.forEach((option) => {
      option.addEventListener("click", () => {
        const radioInput = option.querySelector('input[type="radio"]')
        if (radioInput) {
          radioInput.checked = true
        }
      })
    })
  }

  // Search destinations
  const destinationSearch = document.getElementById("destination-search")
  if (destinationSearch) {
    destinationSearch.addEventListener("focus", showSearchResults)
    destinationSearch.addEventListener("input", filterSearchResults)
  }

  // Generate tour button
  const generateTourBtn = document.getElementById("generate-tour-btn")
  if (generateTourBtn) {
    generateTourBtn.addEventListener("click", generateTour)
  }
}

// Get current location
function getCurrentLocation() {
  const locationDisplay = document.getElementById("current-location-display")
  const locationCoordinates = document.getElementById("location-coordinates")
  const getLocationBtn = document.getElementById("get-location-btn")

  if (getLocationBtn) {
    getLocationBtn.textContent = "Getting Location..."
    getLocationBtn.disabled = true
  }

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude
        const lng = position.coords.longitude

        if (locationCoordinates) {
          locationCoordinates.textContent = `Coordinates: ${lat.toFixed(5)}, ${lng.toFixed(5)}`
        }

        if (locationDisplay) {
          locationDisplay.classList.remove("hidden")
        }

        if (getLocationBtn) {
          getLocationBtn.textContent = "Use Current Location"
          getLocationBtn.disabled = false
        }

        // Save to localStorage
        const locationData = {
          lat: lat,
          lng: lng,
          name: "GPS Location",
        }

        localStorage.setItem("currentLocation", JSON.stringify(locationData))
      },
      (error) => {
        showError("Could not get your location. Please try again or enter it manually.")
        console.error("Geolocation error:", error)

        if (getLocationBtn) {
          getLocationBtn.textContent = "Use Current Location"
          getLocationBtn.disabled = false
        }
      },
    )
  } else {
    showError("Geolocation is not supported by your browser.")

    if (getLocationBtn) {
      getLocationBtn.textContent = "Use Current Location"
      getLocationBtn.disabled = false
    }
  }
}

// Update category status
function updateCategoryStatus() {
  const selectedCategories = document.querySelectorAll(".category-checkbox:checked")
  const categoryBadge = document.getElementById("category-badge")
  const categoryMessage = document.getElementById("category-message")

  if (categoryBadge && categoryMessage) {
    const count = selectedCategories.length
    categoryBadge.textContent = `${count} / 3 selected`

    if (count >= 3) {
      categoryBadge.classList.remove("badge-error")
      categoryBadge.classList.add("badge-success")
      categoryMessage.textContent = "Minimum requirement met"
    } else {
      categoryBadge.classList.remove("badge-success")
      categoryBadge.classList.add("badge-error")
      categoryMessage.textContent = `Please select ${3 - count} more categories`
    }
  }
}

// Update stars display
function updateStarsDisplay() {
  const minStarsInput = document.getElementById("min-stars")
  const maxStarsInput = document.getElementById("max-stars")
  const minStarsDisplay = document.getElementById("min-stars-display")
  const maxStarsDisplay = document.getElementById("max-stars-display")

  if (minStarsInput && maxStarsInput && minStarsDisplay && maxStarsDisplay) {
    let minStars = Number.parseInt(minStarsInput.value)
    let maxStars = Number.parseInt(maxStarsInput.value)

    // Validate values
    if (minStars < 1) minStars = 1
    if (minStars > 5) minStars = 5
    if (maxStars < minStars) maxStars = minStars
    if (maxStars > 5) maxStars = 5

    // Update input values
    minStarsInput.value = minStars
    maxStarsInput.value = maxStars

    // Update star displays
    updateStarIcons(minStarsDisplay, minStars)
    updateStarIcons(maxStarsDisplay, maxStars)
  }
}

// Update star icons
function updateStarIcons(container, count) {
  if (container) {
    const stars = container.querySelectorAll("i")
    stars.forEach((star, index) => {
      if (index < count) {
        star.classList.remove("star-empty")
        star.classList.add("star-filled")
      } else {
        star.classList.remove("star-filled")
        star.classList.add("star-empty")
      }
    })
  }
}

// Update destinations value
function updateDestinationsValue() {
  const slider = document.getElementById("destinations-per-day")
  const valueDisplay = document.getElementById("destinations-value")

  if (slider && valueDisplay) {
    const value = slider.value
    valueDisplay.textContent = `${value} destination${value > 1 ? "s" : ""} per day`
  }
}


// Show search results
function showSearchResults() {
  const searchResults = document.getElementById("search-results")
  if (searchResults) {
    // Sample destinations data
    const destinations = [
      {id: "1", name: "Casbah of Algiers", region: "Algiers"},
      {id: "2", name: "Martyrs' Memorial", region: "Algiers"},
      {id: "3", name: "Bardo National Museum", region: "Algiers"},
      {id: "4", name: "Notre-Dame d’Afrique", region: "Algiers"},
      {id: "5", name: "El Hamma Botanical Garden", region: "Algiers"},
      {id: "6", name: "Tipaza Roman Ruins", region: "Tipaza"},
      {id: "7", name: "Royal Mausoleum of Mauretania", region: "Tipaza"},
      {id: "8", name: "Mount Chenoua", region: "Tipaza"},
      {id: "9", name: "Tipaza Beaches", region: "Tipaza"},
      {id: "10", name: "Chréa National Park", region: "Blida"},
      {id: "11", name: "Chréa Ski Resort", region: "Blida"},
      {id: "12", name: "Les Gorges De La Chiffa", region: "Blida"},
      {id: "13", name: "Ushuaia Beach Club", region: "Boumerdès"},
      {id: "14", name: "Corso Beach", region: "Boumerdès"},
      {id: "15", name: "Tibhirine Monastery", region: "Médéa"},
      {id: "16", name: "Hammam Righa", region: "Aïn Defla"},
      {id: "17", name: "Emir Abdelkader’s Home", region: "Aïn Defla"},
      {id: "18", name: "Musée Public National de Cherchell", region: "Tipaza"},
      {id: "19", name: "Al Rahman Mosque", region: "Tipaza"},
      {id: "20", name: "Promenade des Sablettes", region: "Algiers"},
      {id: "21", name: "Ketchaoua Mosque", region: "Algiers"},
      {id: "22", name: "Cirta Museum", region: "Constantine"},
      {id: "23", name: "Sidi M’Cid Bridge", region: "Constantine"},
      {id: "24", name: "Hippo Museum", region: "Annaba"},
      {id: "25", name: "Okacha Beach", region: "Annaba"},
      {id: "26", name: "Tizgban Forest", region: "Skikda"},
      {id: "27", name: "Marina d’Or", region: "Skikda"},
      {id: "28", name: "Les Grottes des Singes", region: "Jijel"},
      {id: "29", name: "Jijel-Zoo", region: "Jijel"},
      {id: "30", name: "Hammam Debagh Hot Springs", region: "Guelma"},
      {id: "31", name: "Roman Theater of Guelma", region: "Guelma"},
      {id: "32", name: "Thubursicum Ruins", region: "Souk Ahras"},
      {id: "33", name: "Beni Haroun Dam", region: "Mila"},
      {id: "34", name: "Emir Abdelkader Mosque", region: "Constantine"},
      {id: "35", name: "Viva Mall", region: "Annaba"},
      {id: "36", name: "Aftis Beach", region: "Jijel"},
      {id: "37", name: "Farouk Land Park", region: "Annaba"},
      {id: "38", name: "Qasr Bajouda", region: "Adrar"},
      {id: "39", name: "Assekrem Plateau", region: "Tamanrasset"},
      {id: "40", name: "Tahat Atakor", region: "Tamanrasset"},
      {id: "41", name: "Tassili N'Ajjer National Park", region: "Illizi"},
      {id: "42", name: "Tamantit Palace", region: "Adrar"},
      {id: "43", name: "Ahaggar National Park", region: "Tamanrasset"},
      {id: "44", name: "Oued Afilal", region: "Tamanrasset"},
      {id: "45", name: "Toboggan Aqua Park", region: "Ghardaia"},
      {id: "46", name: "Takimit n Imdochal", region: "Ghardaia"},
      {id: "47", name: "Tin Merzouga Dunes", region: "Tamanrasset"},
      {id: "48", name: "Tin Akachaker", region: "Tamanrasset"},
      {id: "49", name: "Kawthar mosque", region: "El Oued"},
      {id: "50", name: "Gouri park", region: "El Oued"},
      {id: "51", name: "the Oasis of El Oued", region: "El Oued"},
      {id: "52", name: "Moutain Peak (pic des singes)", region: "Bejaia"},
      {id: "53", name: "Gouraya national park", region: "Bejaia"},
      {id: "54", name: "Casbah of Bejaia", region: "Bejaia"},
      {id: "55", name: "Cap Carbon", region: "Bejaia"},
      {id: "56", name: "Bab El Fouka", region: "Bejaia"},
      {id: "57", name: "Bordj El Mokrani", region: "Bourdj"},
      {id: "58", name: "Tikjda national park", region: "Bouira"},
      {id: "59", name: "El Moudjahid museum", region: "Bejaia"},
      {id: "60", name: "La plage rouge", region: "Jijel"},
      {id: "61", name: "Razan Mall", region: "Tamanrasset"},
      {id: "62", name: "Waterfall Kerfida", region: "Bejaia"},
      {id: "63", name: "Place Gueydon", region: "Bejaia"},
      {id: "64", name: "Zawiat sidi Ahsen", region: "Setif"},
      {id: "65", name: "Parc d'attraction et loisirs", region: "Setif"},
      {id: "66", name: "Oued El Barad", region: "Setif"},
      {id: "67", name: "El elma Dubai rue", region: "Setif"},
      {id: "68", name: "Djemila", region: "Setif"},
      {id: "69", name: "Park Mall", region: "Setif"},
      {id: "70", name: "Lompi Park", region: "Batna"},
      {id: "71", name: "Hammam Salhine", region: "Khanchla"},
      {id: "72", name: "Dream paradise park Oran", region: "Oran"},
      {id: "73", name: "Temple Minarf", region: "Tbessa"},
      {id: "74", name: "Lalla Setti Park", region: "Tlemcen"},
      {id: "75", name: "The Remains of Mansourah", region: "Tlemcen"},
      {id: "76", name: "The Cave of Beni Add", region: "Tlemcen"},
      {id: "77", name: "Great Mosque of Tlemcen", region: "Tlemcen"},
      {id: "78", name: "El Ourit Waterfalls", region: "Tlemcen"},
      {id: "79", name: "Marsa BenM'hidi Beach", region: "Tlemcen"},
      {id: "80", name: "Aquapark Rechgoune", region: "Ain Temouchent"},
      {id: "81", name: "EL Bir Beach", region: "Ain Temouchent"},
      {id: "82", name: "Rechgoune Beach", region: "Ain Temouchent"},
      {id: "83", name: "Doriane Beach Club", region: "Ain Temouchent"},
      {id: "84", name: "The Guitar Beach", region: "Ain Temouchent"},
      {id: "85", name: "Sidi Mohamed Lake", region: "Sidi Bel Abbes"},
      {id: "86", name: "Loumi Castle", region: "Sidi Bel Abbes"},
      {id: "87", name: "Santa Cruz", region: "Oran"},
      {id: "88", name: "Ahmed Zabana National Museum", region: "Oran"},
      {id: "89", name: "Ibn Badis Mosque", region: "Oran"},
      {id: "90", name: "The Andalusians", region: "Oran"},
      {id: "91", name: "AZ Grand Oran", region: "Oran"},
      {id: "92", name: "Cap Ivi Beach", region: "Mostaganem"},
      {id: "93", name: "Mostaland Park", region: "Mostaganem"},
      {id: "94", name: "EL Asra Parc", region: "Mostaganem"},
      {id: "95", name: "Amusment Park", region: "Ain Salah"},
      {id: "96", name: "The Ancient Palace of the Sons of Ali Ibn Musa", region: "Adrar"},
      {id: "97", name: "Ksar Beni Isguen", region: "Ghardaia"},
      {id: "98", name: "Fort Polignac", region: "Illizi"},
      {id: "99", name: "Ksar El Mihan", region: "Illizi"},
      {id: "100", name: "PLACE DE 1 NOVEMBRE", region: "Oran"},
      {id: "101", name: "ES-SENIA", region: "Oran"},
      {id: "102", name: "Aqua Souf Water Park", region: "El Qued"},
      {id: "103", name: "Museum of Dar El Baroud (Museum of Idols)", region: "Chelf"}      
    ]


    // Clear previous results
    searchResults.innerHTML = ""

    // Create result items
    destinations.forEach((destination) => {
      const item = document.createElement("div")
      item.className = "search-result-item"
      item.innerHTML = `
        <span>${destination.name}</span>
        <span class="badge">${destination.region}</span>
      `

      item.addEventListener("click", () => {
        selectDestination(destination)
        searchResults.classList.add("hidden")
      })

      searchResults.appendChild(item)
    })

    searchResults.classList.remove("hidden")
  }
}




// Filter search results
function filterSearchResults() {
  const searchInput = document.getElementById("destination-search")
  const searchResults = document.getElementById("search-results")

  if (searchInput && searchResults) {
    const query = searchInput.value.toLowerCase()
    const resultItems = searchResults.querySelectorAll(".search-result-item")

    resultItems.forEach((item) => {
      const destinationName = item.querySelector("span").textContent.toLowerCase()
      const destinationRegion = item.querySelector(".badge").textContent.toLowerCase()

      if (destinationName.includes(query) || destinationRegion.includes(query)) {
        item.style.display = "flex"
      } else {
        item.style.display = "none"
      }
    })
  }
}



// Select destination
function selectDestination(destination) {
  const selectedContainer = document.getElementById("selected-destinations")
  const selectedDestinationsContainer = document.getElementById("selected-destinations-container")

  if (selectedContainer && selectedDestinationsContainer) {
    // Check if already selected
    const existingDestination = selectedContainer.querySelector(`[data-id="${destination.id}"]`)
    if (existingDestination) return

    // Create badge
    const badge = document.createElement("div")
    badge.className = "badge-c"
    badge.setAttribute("data-id", destination.id)
    badge.innerHTML = `
      ${destination.name}
      <button type="button" class="btn-close">
        <i class="fas fa-times"></i>
      </button>
    `

    // Add remove functionality
    const removeButton = badge.querySelector(".btn-close")
    removeButton.addEventListener("click", (e) => {
      e.stopPropagation()
      badge.remove()

      // Hide container if empty
      if (selectedContainer.children.length === 0) {
        selectedDestinationsContainer.classList.add("hidden")
      }

      // Update localStorage
      updateSelectedDestinations()
    })

    // Add to container
    selectedContainer.appendChild(badge)
    selectedDestinationsContainer.classList.remove("hidden")

    // Update localStorage
    updateSelectedDestinations()
  }
}

// Update selected destinations in localStorage
function updateSelectedDestinations() {
  const selectedContainer = document.getElementById("selected-destinations")

  if (selectedContainer) {
    const badges = selectedContainer.querySelectorAll(".badge-c")
    const destinations = []

    badges.forEach((badge) => {
      destinations.push({
        id: badge.getAttribute("data-id"),
        name: badge.textContent.trim(),
      })
    })

    localStorage.setItem("selectedDestinations", JSON.stringify(destinations))
  }
}