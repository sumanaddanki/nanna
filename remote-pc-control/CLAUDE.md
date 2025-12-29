# Remote PC Control - AI-Powered KVM

## Project Overview
External hardware solution to control any PC remotely using:
- Raspberry Pi Pico W (USB HID mouse/keyboard emulation)
- HDMI capture for screen viewing
- Gemini Vision AI for intelligent automation
- Web interface for remote access

## Architecture
```
[Target PC] ←USB→ [Pico W] ←WiFi→ [Server/Pi] ←Web→ [User anywhere]
                                      ↑
                              [HDMI Capture]
                                      ↑
                              [Target PC display]
```

## Project Structure
```
remote-pc-control/
├── pico/           # Raspberry Pi Pico W firmware (CircuitPython)
│   └── main.py     # USB HID + WiFi server
├── server/         # Python server (runs on Pi/laptop)
│   ├── main.py     # Flask + AI + screen capture
│   └── requirements.txt
└── web/            # Web interface (TODO)
    └── templates/
        └── index.html
```

## Hardware Required
- Raspberry Pi Pico W (~$6)
- HDMI capture dongle (~$10-15)
- Raspberry Pi Zero 2 W or laptop (~$15+)

## Setup
1. Flash Pico W with CircuitPython + pico/main.py
2. Install server dependencies: `pip install -r server/requirements.txt`
3. Configure .env with GEMINI_API_KEY and PICO_IP
4. Run server: `python server/main.py`

## TODO
- [ ] Complete Pico W firmware
- [ ] Create web interface with live video feed
- [ ] Add AI automation features
- [ ] Create setup instructions
- [ ] Test end-to-end

## Business Goal
Potential Amazon product - external KVM with AI features
Similar to: PiKVM, TinyPilot
