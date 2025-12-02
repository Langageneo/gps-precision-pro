package com.tonapp.gpsdashboard

import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.*

class MainActivity : AppCompatActivity() {

    private lateinit var gpsModule: GPSModule
    private lateinit var analyticsService: AnalyticsService
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: TableAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        gpsModule = GPSModule(this)
        analyticsService = AnalyticsService("https://ton-backend.com")

        recyclerView = findViewById(R.id.rvTable)
        recyclerView.layoutManager = LinearLayoutManager(this)
        adapter = TableAdapter()
        recyclerView.adapter = adapter

        val btnRefresh: Button = findViewById(R.id.btnRefresh)
        btnRefresh.setOnClickListener {
            refreshData()
        }

        // Optionnel : récupérer GPS dès le lancement
        gpsModule.getCurrentLocation { lat, lon ->
            Toast.makeText(this, "GPS: $lat, $lon", Toast.LENGTH_SHORT).show()
        }
    }

    private fun refreshData() {
        CoroutineScope(Dispatchers.Main).launch {
            try {
                val livreurs = analyticsService.getLivreurs()
                val best = analyticsService.getBestLivreur()
                val produits = analyticsService.getProduitsPopulaires()

                // Mettre à jour RecyclerView
                val tableData = mutableListOf<String>()
                tableData.add("=== Meilleur Livreur ===")
                tableData.add("${best?.livreur_id} - Score: ${best?.score_moyen}")

                tableData.add("=== Top Produits ===")
                produits.forEach { tableData.add("${it.name} - Ventes: ${it.ventes}") }

                tableData.add("=== Tous Livreurs ===")
                livreurs.forEach { tableData.add("${it.livreur_id} - Livraisons: ${it.livraisons}") }

                adapter.updateData(tableData)

            } catch (e: Exception) {
                e.printStackTrace()
                Toast.makeText(this@MainActivity, "Erreur récupération analytics", Toast.LENGTH_LONG).show()
            }
        }
    }
}
