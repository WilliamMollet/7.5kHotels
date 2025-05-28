<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Filtres -->
    <div class="bg-white p-6 rounded-lg shadow-md mb-8">
      <div class="flex flex-wrap items-end gap-4">
        <!-- Filtre Ville -->
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-2">Ville</label>
          <select v-model="selectedCity" class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white">
            <option value="paris">Paris</option>
            <option value="london">London</option>
            <option value="berlin">Berlin</option>
            <option value="madrid">Madrid</option>
            <option value="rome">Rome</option>
          </select>
        </div>

        <!-- Filtre Type d'hébergement -->
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-2">Type d'hébergement</label>
          <select v-model="selectedType" class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white">
            <option value="airbnb">Airbnb</option>
            <option value="booking">Booking</option>
            <option value="hotelscom">Hotels.com</option>
          </select>
        </div>

        <!-- Filtre Prix Min -->
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-2">Prix minimum</label>
          <div class="relative">
            <input 
              type="number" 
              v-model="minPrice" 
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 pl-8 bg-white"
              placeholder="Min"
            >
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">€</span>
          </div>
        </div>

        <!-- Filtre Prix Max -->
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-2">Prix maximum</label>
          <div class="relative">
            <input 
              type="number" 
              v-model="maxPrice" 
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 pl-8 bg-white"
              placeholder="Max"
            >
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">€</span>
          </div>
        </div>

        <!-- Bouton Réinitialiser -->
        <button 
          @click="resetFilters"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors duration-200"
        >
          Réinitialiser
        </button>
      </div>
    </div>

    <!-- Message d'erreur -->
    <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
      <span class="block sm:inline">{{ error }}</span>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="flex justify-center items-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- Grille d'hôtels -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="hotel in hotels" :key="hotel.title" class="bg-white rounded-lg shadow-md overflow-hidden">
        <div class="relative h-48">
          <img 
            :src="hotel.thumbnail" 
            :alt="hotel.title" 
            class="w-full h-full object-cover"
          >
          <div class="absolute top-2 right-2 bg-blue-600 text-white px-2 py-1 rounded-md text-sm">
            {{ selectedType }}
          </div>
        </div>
        <div class="p-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ hotel.title }}</h3>
          <div class="flex items-center mb-2">
            <span class="text-yellow-400">★</span>
            <span class="text-gray-600 ml-1">{{ hotel.rating || 'N/A' }}</span>
          </div>
          <p class="text-gray-600 text-sm mb-4">{{ hotel.location || 'Centre-ville' }}, {{ selectedCity }}</p>
          <div class="flex justify-between items-center">
            <span class="text-lg font-bold text-blue-600">{{ hotel.price?.value || hotel.price }}€</span>
            <span class="text-sm text-gray-500">/nuit</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const selectedCity = ref('paris')
const selectedType = ref('airbnb')
const minPrice = ref('')
const maxPrice = ref('')
const hotels = ref([])
const loading = ref(false)
const error = ref(null)

const fetchHotels = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await fetch(`http://localhost:5000/${selectedCity.value}/${selectedType.value}`)
    if (!response.ok) throw new Error('Erreur lors de la récupération des hôtels')
    hotels.value = await response.json()
  } catch (e) {
    error.value = e.message
    console.error('Erreur:', e)
  } finally {
    loading.value = false
  }
}

// Charger les hôtels au montage du composant
onMounted(() => {
  fetchHotels()
})

const resetFilters = () => {
  selectedCity.value = 'paris'
  selectedType.value = 'airbnb'
  minPrice.value = ''
  maxPrice.value = ''
  fetchHotels()
}

// Les filtres sont réactifs et mettront à jour l'affichage automatiquement
watch([selectedCity, selectedType], () => {
  fetchHotels()
})
</script> 