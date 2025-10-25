# Raspberry Pi Commands Reference

Your ARC installation: **`/home/admin/ARC`**

## Running Apps Manually

### Simple Command Format:
```bash
cd /home/admin/ARC/<app_folder> && ../venv/bin/python main.py
```

### Specific Apps:

**Music Player:**
```bash
cd /home/admin/ARC/music_player && ../venv/bin/python main.py
```

**Chatbot:**
```bash
cd /home/admin/ARC/Chatbot && ../venv/bin/python main.py
```

**WiFi Tools:**
```bash
cd /home/admin/ARC/WIFI_tools && ../venv/bin/python main.py
```

**Calendar:**
```bash
cd /home/admin/ARC/Calendar_app && ../venv/bin/python main.py
```

**Games:**
```bash
cd /home/admin/ARC/Games && ../venv/bin/python main.py
```

**NFC Tools:**
```bash
cd /home/admin/ARC/NFC_tools && ../venv/bin/python main.py
```

**RF Tools:**
```bash
cd /home/admin/ARC/RF_tools && ../venv/bin/python main.py
```

**IR Tools:**
```bash
cd /home/admin/ARC/IR_tools && ../venv/bin/python main.py
```

**Bluetooth Tools:**
```bash
cd /home/admin/ARC/BT_tools && ../venv/bin/python main.py
```

**Notes/Text Editor:**
```bash
cd /home/admin/ARC/Notes_app && ../venv/bin/python main.py
```

**ARC Connect:**
```bash
cd /home/admin/ARC/ARC_connect && ../venv/bin/python ip.py
```

## Running the Launcher

```bash
cd /home/admin/ARC
venv/bin/python launcher.py
```

## Setup Commands

### Pull Latest Changes:
```bash
cd /home/admin/ARC
git pull
```

### Update Config Paths (if needed):
```bash
cd /home/admin/ARC
./generate_config.sh
```

### Setup Auto-Start:
```bash
cd /home/admin/ARC
./setup_autostart.sh
```

### Install/Update Dependencies:
```bash
cd /home/admin/ARC
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-linux.txt
```

## Auto-Start Management

### Enable Auto-Start (Desktop Method):
```bash
mkdir -p ~/.config/autostart
cp /home/admin/ARC/arc-launcher.desktop ~/.config/autostart/
chmod +x ~/.config/autostart/arc-launcher.desktop
```

### Enable Auto-Start (Systemd Method):
```bash
sudo cp /home/admin/ARC/arc-launcher.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable arc-launcher.service
sudo systemctl start arc-launcher.service
```

### Check Status:
```bash
sudo systemctl status arc-launcher
```

### View Logs:
```bash
sudo journalctl -u arc-launcher -f
```

### Stop Service:
```bash
sudo systemctl stop arc-launcher
```

### Restart Service:
```bash
sudo systemctl restart arc-launcher
```

### Disable Auto-Start:
```bash
sudo systemctl disable arc-launcher
```

## Icon Setup

### Create Icons Directory:
```bash
sudo mkdir -p /home/admin/Icons
```

### Copy Icons:
```bash
cp -r /home/admin/ARC/ARC_DE/icons/* /home/admin/Icons/
```

### Verify Icons:
```bash
ls -l /home/admin/Icons/
```

## Troubleshooting

### Test Icon Loading:
```bash
cd /home/admin/ARC
python test_icons.py
```

### Check Virtual Environment:
```bash
ls -la /home/admin/ARC/venv/bin/python
```

### Verify Config:
```bash
cat /home/admin/ARC/config/arc.yaml | grep "cd /home/admin/ARC"
```

### Test App Manually:
```bash
cd /home/admin/ARC/music_player
../venv/bin/python main.py
```

## Quick Fixes

### Icons Not Loading:
```bash
sudo mkdir -p /home/admin/Icons
cp -r /home/admin/ARC/ARC_DE/icons/* /home/admin/Icons/
```

### Apps Not Launching:
```bash
cd /home/admin/ARC
./generate_config.sh
```

### Service Not Starting:
```bash
sudo systemctl daemon-reload
sudo systemctl restart arc-launcher
sudo journalctl -u arc-launcher -n 50
```

## File Locations

- **Project Root:** `/home/admin/ARC`
- **Virtual Environment:** `/home/admin/ARC/venv`
- **Config File:** `/home/admin/ARC/config/arc.yaml`
- **Icons:** `/home/admin/Icons/`
- **Launcher:** `/home/admin/ARC/launcher.py`

## Quick Alias (Optional)

Add to `~/.bashrc`:
```bash
echo 'alias arc="cd /home/admin/ARC && source venv/bin/activate"' >> ~/.bashrc
source ~/.bashrc
```

Then just type `arc` to activate environment and go to project root!

