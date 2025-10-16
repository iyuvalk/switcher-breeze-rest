#!/usr/local/bin/python3

import asyncio
import argparse
from dataclasses import asdict
from bottle import Bottle, run, request, response
from aioswitcher.bridge import SwitcherBridge
from aioswitcher.api import SwitcherApi
from aioswitcher.api.remotes import SwitcherBreezeRemoteManager
from aioswitcher.device import (
    DeviceState,
    DeviceType,
    ThermostatFanLevel,
    ThermostatMode,
    ThermostatSwing,
)

app = Bottle()


# ----------- Helper functions -----------

async def scan_devices(callback, delay=10):
    """Scan devices for a short period and call the callback for each device found."""
    async with SwitcherBridge(callback):
        await asyncio.sleep(delay)


async def control_breeze(device_type, device_ip, device_id, device_key, remote_manager,
                         remote_id, device_state, mode, temperature, fan_level):
    """Control a Switcher Breeze device."""
    async with SwitcherApi(device_type, device_ip, device_id, device_key) as api:
        await api.get_breeze_state()
        remote = remote_manager.get_remote(remote_id)
        await api.control_breeze_device(
            remote,
            device_state,
            mode,
            temperature,
            fan_level,
            ThermostatSwing.ON,
        )


# ----------- Bottle Routes -----------

@app.get("/devices/temperature")
def get_device_temperature():
    """Return the temperature of the first found device."""
    result = {}

    def callback(device):
        nonlocal result
        result = {"temperature": asdict(device)["temperature"]}
        raise SystemExit  # stop scan immediately

    try:
        asyncio.run(scan_devices(callback, delay=10))
    except SystemExit:
        pass

    if result:
        return result
    response.status = 404
    return {"error": "No devices found"}


@app.get("/devices/state")
def get_device_state():
    """Return the state of the first found device."""
    result = {}

    def callback(device):
        nonlocal result
        result = {"state": str(asdict(device)["device_state"])}
        raise SystemExit  # stop scan immediately

    try:
        asyncio.run(scan_devices(callback, delay=10))
    except SystemExit:
        pass

    if result:
        return result
    response.status = 404
    return {"error": "No devices found"}


@app.post("/breeze/control")
def post_breeze_control():
    """Control a Switcher Breeze device via POST JSON."""
    data = request.json
    required_keys = ["device_id", "device_key", "remote_id", "state"]
    if not data or not all(k in data for k in required_keys):
        response.status = 400
        return {"error": f"Missing required keys: {required_keys}"}

    state_str = data["state"].upper()
    if state_str not in ["ON", "OFF"]:
        response.status = 400
        return {"error": "Invalid state, must be 'ON' or 'OFF'"}

    device_state = DeviceState[state_str]
    ip = data.get("ip", "switcher-breeze")
    remote_manager = SwitcherBreezeRemoteManager()

    # If state is ON, check that mode, temp, and fan are provided
    if device_state == DeviceState.ON:
        for key in ["mode", "temp", "fan"]:
            if key not in data:
                response.status = 400
                return {"error": f"Missing required key for ON state: {key}"}
        mode = ThermostatMode[data["mode"].upper()]
        fan_level = ThermostatFanLevel[data["fan"].upper()]
        temp = data["temp"]
    else:
        # If OFF, use default values required by API
        mode = ThermostatMode.COOL
        fan_level = ThermostatFanLevel.MEDIUM
        temp = 23

    asyncio.run(
        control_breeze(
            DeviceType.BREEZE,
            ip,
            data["device_id"],
            data["device_key"],
            remote_manager,
            data["remote_id"],
            device_state,
            mode,
            temp,
            fan_level,
        )
    )

    return {"status": "success"}


# ----------- Run server -----------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Switcher REST API Service")
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to listen on (default: 8080)",
    )
    args = parser.parse_args()

    run(app, host="0.0.0.0", port=args.port, debug=True)
