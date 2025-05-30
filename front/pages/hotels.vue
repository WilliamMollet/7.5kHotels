<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Filtres -->
    <div class="bg-white p-6 rounded-lg shadow-md mb-8">
      <div class="flex flex-wrap items-end gap-4">
        <!-- Filtre Ville -->
        <div class="flex-1 min-w-[200px]" :hidden="cityLocked">
          <label class="block text-sm font-medium text-gray-700 mb-2">Ville</label>
          <select v-model="selectedCity" class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white">
            <option value="toutes">Toutes</option>
            <option value="paris">Paris</option>
            <option value="london">London</option>
            <option value="berlin">Berlin</option>
            <option value="madrid">Madrid</option>
            <option value="rome">Rome</option>
          </select>
        </div>

        <!-- Filtre Source d'hébergement -->
        <div class="flex-1 min-w-[200px]" :hidden="sourceLocked">
          <label class="block text-sm font-medium text-gray-700 mb-2">Source de l'hébergement</label>
          <select v-model="selectedSource" class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white">
            <option value="toutes">Toutes</option>
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
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-2">Titre de la chambre</label>
          <input
            type="text"
            v-model="title"
            placeholder="Rechercher un titre..."
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white"
          >
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
      <div 
        v-for="hotel in hotels" 
        :key="hotel.title" 
        class="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
        @click="goToHotelDetails(hotel)"
      >
        <div class="relative h-48">
          <img 
            :src="hotel.thumbnail || '/images/No_image_available.svg.png'" 
            :alt="hotel.title" 
            class="w-full h-full object-cover"
          >
          <div class="absolute top-2 right-2 bg-blue-600 text-white px-2 py-1 rounded-md text-sm">
            {{ selectedSource }}
          </div>
        </div>
        <div class="p-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ hotel.title }}</h3>
          <div class="flex items-center mb-2">
            <span class="text-yellow-400">★</span>
            <span class="text-gray-600 ml-1">
              <template v-if="SelectedSource === 'airbnb'">
                {{ hotel.unified_rating || 'N/A' }}
              </template>
              <template v-else-if="SelectedSource === 'booking'">
                {{ hotel.unified_rating?.score || 'N/A' }}
              </template>
              <template v-else>
                {{ hotel.unified_rating || 'N/A' }}
              </template>
            </span>
          </div>
          <p class="text-gray-600 text-sm mb-4">
            <template v-if="SelectedSource === 'airbnb'">
              {{ hotel.subtitles?.[0] || 'Centre-ville' }}, {{ hotel.city }}
            </template>
            <template v-else>
              {{ hotel.location || 'Centre-ville' }}, {{ hotel.city }}
            </template>
          </p>
          <div class="flex justify-between items-center">
            <span class="text-lg font-bold text-blue-600">
              <template v-if="SelectedSource === 'airbnb'">
                {{ hotel.unified_price?.value || hotel.unified_price }}€
              </template>
              <template v-else-if="SelectedSource === 'booking'">
                {{ hotel.unified_price?.value || hotel.unified_price }}€
              </template>
              <template v-else>
                {{ hotel.unified_price?.value || hotel.unified_price }}€
              </template>
            </span>
            <span class="text-sm text-gray-500">/nuit</span>
          </div>
          <!-- Badges pour Booking -->
          <div v-if="SelectedSource === 'booking'" class="mt-2 flex flex-wrap gap-2">
            <span v-if="hotel.preferredBadge" class="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">Préféré</span>
            <span v-if="hotel.promotedBadge" class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Promu</span>
            <span v-if="hotel.sustainability" class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Écologique</span>
          </div>
          <!-- Highlights pour Booking -->
          <div v-if="SelectedSource === 'booking' && hotel.highlights" class="mt-2">
            <ul class="text-xs text-gray-600 space-y-1">
              <li v-for="(highlight, index) in hotel.highlights.slice(0, 2)" :key="index">
                {{ highlight }}
              </li>
            </ul>
          </div>
          <!-- Snippet pour Hotels.com -->
          <div v-if="SelectedSource === 'hotelscom' && hotel.snippet" class="mt-2">
            <p class="text-xs text-gray-600">{{ hotel.snippet.text }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div class="flex justify-center mt-6 space-x-2">
      <button
        :disabled="currentPage === 1"
        @click="currentPage-- && fetchHotels()"
        class="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
      >
        Précédent
      </button>
      <span class="px-4 py-2 bg-gray-100 text-gray-800 rounded">
        Page {{ currentPage }} / {{ Math.ceil(totalResults / pageSize) }}
      </span>
      <button
        :disabled="currentPage >= Math.ceil(totalResults / pageSize)"
        @click="currentPage++ && fetchHotels()"
        class="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
      >
        Suivant
      </button>
    </div>

    <!-- Modal de détails de l'hôtel -->
    <div v-if="selectedHotel" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white w-full h-screen overflow-y-auto">
        <!-- En-tête avec image -->
        <div class="relative h-[50vh]">
          <img 
            :src="selectedHotel.thumbnail" 
            :alt="selectedHotel.title" 
            class="w-full h-full object-cover"
          >
          <div class="absolute top-4 right-4 flex gap-2">
            <button 
              @click="startEdit" 
              class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Éditer
            </button>
            <button 
              @click="showDeleteConfirm = true" 
              class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
            >
              Supprimer
            </button>
            <button 
              @click="closeModal" 
              class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
            >
              Fermer
            </button>
          </div>
        </div>

        <!-- Contenu -->
        <div class="p-12 max-w-7xl mx-auto">
          <div class="flex justify-between items-start mb-8">
            <h1 class="text-5xl font-bold text-gray-900">{{ selectedHotel.title }}</h1>
            <a 
              :href="selectedHotel.link" 
              target="_blank" 
              class="inline-flex items-center gap-2 bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition-colors text-lg"
            >
              <span>Voir sur {{ SelectedSource }}</span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
              </svg>
            </a>
          </div>
          
          <!-- Informations principales -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-16 mb-12">
            <div>
              <h2 class="text-3xl font-semibold mb-8">Informations</h2>
              <div class="space-y-8">
                <div class="flex items-center">
                  <span class="text-yellow-400 text-3xl mr-4">★</span>
                  <span class="text-gray-600 text-2xl">
                    <template v-if="SelectedSource === 'airbnb'">
                      {{ selectedHotel.unified_rating || 'N/A' }}
                    </template>
                    <template v-else-if="SelectedSource === 'booking'">
                      {{ selectedHotel.unified_rating?.score || 'N/A' }}
                    </template>
                    <template v-else>
                      {{ selectedHotel.unified_rating || 'N/A' }}
                    </template>
                  </span>
                </div>
                <div class="text-gray-600 text-2xl">
                  <template v-if="SelectedSource === 'airbnb'">
                    {{ selectedHotel.subtitles?.[0] || 'Centre-ville' }}, {{ selectedHotel.city }}
                  </template>
                  <template v-else>
                    {{ selectedHotel.location || 'Centre-ville' }}, {{ selectedHotel.city }}
                  </template>
                </div>
                <div class="text-4xl font-bold text-blue-600">
                  {{ selectedHotel.unified_price?.value || selectedHotel.unified_price }}€ <span class="text-2xl font-normal text-gray-500">/nuit</span>
                </div>
              </div>
            </div>

            <!-- Badges et caractéristiques -->
            <div>
              <h2 class="text-3xl font-semibold mb-8">Caractéristiques</h2>
              <div class="space-y-8">
                <!-- Badges pour Booking -->
                <div v-if="SelectedSource === 'booking'" class="flex flex-wrap gap-4">
                  <span v-if="selectedHotel.preferredBadge" class="text-lg bg-yellow-100 text-yellow-800 px-6 py-3 rounded">Préféré</span>
                  <span v-if="selectedHotel.promotedBadge" class="text-lg bg-green-100 text-green-800 px-6 py-3 rounded">Promu</span>
                  <span v-if="selectedHotel.sustainability" class="text-lg bg-blue-100 text-blue-800 px-6 py-3 rounded">Écologique</span>
                </div>
                
                <!-- Highlights pour Booking -->
                <div v-if="SelectedSource === 'booking' && selectedHotel.highlights" class="space-y-4">
                  <h3 class="text-2xl font-medium">Points forts</h3>
                  <ul class="text-gray-600 space-y-3 text-xl">
                    <li v-for="(highlight, index) in selectedHotel.highlights" :key="index" class="flex items-center gap-3">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                      </svg>
                      {{ highlight }}
                    </li>
                  </ul>
                </div>

                <!-- Snippet pour Hotels.com -->
                <div v-if="SelectedSource === 'hotelscom' && selectedHotel.snippet" class="space-y-4">
                  <h3 class="text-2xl font-medium">Description</h3>
                  <p class="text-gray-600 text-xl">{{ selectedHotel.snippet.text }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de confirmation de suppression -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]">
      <div class="bg-white p-8 rounded-lg max-w-md w-full">
        <h3 class="text-2xl font-bold mb-4">Confirmer la suppression</h3>
        <p class="text-gray-600 mb-6">Êtes-vous sûr de vouloir supprimer l'hôtel "{{ selectedHotel?.title }}" ?</p>
        <div class="flex justify-end gap-4">
          <button 
            @click="showDeleteConfirm = false" 
            class="px-6 py-3 text-gray-600 hover:text-gray-800 font-medium"
          >
            Annuler
          </button>
          <button 
            @click="deleteHotel" 
            class="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
          >
            Supprimer
          </button>
        </div>
      </div>
    </div>

    <!-- Modal d'édition -->
    <div v-if="editMode" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]">
      <div class="bg-white p-8 rounded-lg w-full max-w-2xl">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold">Modifier l'hôtel</h3>
          <button 
            @click="editMode = false" 
            class="text-gray-500 hover:text-gray-700"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="saveEdit" class="space-y-6">
          <!-- Titre -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Titre</label>
            <input 
              v-model="editedHotel.title"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              required
            >
          </div>

          <!-- Prix -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Prix par nuit (€)</label>
            <input 
              v-model="editedHotel.price"
              type="number"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              required
            >
          </div>

          <!-- Note -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Note</label>
            <input 
              v-model="editedHotel.rating"
              type="number"
              step="0.1"
              min="0"
              max="5"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            >
          </div>

          <!-- Localisation -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Localisation</label>
            <input 
              v-model="editedHotel.location"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            >
          </div>

          <!-- Lien -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Lien</label>
            <input 
              v-model="editedHotel.link"
              type="url"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              required
            >
          </div>

          <!-- Badges pour Booking -->
          <div v-if="SelectedSource === 'booking'" class="space-y-4">
            <h4 class="text-lg font-medium">Badges</h4>
            <div class="flex gap-4">
              <label class="flex items-center">
                <input 
                  type="checkbox"
                  v-model="editedHotel.preferredBadge"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <span class="ml-2">Préféré</span>
              </label>
              <label class="flex items-center">
                <input 
                  type="checkbox"
                  v-model="editedHotel.promotedBadge"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <span class="ml-2">Promu</span>
              </label>
              <label class="flex items-center">
                <input 
                  type="checkbox"
                  v-model="editedHotel.sustainability"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <span class="ml-2">Écologique</span>
              </label>
            </div>
          </div>

          <!-- Champs spécifiques à Airbnb -->
          <div v-if="SelectedSource === 'airbnb'" class="space-y-4">
            <h4 class="text-lg font-medium">Informations Airbnb</h4>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Sous-titre</label>
              <input 
                v-model="editedHotel.subtitles[0]"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              >
            </div>
          </div>

          <!-- Champs spécifiques à Booking -->
          <div v-if="SelectedSource === 'booking'" class="space-y-4">
            <h4 class="text-lg font-medium">Informations Booking</h4>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Points forts</label>
              <div class="space-y-2">
                <div v-for="(highlight, index) in editedHotel.highlights" :key="index" class="flex gap-2">
                  <input 
                    v-model="editedHotel.highlights[index]"
                    type="text"
                    class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  >
                  <button 
                    type="button"
                    @click="editedHotel.highlights.splice(index, 1)"
                    class="px-3 py-2 text-red-600 hover:text-red-700"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
                <button 
                  type="button"
                  @click="editedHotel.highlights.push('')"
                  class="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  + Ajouter un point fort
                </button>
              </div>
            </div>
          </div>

          <!-- Champs spécifiques à Hotels.com -->
          <div v-if="SelectedSource === 'hotelscom'" class="space-y-4">
            <h4 class="text-lg font-medium">Informations Hotels.com</h4>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
              <textarea 
                v-model="editedHotel.snippet.text"
                rows="4"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>
          </div>

          <!-- Boutons -->
          <div class="flex justify-end gap-4 pt-4">
            <button 
              type="button"
              @click="editMode = false" 
              class="px-6 py-3 text-gray-600 hover:text-gray-800 font-medium"
            >
              Annuler
            </button>
            <button 
              type="submit"
              class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
            >
              Enregistrer
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()

// Lecture des paramètres forcés depuis l'URL
const cityFromURL = route.query.city as string || 'toutes'
const sourceFromURL = route.query.source as string || 'toutes'

const selectedCity = ref(cityFromURL)
const selectedSource = ref(sourceFromURL)
const minPrice = ref('')
const maxPrice = ref('')
const title = ref('')
const hotels = ref([])
const allHotels = ref([])
const loading = ref(false)
const error = ref(null)
const selectedHotel = ref(null)
const showDeleteConfirm = ref(false)
const editMode = ref(false)
const editedHotel = ref(null)
const currentPage = ref(1)
const pageSize = 20
const totalResults = ref(0)

// Si city ou source vient de l'URL, on les "verrouille"
const cityLocked = computed(() => route.query.city !== undefined)
const sourceLocked = computed(() => route.query.source !== undefined)

const fetchHotels = async () => {
  loading.value = true
  try {
    const params: any = {
      offset: (currentPage.value - 1) * pageSize,
      limit: pageSize,
    }

    if (selectedCity.value !== 'toutes') {
      params.city = selectedCity.value
    }
    if (selectedSource.value !== 'toutes') {
      params.source = selectedSource.value
    }
    if (minPrice.value) {
      params.min_price = minPrice.value
    }
    if (maxPrice.value) {
      params.max_price = maxPrice.value
    }
    if (title.value) {
      params.title_contains = title.value
    }

    // Exemple d'appel avec Fetch ou $fetch

    
    const response = await $fetch('http://localhost:5000/smart-search', { params })
    hotels.value = response.results
    console.log('Hôtels récupérés:', hotels.value)
    totalResults.value = response.total
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
}

const filterHotels = () => {
  hotels.value = allHotels.value.filter(hotel => {
    const matchesCity = selectedCity.value === 'all' || hotel.city === selectedCity.value
    const price = hotel.unified_price?.value || hotel.unified_price
    const matchesMinPrice = !minPrice.value || price >= Number(minPrice.value)
    const matchesMaxPrice = !maxPrice.value || price <= Number(maxPrice.value)
    return matchesCity && matchesMinPrice && matchesMaxPrice
  })
}

// Charger les hôtels au montage du composant
onMounted(() => {
  fetchHotels()
})

const resetFilters = () => {
  if (!cityLocked.value) selectedCity.value = 'toutes'
  if (!sourceLocked.value) selectedSource.value = 'toutes'
  minPrice.value = ''
  maxPrice.value = ''
  title.value = ''
}

// Les filtres sont réactifs et mettront à jour l'affichage automatiquement
watch([selectedCity, selectedSource, title, maxPrice, minPrice], () => {
  currentPage.value = 1
  fetchHotels()
})

const goToHotelDetails = (hotel) => {
  selectedHotel.value = hotel
}

const closeModal = () => {
  selectedHotel.value = null
  showDeleteConfirm.value = false
  editMode.value = false
}

const deleteHotel = async () => {
  try {
    const response = await fetch(
      `http://localhost:5000/${selectedHotel.value.city}/${SelectedSource.value}?title=${encodeURIComponent(selectedHotel.value.title)}`,
      { method: 'DELETE' }
    )
    if (!response.ok) throw new Error('Erreur lors de la suppression')
    // Mettre à jour la liste des hôtels
    await fetchHotels()
    closeModal()
  } catch (e) {
    error.value = e.message
    console.error('Erreur:', e)
  }
}

const startEdit = () => {
  // Créer une copie profonde de l'hôtel sélectionné
  editedHotel.value = {
    ...selectedHotel.value,
    price: selectedHotel.value.price?.value || selectedHotel.value.price,
    rating: selectedHotel.value.rating?.score || selectedHotel.value.rating,
    // Pour Airbnb
    subtitles: selectedHotel.value.subtitles || [],
    // Pour Booking
    highlights: selectedHotel.value.highlights || [],
    // Pour Hotels.com
    snippet: selectedHotel.value.snippet || { text: '' }
  }
  editMode.value = true
}

const saveEdit = async () => {
  try {
    // Restructurer les données avant l'envoi
    const dataToSend = {
      ...editedHotel.value,
      price: {
        value: Number(editedHotel.value.price)
      },
      rating: SelectedSource.value === 'booking' ? { score: Number(editedHotel.value.rating) } : Number(editedHotel.value.rating)
    }

    const response = await fetch(
      `http://localhost:5000/${editedHotel.value.city}/${SelectedSource.value}?title=${encodeURIComponent(editedHotel.value.title)}`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToSend)
      }
    )
    if (!response.ok) throw new Error('Erreur lors de la modification')
    await fetchHotels()
    editMode.value = false
    selectedHotel.value = dataToSend
  } catch (e) {
    error.value = e.message
    console.error('Erreur:', e)
  }
}
</script> 