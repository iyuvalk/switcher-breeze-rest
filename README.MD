# switcher-breeze-rest
A simple REST service for controlling the AC via Switcher Breeze

# Example Usage:
1. Turn ON the AC:
```
curl -X POST http://localhost:8080/breeze/control \
     -H "Content-Type: application/json" \
     -d '{
           "device_id": "xxxx",
           "device_key": "nn",
           "remote_id": "ZM079060",
           "state": "ON",
           "mode": "COOL",
           "temp": 23,
           "fan": "MEDIUM"
         }'
```

2. Turn OFF the AC:
```
curl -X POST http://localhost:8080/breeze/control \
     -H "Content-Type: application/json" \
     -d '{
           "device_id": "xxxx",
           "device_key": "nn",
           "remote_id": "ZM079060",
           "state": "OFF"
         }'
```

3. Get current temperature:
```
curl http://localhost:8080/devices/temperature
```

4. Get device state:
```
curl http://localhost:8080/devices/state
```

