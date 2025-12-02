package com.tonapp.gpsdashboard

import okhttp3.*
import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class AnalyticsService(val backendUrl: String) {
    private val client = OkHttpClient()
    private val gson = Gson()

    suspend fun getLivreurs(): List<Livreur> = withContext(Dispatchers.IO) {
        val request = Request.Builder().url("$backendUrl/analytics/livreurs").build()
        val response = client.newCall(request).execute()
        val body = response.body?.string() ?: "[]"
        gson.fromJson(body, Array<Livreur>::class.java).toList()
    }

    suspend fun getBestLivreur(): Livreur? = withContext(Dispatchers.IO) {
        val request = Request.Builder().url("$backendUrl/analytics/meilleur-livreur").build()
        val response = client.newCall(request).execute()
        val body = response.body?.string() ?: "{}"
        gson.fromJson(body, Livreur::class.java)
    }

    suspend fun getProduitsPopulaires(): List<Produit> = withContext(Dispatchers.IO) {
        val request = Request.Builder().url("$backendUrl/analytics/produits-populaires").build()
        val response = client.newCall(request).execute()
        val body = response.body?.string() ?: "[]"
        gson.fromJson(body, Array<Produit>::class.java).toList()
    }

    suspend fun getAlerts(): List<Alert> = withContext(Dispatchers.IO) {
        val request = Request.Builder().url("$backendUrl/analytics/alertes").build()
        val response = client.newCall(request).execute()
        val body = response.body?.string() ?: "[]"
        gson.fromJson(body, Array<Alert>::class.java).toList()
    }

    suspend fun getPredictive(): Predictive = withContext(Dispatchers.IO) {
        val request = Request.Builder().url("$backendUrl/analytics/predictive").build()
        val response = client.newCall(request).execute()
        val body = response.body?.string() ?: "{}"
        gson.fromJson(body, Predictive::class.java)
    }
}
