#!/usr/bin/env python3
"""
ESP32 Wireless Stream Deck & Audio Mixer - PC Companion Server
Listens for WebSocket events from ESP32 to control application volume and execute hotkeys/macros.
"""

import asyncio
import json
import os
import sys
import subprocess
import websockets

# Platform detection
IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

# Audio controls on Windows
if IS_WINDOWS:
    try:
        from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, IAudioEndpointVolume
        from ctypes import cast, POINTER
        WINDOWS_AUDIO_AVAILABLE = True
    except ImportError:
        WINDOWS_AUDIO_AVAILABLE = False
        print("[ADVARSEL] 'pycaw' biblioteket er ikke installeret. Kør: pip install pycaw comtypes")
else:
    WINDOWS_AUDIO_AVAILABLE = False

# Keyboard input simulation
try:
    import keyboard
    KEYBOARD_LIB = "keyboard"
except ImportError:
    try:
        from pynput.keyboard import Controller, Key
        keyboard_ctrl = Controller()
        KEYBOARD_LIB = "pynput"
    except ImportError:
        KEYBOARD_LIB = None
        print("[ADVARSEL] Hverken 'keyboard' eller 'pynput' er installeret. Kør: pip install keyboard")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load_config():
    """Indlæser konfiguration fra config.json."""
    if not os.path.exists(CONFIG_PATH):
        print(f"[FEJL] Kunne ikke finde konfigurationsfilen: {CONFIG_PATH}")
        return {"channels": [], "keys": {}}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[FEJL] Fejl under indlæsning af config.json: {e}")
        return {"channels": [], "keys": {}}


def set_master_volume(percent):
    """Sætter master volumen på PC."""
    volume_scalar = max(0.0, min(1.0, percent / 100.0))
    if IS_WINDOWS and WINDOWS_AUDIO_AVAILABLE:
        try:
            speakers = AudioUtilities.GetSpeakers()
            interface = speakers.Activate(IAudioEndpointVolume._iid_, 0, None)
            vol_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
            vol_ctrl.SetMasterVolumeLevelScalar(volume_scalar, None)
            print(f"[AUDIO] Master volumen -> {percent}%")
        except Exception as e:
            print(f"[AUDIO FEJL] Master volumen kunne ikke ændres: {e}")
    elif IS_MACOS:
        # macOS volumestyring via osascript
        try:
            subprocess.run(
                ["osascript", "-e", f"set volume output volume {percent}"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"[AUDIO macOS] Master volumen -> {percent}%")
        except Exception as e:
            print(f"[AUDIO macOS FEJL] {e}")
    else:
        print(f"[MOCK AUDIO] Master sat til {percent}% (Styresystem ikke understøttet direkte)")


def set_app_volume(app_name, percent):
    """Sætter lydstyrken for et specifikt program på Windows via dets procesnavn."""
    if not (IS_WINDOWS and WINDOWS_AUDIO_AVAILABLE):
        print(f"[MOCK AUDIO] App '{app_name}' volumen sat til {percent}%")
        return

    volume_scalar = max(0.0, min(1.0, percent / 100.0))
    target_lower = app_name.lower().strip()

    try:
        sessions = AudioUtilities.GetAllSessions()
        matched = False
        for session in sessions:
            if session.Process:
                proc_name = session.Process.name().lower()
                if target_lower in proc_name:
                    volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                    volume.SetMasterVolume(volume_scalar, None)
                    matched = True

        if matched:
            print(f"[AUDIO] App '{app_name}' volumen -> {percent}%")
        else:
            # Programmet kører måske ikke lige nu
            pass
    except Exception as e:
        print(f"[AUDIO FEJL] Kunne ikke sætte volumen for '{app_name}': {e}")


def execute_action(key_id):
    """Udfører en handling baseret på tastenummer og config.json."""
    config = load_config()
    keys_conf = config.get("keys", {})
    key_str = str(key_id)

    if key_str not in keys_conf:
        print(f"[STREAMDECK] Tast {key_id} har ingen konfigureret handling i config.json.")
        return

    item = keys_conf[key_str]
    action = item.get("action")
    desc = item.get("name", f"Key {key_id}")
    print(f"[STREAMDECK] Udfører tast {key_id} ({desc}): action='{action}'")

    if KEYBOARD_LIB == "keyboard":
        if action == "hotkey":
            keys = item.get("keys", [])
            combo = "+".join(keys)
            keyboard.send(combo)
        elif action == "media_play_pause":
            keyboard.send("play/pause media")
        elif action == "media_next":
            keyboard.send("next track")
        elif action == "media_prev":
            keyboard.send("previous track")
        elif action == "media_mute":
            keyboard.send("volume mute")
        elif action == "launch":
            cmd = item.get("cmd")
            if cmd:
                subprocess.Popen(cmd, shell=True)
    elif KEYBOARD_LIB == "pynput":
        # Fallback for systemer hvor keyboard lib ikke er tilgængeligt
        if action == "launch":
            cmd = item.get("cmd")
            if cmd:
                subprocess.Popen(cmd, shell=True)
        else:
            print(f"[INFO] Handling '{action}' understøttes bedst på Windows med 'keyboard' pakken.")
    else:
        print(f"[ADVARSEL] Ingen tastatursimulator installeret til at udføre handling '{action}'.")


async def handler(websocket):
    client_ip = websocket.remote_address[0] if websocket.remote_address else "Ukendt"
    print(f"\n[+] Ny ESP32 forbundet fra: {client_ip}")

    config = load_config()
    channels = config.get("channels", [])

    # Send kanal-labels til ESP32 ved opkobling så OLED skærmen matcher config.json
    labels = [ch.get("label", f"CH{i+1}")[:3].upper() for i, ch in enumerate(channels[:4])]
    while len(labels) < 4:
        labels.append("---")

    init_payload = json.dumps({"labels": labels})
    await websocket.send(init_payload)
    print(f"[+] Sendte display-labels til ESP32: {labels}")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                print(f"[!] Ugyldig JSON modtaget: {message}")
                continue

            msg_type = data.get("type")

            # Håndter tastetryk
            if msg_type == "key":
                key_num = data.get("key")
                state = data.get("state", "down")
                if state == "down":
                    execute_action(key_num)

            # Håndter potentiometer ændringer
            elif msg_type == "pot":
                pot_idx = data.get("pot")
                val = data.get("val")

                if pot_idx is not None and 0 <= pot_idx < len(channels):
                    target = channels[pot_idx].get("target", "").lower().strip()
                    if target == "master":
                        set_master_volume(val)
                    else:
                        set_app_volume(target, val)

    except websockets.exceptions.ConnectionClosed:
        print(f"[-] ESP32 forbindelsen lukkede ({client_ip}).")
    except Exception as e:
        print(f"[!] Uventet fejl: {e}")


async def main():
    port = 8765
    print("=" * 60)
    print("  ESP32 Trådløs Stream Deck & Audio Mixer PC Server")
    print("=" * 60)
    print(f"Server lytter på: 0.0.0.0:{port}")
    print("Tjek at din ESP32's 'PC_HOST' IP matcher denne computers lokale IP.")
    print("Tryk Ctrl+C for at stoppe serveren.\n")

    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # Kør for evigt


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stoppet af bruger.")
