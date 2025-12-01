// android/gps_module.kt
package com.example.gpsmodule

import android.location.Location
import android.os.Bundle
import okhttp3.*
import org.json.JSONObject
import java.io.IOException

object GpsUploader {
    val client = OkHttpClient()
    val API = "http://YOUR_SERVER:8000/gps-correct"

    fun sendPoint(deviceId: String, loc: Location, timestamp: Long) {
        val json = JSONObject()
        json.put("device_id", deviceId)
        json.put("lat", loc.latitude)
        json.put("lon", loc.longitude)
        json.put("accuracy", loc.accuracy)
        json.put("timestamp", timestamp)
        val body = RequestBody.create(MediaType.parse("application/json"), json.toString())
        val req = Request.Builder().url(API).post(body).build()
        client.newCall(req).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) { /* log */ }
            override fun onResponse(call: Call, response: Response) { /* handle */ }
        })
    }
}
