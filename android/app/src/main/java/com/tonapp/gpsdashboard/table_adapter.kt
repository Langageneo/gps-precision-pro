package com.tonapp.gpsdashboard

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class TableAdapter : RecyclerView.Adapter<TableAdapter.TableViewHolder>() {

    private var data: List<TableItem> = listOf()

    fun updateData(newData: List<TableItem>) {
        data = newData
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TableViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_table_row, parent, false)
        return TableViewHolder(view)
    }

    override fun onBindViewHolder(holder: TableViewHolder, position: Int) {
        holder.bind(data[position])
    }

    override fun getItemCount(): Int = data.size

    class TableViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val col1: TextView = itemView.findViewById(R.id.tvColumn1)
        private val col2: TextView = itemView.findViewById(R.id.tvColumn2)

        fun bind(item: TableItem) {
            col1.text = item.title
            col2.text = item.detail
        }
    }
}
