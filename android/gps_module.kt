package com.gpspro

import android.location.Location
import okhttp3.*
import org.json.JSONObject

class GPSModule(private val client: OkHttpClient) {
    fun sendPosition(loc: Location) {
        val json = JSONObject()
        json.put("lat", loc.latitude)
        json.put("lon", loc.longitude)
        json.put("accuracy", loc.accuracy)
        json.put("device_id", "android")

        val body = json.toString().toRequestBody("application/json".toMediaType())
        val req = Request.Builder()
            .url("http://10.0.2.2:8000/gps-correct")
            .post(body)
            .build()

        client.newCall(req).execute()
    }
}
