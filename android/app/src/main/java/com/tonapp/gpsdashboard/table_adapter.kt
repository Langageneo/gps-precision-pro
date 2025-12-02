package com.tonapp.gpsdashboard

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

data class DeliveryData(
    val livreur: String,
    val produit: String,
    val distance: Double,
    val evaluation: Float
)

class TableAdapter(private val dataList: List<DeliveryData>) :
    RecyclerView.Adapter<TableAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val livreurText: TextView = view.findViewById(R.id.livreurText)
        val produitText: TextView = view.findViewById(R.id.produitText)
        val distanceText: TextView = view.findViewById(R.id.distanceText)
        val evaluationText: TextView = view.findViewById(R.id.evaluationText)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_table_row, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = dataList[position]
        holder.livreurText.text = item.livreur
        holder.produitText.text = item.produit
        holder.distanceText.text = "%.2f km".format(item.distance)
        holder.evaluationText.text = "%.1f ⭐".format(item.evaluation)
    }

    override fun getItemCount(): Int = dataList.size
    }
