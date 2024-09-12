package com.example.labchecker.util.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.core.view.isVisible
import androidx.recyclerview.widget.RecyclerView
import com.example.labchecker.R

class LabsRecyclerViewAdapter(
    private val items: List<String>,
    private val onGradeClick: (lab: String) -> Unit // Коллбэк для обработки нажатия на кнопку
) : RecyclerView.Adapter<LabsRecyclerViewAdapter.LabViewHolder>() {

    class LabViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val textView: TextView = itemView.findViewById(R.id.textView)
        val button: Button = itemView.findViewById(R.id.btn_check)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): LabViewHolder {
        val itemView = LayoutInflater.from(parent.context)
            .inflate(R.layout.list_item, parent, false)
        return LabViewHolder(itemView)
    }

    override fun onBindViewHolder(holder: LabViewHolder, position: Int) {
        val item = items[position]
        holder.textView.text = item

        holder.button.setOnClickListener {
            holder.button.isVisible = false
            onGradeClick(item) // Вызов коллбэка с текущим элементом списка (lab)
        }
    }

    override fun getItemCount() = items.size
}
