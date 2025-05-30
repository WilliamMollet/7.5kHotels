<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div v-if="loading" class="flex justify-center items-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
      <span class="block sm:inline">{{ error }}</span>
    </div>

    <div v-else class="bg-white rounded-lg shadow-lg overflow-hidden">
      <!-- En-tête avec image -->
      <div class="relative h-96">
        <img 
          :src="hotel.thumbnail" 
          :alt="hotel.title" 
          class="w-full h-full object-cover"
        >
        <div class="absolute top-4 right-4 flex gap-2">
          <button 
            @click="editMode = true" 
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
        </div>
      </div>

      <!-- Contenu -->
      <div class="p-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">{{ hotel.title }}</h1>
        
        <!-- Informations principales -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div>
            <h2 class="text-xl font-semibold mb-4">Informations</h2>
            <div class="space-y-4">
              <div class="flex items-center">
                <span class="text-yellow-400 text-xl mr-2">★</span>
                <span class="text-gray-600">
                  <template v-if="platform === 'airbnb'">
                    {{ hotel.rating || 'N/A' }}
                  </template>
                  <template v-else-if="platform === 'booking'">
                    {{ hotel.rating?.score || 'N/A' }}
                  </template>
                  <template v-else>
                    {{ hotel.rating || 'N/A' }}
                  </template>
                </span>
              </div>
              <div class="text-gray-600">
                <template v-if="platform === 'airbnb'">
                  {{ hotel.subtitles?.[0] || 'Centre-ville' }}, {{ hotel.city }}
                </template>
                <template v-else>
                  {{ hotel.location || 'Centre-ville' }}, {{ hotel.city }}
                </template>
              </div>
              <div class="text-2xl font-bold text-blue-600">
                {{ hotel.price?.value || hotel.price }}€ <span class="text-sm font-normal text-gray-500">/nuit</span>
              </div>
            </div>
          </div>

          <!-- Badges et caractéristiques -->
          <div>
            <h2 class="text-xl font-semibold mb-4">Caractéristiques</h2>
            <div class="space-y-4">
              <!-- Badges pour Booking -->
              <div v-if="platform === 'booking'" class="flex flex-wrap gap-2">
                <span v-if="hotel.preferredBadge" class="text-sm bg-yellow-100 text-yellow-800 px-3 py-1 rounded">Préféré</span>
                <span v-if="hotel.promotedBadge" class="text-sm bg-green-100 text-green-800 px-3 py-1 rounded">Promu</span>
                <span v-if="hotel.sustainability" class="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded">Écologique</span>
              </div>
              
              <!-- Highlights pour Booking -->
              <div v-if="platform === 'booking' && hotel.highlights" class="space-y-2">
                <h3 class="font-medium">Points forts</h3>
                <ul class="text-gray-600 space-y-1">
                  <li v-for="(highlight, index) in hotel.highlights" :key="index">
                    {{ highlight }}
                  </li>
                </ul>
              </div>

              <!-- Snippet pour Hotels.com -->
              <div v-if="platform === 'hotelscom' && hotel.snippet" class="space-y-2">
                <h3 class="font-medium">Description</h3>
                <p class="text-gray-600">{{ hotel.snippet.text }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Lien vers la plateforme -->
        <div class="mt-8">
          <a 
            :href="hotel.link" 
            target="_blank" 
            class="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Voir sur {{ platform }}
          </a>
        </div>
      </div>
    </div>

    <!-- Modal de confirmation de suppression -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white p-6 rounded-lg max-w-md w-full">
        <h3 class="text-xl font-bold mb-4">Confirmer la suppression</h3>
        <p class="text-gray-600 mb-6">Êtes-vous sûr de vouloir supprimer cet hôtel ?</p>
        <div class="flex justify-end gap-4">
          <button 
            @click="showDeleteConfirm = false" 
            class="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            Annuler
          </button>
          <button 
            @click="deleteHotel" 
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Supprimer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const hotel = ref(null)
const loading = ref(true)
const error = ref(null)
const showDeleteConfirm = ref(false)
const platform = ref('')

const fetchHotel = async () => {
  loading.value = true
  error.value = null
  try {
    const { city, platform: platformParam, title } = route.params
    console.log('=== DÉBUT DE LA REQUÊTE FRONTEND ===')
    console.log('Paramètres de route bruts:', route.params)
    
    const decodedTitle = decodeURIComponent(title)
    console.log('Titre décodé:', decodedTitle)
    
    const url = `http://localhost:5000/hotel/${city}/${platformParam}/${decodedTitle}`
    console.log('URL de la requête:', url)
    
    platform.value = platformParam
    console.log('Envoi de la requête...')
    const response = await fetch(url)
    console.log('Statut de la réponse:', response.status)
    
    if (!response.ok) {
      const errorData = await response.json()
      console.error('Erreur de réponse:', errorData)
      throw new Error(errorData.error || 'Erreur lors de la récupération des données')
    }
    
    hotel.value = await response.json()
    console.log('Données reçues:', hotel.value)
    console.log('=== FIN DE LA REQUÊTE FRONTEND ===')
  } catch (e) {
    console.error('Erreur complète:', e)
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const deleteHotel = async () => {
  try {
    const { city, platform: platformParam } = route.params
    const response = await fetch(
      `http://localhost:5000/${city}/${platformParam}?title=${encodeURIComponent(hotel.value.title)}`,
      { method: 'DELETE' }
    )
    if (!response.ok) throw new Error('Erreur lors de la suppression')
    router.push('/hotels')
  } catch (e) {
    error.value = e.message
    console.error('Erreur:', e)
  }
}

onMounted(() => {
  fetchHotel()
})
</script> 