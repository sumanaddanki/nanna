# Deploy Recipe Extractor to MSI with Docker

## ✅ Code is Ready!

All code has been pushed to GitHub and pulled to MSI at:
```
C:\Users\SemoMSIRemote\git\sumanaddanki\nanna\recipe-extractor\
```

---

## 🐳 Docker Deployment Steps

### 1. Start Docker Desktop on MSI

**Option A: GUI**
- Open Start Menu
- Search for "Docker Desktop"
- Click to start
- Wait for Docker to fully start (~30 seconds)

**Option B: Command Line (PowerShell as Admin)**
```powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

### 2. Verify Docker is Running

Open Command Prompt or PowerShell and run:
```cmd
docker --version
docker info
```

Should show Docker version and running status.

### 3. Navigate to Recipe Extractor Directory

```cmd
cd C:\Users\SemoMSIRemote\git\sumanaddanki\nanna\recipe-extractor
```

### 4. Build and Start the Container

```cmd
docker-compose up -d --build
```

This will:
- Build Docker image with Python 3.11, ffmpeg, all dependencies
- Start container on port 5555
- Mount `.env` for API keys
- Persist recipes in `recipes/` folder

### 5. Verify Container is Running

```cmd
docker-compose ps
docker logs recipe-extractor
```

Should show:
```
Starting Recipe Extractor Web UI...
Open browser to: http://localhost:5555
```

### 6. Access the Web UI

**From MSI (locally):**
```
http://localhost:5555
```

**From Mac Studio (Tailscale):**
```
http://100.112.166.117:5555
```

**From Mac Air (Tailscale):**
```
http://100.112.166.117:5555
```

**From Phone (same WiFi):**
```
http://[MSI_LOCAL_IP]:5555
```

---

## 🎯 Quick Commands

### Start Container (if stopped)
```cmd
cd C:\Users\SemoMSIRemote\git\sumanaddanki\nanna\recipe-extractor
docker-compose start
```

### Stop Container
```cmd
docker-compose stop
```

### Restart Container
```cmd
docker-compose restart
```

### View Logs
```cmd
docker-compose logs -f
```

### Rebuild After Code Changes
```cmd
git pull origin main
docker-compose up -d --build
```

### Stop and Remove Everything
```cmd
docker-compose down
```

---

## 📁 Docker Configuration

### Dockerfile
- Base image: `python:3.11-slim`
- Includes: ffmpeg, OpenCV, all Python deps
- Exposes port: 5555
- Health check: HTTP ping every 30s

### docker-compose.yml
- Service name: `recipe-extractor`
- Port mapping: `5555:5555`
- Volume mounts:
  - `./recipes:/app/recipes` (persist extracted recipes)
  - `./.env:/app/.env` (API keys)
- Auto-restart: `unless-stopped`

### Volumes
- **recipes/**: Extracted recipes stored here
- **.env**: Gemini API key (already configured)

---

## 🔧 Troubleshooting

### Docker Desktop Won't Start
```powershell
# Check if Docker service is running
Get-Service -Name *docker*

# Start Docker service
Start-Service -Name com.docker.service
```

### Container Fails to Build
```cmd
# Check logs
docker-compose logs

# Clean rebuild
docker-compose down
docker system prune -a
docker-compose up -d --build
```

### Port 5555 Already in Use
```cmd
# Find process using port 5555
netstat -ano | findstr :5555

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
ports:
  - "5556:5555"  # Use 5556 instead
```

### Can't Access from Other Devices
```cmd
# Check Windows Firewall
# Allow port 5555 inbound:
netsh advfirewall firewall add rule name="Recipe Extractor" dir=in action=allow protocol=TCP localport=5555
```

---

## 🚀 Performance Notes

### Current Setup (CPU Only)
- **Whisper Transcription**: ~30-60s for 5-min video
- **Gemini OCR**: ~3-5s per image
- **Total Processing**: ~1-2 min per recipe

### After PyTorch RTX 5080 Support
- **Whisper Transcription**: ~10-15s (GPU accelerated!)
- **Gemini OCR**: ~3-5s
- **Total Processing**: ~15-25s per recipe

To enable GPU later, update Dockerfile:
```dockerfile
# Install CUDA-enabled PyTorch
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

---

## 📊 What Runs in Docker

The container includes:
- Flask web server (port 5555)
- WebSocket for real-time updates
- Whisper large model (auto-downloads ~3GB on first run)
- Gemini API client
- OpenCV for video frame extraction
- ffmpeg for audio extraction

**First Run**: May take a few minutes as Whisper downloads its model.

---

## ✅ Testing Checklist

After deployment, test:
- [ ] Web UI loads at http://localhost:5555
- [ ] Can upload image → recipe extracted
- [ ] Can paste YouTube URL → recipe extracted
- [ ] Can upload video file → frames + transcript
- [ ] Download JSON works
- [ ] Download Markdown works
- [ ] Accessible from Mac Studio via Tailscale
- [ ] Accessible from Mac Air via Tailscale

---

## 🔄 Update Workflow

When code is updated:
```cmd
# On MSI
cd C:\Users\SemoMSIRemote\git\sumanaddanki\nanna\recipe-extractor

# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose up -d --build
```

---

## 🎉 Benefits of Docker Deployment

1. **Consistency**: Same environment everywhere
2. **Isolation**: Won't interfere with other Python projects
3. **Easy Updates**: Just rebuild container
4. **Auto-restart**: Survives MSI reboots
5. **Clean Logs**: Centralized in Docker
6. **Portable**: Can deploy to any machine with Docker

---

## 📞 Support

**Docker not working?**
1. Check if Docker Desktop is installed
2. Verify Docker service is running
3. Try starting Docker Desktop manually

**Container fails?**
1. Check logs: `docker-compose logs`
2. Verify .env file exists with API key
3. Ensure port 5555 is free

**Can't access from network?**
1. Check Windows Firewall
2. Verify Tailscale is running
3. Try localhost:5555 first

---

**Status**: Ready for deployment!

**Next Step**: Start Docker Desktop on MSI and run `docker-compose up -d --build`

**Access URL**: http://100.112.166.117:5555 (from Mac Studio/Air)
