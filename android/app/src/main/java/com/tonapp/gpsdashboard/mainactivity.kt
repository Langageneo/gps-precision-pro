package com.tonapp.gpsdashboard

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.*

class MainActivity : AppCompatActivity() {

    private lateinit var gpsModule: GPSModule
    private lateinit var analyticsService: AnalyticsService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        gpsModule = GPSModule(this)
        analyticsService = AnalyticsService("https://ton-backend.com")

        val btnRefresh: Button = findViewById(R.id.btnRefresh)
        btnRefresh.setOnClickListener {
            fetchAnalytics()
        }
    }

    private fun fetchAnalytics() {
        CoroutineScope(Dispatchers.Main).launch {
            try {
                val livreurs = analyticsService.getLivreurs()
                val best = analyticsService.getBestLivreur()
                val produits = analyticsService.getProduitsPopulaires()
                val alerts = analyticsService.getAlerts()
                val predictive = analyticsService.getPredictive()

                // Affichage console temporaire, tu peux faire recyclerview ou cartes
                println("Livreurs: $livreurs")
                println("Meilleur: $best")
                println("Produits: $produits")
                println("Alertes: $alerts")
                println("Prédictions: $predictive")

            } catch (e: Exception) {
                e.printStackTrace()
                Toast.makeText(this@MainActivity, "Erreur récupération analytics", Toast.LENGTH_LONG).show()
            }
        }
    }
}
