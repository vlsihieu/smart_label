# Temp Label Manager — Phase 1 v3 (PyQt5)

## Run (Windows)

1. Install Python 3.10–3.12 and Qt Designer 5 (provided with PyQt5 tools or your Qt installation).
2. Unzip this project, open a terminal in its directory, then run:

```bat
py -m pip install -r requirements.txt
py main.py
```

## Edit the interface in Qt Designer 5

Open `ui/main_window.ui` for the main shell and `ui/dashboard.ui` for the dashboard layout. Additional views are editable in `ui/device_configuration.ui`, `ui/data_download.ui`, `ui/history_viewer.ui`, `ui/device_information.ui`, and `ui/settings.ui`.

**Dashboard layout**: blue collapsible sidebar; header with thermometer icon; device scan; device information; editable configuration; live-style history chart; incremental transfer simulation; download records and CSV export.

The **☰** hamburger button in the header collapses the blue navigation area to a narrow icon strip. Click again to expand. This behavior is implemented in `main.py` because Qt Designer `.ui` files describe layout rather than Python event handlers.

**Phase 1 limitations:** all devices, configurations, temperature samples and ACK/resume transfers are simulated. This release does NOT communicate over BLE; it does not offer durable SQLite checkpoints and does not verify real CRCs. Qt Designer can edit the `.ui` files, while `main.py` provides the interactive demo.

To connect real devices later, replace the simulator with a Bleak-based GATT protocol implementation.
