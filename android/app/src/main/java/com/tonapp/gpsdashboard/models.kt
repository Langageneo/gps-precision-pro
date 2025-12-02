package com.tonapp.gpsdashboard

data class Livreur(
    val livreur_id: String,
    val livraisons: Int,
    val distance_totale: Double,
    val score_moyen: Double
)

data class Produit(
    val name: String,
    val ventes: Int
)

data class Alert(
    val zone: String,
    val nb_livraisons: Int
)

data class Predictive(
    val zones_a_surveiller: List<Pair<String, Int>>
)
