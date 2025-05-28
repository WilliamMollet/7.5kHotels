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

    <!-- Grille d'hôtels -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Carte d'hôtel (exemple) -->
      <div v-for="i in 6" :key="i" class="bg-white rounded-lg shadow-md overflow-hidden">
        <div class="relative h-48">
          <img 
            src="https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80" 
            alt="Hotel" 
            class="w-full h-full object-cover"
          >
          <div class="absolute top-2 right-2 bg-blue-600 text-white px-2 py-1 rounded-md text-sm">
            {{ selectedType }}
          </div>
        </div>
        <div class="p-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Hôtel de Luxe</h3>
          <div class="flex items-center mb-2">
            <span class="text-yellow-400">★</span>
            <span class="text-gray-600 ml-1">4.8</span>
          </div>
          <p class="text-gray-600 text-sm mb-4">Centre-ville, {{ selectedCity }}</p>
          <div class="flex justify-between items-center">
            <span class="text-lg font-bold text-blue-600">150€</span>
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

const resetFilters = () => {
  selectedCity.value = 'paris'
  selectedType.value = 'airbnb'
  minPrice.value = ''
  maxPrice.value = ''
}

// Les filtres sont réactifs et mettront à jour l'affichage automatiquement
watch([selectedCity, selectedType, minPrice, maxPrice], () => {
  // Ici, vous pourrez ajouter la logique de filtrage quand vous connecterez l'API
  console.log('Filtres mis à jour:', {
    city: selectedCity.value,
    type: selectedType.value,
    minPrice: minPrice.value,
    maxPrice: maxPrice.value
  })
})
</script> 