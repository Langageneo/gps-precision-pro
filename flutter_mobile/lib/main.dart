// flutter_mobile/lib/main.dart
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  final API = "http://localhost:8000/gps-correct";
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'GPS Mobile',
      home: Scaffold(
        appBar: AppBar(title: Text('GPS Mobile')),
        body: Center(child: GPSButton(api: API)),
      ),
    );
  }
}

class GPSButton extends StatefulWidget {
  final String api;
  GPSButton({required this.api});
  @override State<GPSButton> createState() => _GPSButtonState();
}

class _GPSButtonState extends State<GPSButton> {
  String _status = '';

  Future<void> send() async {
    LocationPermission permission = await Geolocator.checkPermission();
    if(permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    Position pos = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
    final payload = {
      "device_id": "flutter-"+DateTime.now().millisecondsSinceEpoch.toString(),
      "lat": pos.latitude,
      "lon": pos.longitude,
      "accuracy": pos.accuracy,
      "timestamp": (DateTime.now().millisecondsSinceEpoch/1000).round()
    };
    final resp = await http.post(Uri.parse(widget.api), headers: {"Content-Type":"application/json"}, body: json.encode(payload));
    setState(() { _status = resp.body; });
  }

  @override
  Widget build(BuildContext context) {
    return Column(mainAxisAlignment: MainAxisAlignment.center, children: [
      ElevatedButton(onPressed: send, child: Text("Envoyer position")),
      SizedBox(height:10),
      Text(_status)
    ]);
  }
}
