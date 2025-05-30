<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <div class="text-center mb-12">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">Contactez-nous</h1>
      <p class="text-lg text-gray-600">Nous sommes là pour vous aider et répondre à vos questions</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
      <!-- Formulaire de contact -->
      <div class="bg-white p-8 rounded-lg shadow-md">
        <form @submit.prevent="submitForm" class="space-y-6">
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 mb-2">Nom complet</label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              placeholder="Votre nom"
            >
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              placeholder="votre@email.com"
            >
          </div>

          <div>
            <label for="subject" class="block text-sm font-medium text-gray-700 mb-2">Sujet</label>
            <input
              id="subject"
              v-model="form.subject"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              placeholder="Sujet de votre message"
            >
          </div>

          <div>
            <label for="message" class="block text-sm font-medium text-gray-700 mb-2">Message</label>
            <textarea
              id="message"
              v-model="form.message"
              rows="6"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              placeholder="Votre message..."
            ></textarea>
          </div>

          <button
            type="submit"
            class="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors duration-200"
            :disabled="loading"
          >
            <span v-if="loading">Envoi en cours...</span>
            <span v-else>Envoyer le message</span>
          </button>
        </form>
      </div>

      <!-- Informations de contact -->
      <div class="space-y-8">
        <div class="bg-white p-8 rounded-lg shadow-md">
          <h2 class="text-2xl font-semibold text-gray-900 mb-6">Informations de contact</h2>
          
          <div class="space-y-6">
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-medium text-gray-900">Email</h3>
                <p class="mt-1 text-gray-600">contact@7.5khotels.com</p>
              </div>
            </div>

            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-medium text-gray-900">Téléphone</h3>
                <p class="mt-1 text-gray-600">+33 1 23 45 67 89</p>
              </div>
            </div>

            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-medium text-gray-900">Adresse</h3>
                <p class="mt-1 text-gray-600">
                  123 Rue de l'Innovation<br>
                  75001 Paris<br>
                  France
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Horaires d'ouverture -->
        <div class="bg-white p-8 rounded-lg shadow-md">
          <h2 class="text-2xl font-semibold text-gray-900 mb-6">Horaires d'ouverture</h2>
          <div class="space-y-4">
            <div class="flex justify-between">
              <span class="text-gray-600">Lundi - Vendredi</span>
              <span class="text-gray-900 font-medium">9h00 - 18h00</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Samedi</span>
              <span class="text-gray-900 font-medium">10h00 - 16h00</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Dimanche</span>
              <span class="text-gray-900 font-medium">Fermé</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const form = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const loading = ref(false)

const submitForm = async () => {
  loading.value = true
  try {
    // Ici, vous pouvez ajouter la logique pour envoyer le formulaire à votre backend
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulation d'envoi
    alert('Message envoyé avec succès !')
    form.value = {
      name: '',
      email: '',
      subject: '',
      message: ''
    }
  } catch (error) {
    alert('Une erreur est survenue lors de l\'envoi du message.')
  } finally {
    loading.value = false
  }
}
</script> 