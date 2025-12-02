package com.tonapp.gpsdashboard

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import okhttp3.OkHttpClient
import okhttp3.Request
import com.google.gson.Gson

class SyncWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    private val client = OkHttpClient()
    private val gson = Gson()

    override suspend fun doWork(): Result {
        // Exemple : push les positions locales au backend
        try {
            // Ici tu lirais ta DB locale (Room) et enverrais les positions non sync
            // Simplifié : ping backend
            val backend = inputData.getString("backend_url") ?: "https://ton-backend.com"
            val req = Request.Builder().url("$backend/health").build()
            val resp = client.newCall(req).execute()
            if (resp.isSuccessful) return Result.success()
            return Result.retry()
        } catch (e: Exception) {
            e.printStackTrace()
            return Result.retry()
        }
    }
}
