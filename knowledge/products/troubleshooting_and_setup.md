# NovaGear Product Troubleshooting and Setup Guide

## Wireless Audio and Power Troubleshooting

### NovaBuds Pro 2 Bluetooth Pairing Error ERR-BT-104
Error code `ERR-BT-104` indicates a Bluetooth handshake timeout between the NovaBuds Pro 2 (SKU: NG-ANC-700) and the host device (smartphone, tablet, or laptop). This typically occurs when previous pairing caches conflict or when the earbuds attempt simultaneous connection beyond their 2-device multipoint limit.
- **Resolution Procedure:**
  1. Place both NovaBuds Pro 2 earbuds inside the charging case and keep the lid open.
  2. Press and hold the circular setup button located on the rear of the charging case for exactly 10 seconds.
  3. Release the button when the front LED indicator flashes amber three times, then pulses white.
  4. On the host device, open Bluetooth settings, select "Forget This Device" for NovaBuds Pro 2, toggle Bluetooth off and on, and initiate a fresh scan. Select "NovaBuds Pro 2" to re-establish a secure Bluetooth 5.3 connection.

### NovaBuds Pro 2 Audio Drift or Mono Audio Output
If audio plays from only one earbud or if volume levels between the left and right earbuds drift out of balance:
- **Resolution Procedure:**
  1. Inspect the infrared optical in-ear detection sensors located on the inner stem of each earbud. Dust, earwax, or moisture on the sensor can trick the earbud into pausing audio playback. Gently wipe the sensor window with a dry microfiber cloth or cotton swab dampened with 70% isopropyl alcohol.
  2. Place both earbuds into the case and close the lid for 15 seconds to allow internal firmware synchronization.
  3. Ensure the earbud contact pins inside the case are free of debris to guarantee balanced charging levels.

### NovaPower 65W GaN Overheat Thermal Cutoff ERR-PWR-209
The NovaPower 65W GaN Dual Charger (SKU: NG-PWR-065) includes an intelligent thermal safety circuit. If internal temperatures exceed 75°C (167°F) due to restricted airflow, heavy sustained 65W power delivery, or direct sunlight, the charger triggers error state `ERR-PWR-209` and cuts power to protect connected devices.
- **Resolution Procedure:**
  1. Immediately unplug the NovaPower charger from the wall outlet and disconnect all USB-C charging cables.
  2. Allow the unit to cool in a well-ventilated room for at least 10 minutes.
  3. Verify that your USB-C cable is certified for 100W/5A with an integrated E-Marker chip, as damaged or uncertified cables cause high electrical resistance and heat buildup.
  4. Reconnect to the wall outlet; the green LED power indicator will illuminate, signaling normal operation.

## Smart Home Device Troubleshooting

### NovaSense Smart Hub Synchronization Error ERR-SYNC-501
Error code `ERR-SYNC-501` occurs when the NovaSense Smart Hub (SKU: NG-HUB-01) fails to commission a Matter-over-Thread or Zigbee 3.0 sub-device within the 3-minute pairing window.
- **Resolution Procedure:**
  1. Confirm that your home Wi-Fi network's 2.4GHz band is broadcasting and that client device isolation (AP isolation) is disabled in your router settings.
  2. Ensure the sub-device being paired is located within 15 feet of the NovaSense Hub during initial commissioning.
  3. Reboot the NovaSense Hub by power-cycling the USB-C cable, or initiate an in-app reboot via the NovaGear App under Settings > Network Diagnostics.
  4. If `ERR-SYNC-501` persists, initiate a Matter fabric reset: press the recessed pinhole button on the bottom of the hub for 5 seconds until the status ring pulses amber.

### NovaSense Smart Hub LED Status Ring Indicator Diagnostics
The circular LED light ring on the NovaSense Smart Hub (SKU: NG-HUB-01) communicates real-time hardware status:
- **Solid Blue:** Connected to local network and cloud services; all Matter and Zigbee mesh networks operating normally.
- **Pulsing Amber:** Pairing / Discovery mode active; ready to pair new Matter, Thread, or Zigbee accessories.
- **Solid Red:** Network communication failure. Indicates Ethernet disconnection, incorrect Wi-Fi credentials, or IP address conflict.
- **Blinking Green:** Over-The-Air (OTA) firmware update in progress. **Do not unplug** the power cable while green LED flashes; update completes in 2 to 4 minutes.

## Ergonomic Workspace Furniture Calibration

### ErgoLift Standing Desk Error Code E01 and Reset Procedure
When the digital LED handset on the ErgoLift Standing Desk (SKU: NG-DSK-420) displays error code `E01` (or `rES`), it signifies that the dual lifting motors have lost leg height synchronization or that the active gyro anti-collision sensor detected uneven resistance.
- **Reset Procedure:**
  1. Remove any obstacles situated beneath the desk frame or tabletop.
  2. Press and hold the **Down Arrow (▼)** button on the digital handset continuously. The desk will descend to its lowest mechanical point (28 inches).
  3. Continue holding the **Down Arrow** button for 7 additional seconds. The desk will slightly rebound upward and the LED display will flash `rES`, followed by an audible confirmation beep and the height readout `28.0`.
  4. The motors are now recalibrated and ready for normal programmed memory operation.
