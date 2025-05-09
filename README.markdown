# README.md for `create_yom_tov_rules.py`

This Python script automates the creation of SmartThings rules to enable Shabbos mode on a Samsung refrigerator for Yom Tov dates over the next 10 years. It reads a CSV file with Yom Tov dates and generates rules that activate Shabbos mode 18 minutes before sunset, provided a virtual switch is in the "on" state.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [How to Use the Script](#how-to-use-the-script)
4. [CSV File Format](#csv-file-format)
5. [Environment Variables](#environment-variables)
6. [Troubleshooting](#troubleshooting)
7. [Additional Notes](#additional-notes)

---

## Prerequisites

Before using the script, ensure you have:

- **Python 3.x**: Installed on your system.
- **Requests Library**: Install it with `pip install requests`.
- **SmartThings Account**: You’ll need a Personal Access Token (PAT) with the following scopes:

  - `Rules: Write`
  - `Devices: Read`
  - `Locations: Read`
    Create your PAT here: [SmartThings Personal Access Token](https://account.smartthings.com/tokens)

- **Device ID**: The ID of your Samsung refrigerator in SmartThings.  
  Find it here: [SmartThings Devices](https://my.smartthings.com/advanced/devices)
- **Location ID**: The ID of your SmartThings location.  
  Find it here: [SmartThings Locations](https://my.smartthings.com/advanced/locations)
- **Virtual Switch ID**: The ID of a virtual switch device in SmartThings (see [Initial Setup](#initial-setup)).

---

## Initial Setup

### Setting Up a Virtual Environment

To isolate your project's dependencies and ensure reproducibility, it's recommended to use a virtual environment. Here's how to set one up:

1. Create a Virtual Environment:

   - Open a terminal in the script's directory.
   - Run the command:
     ```bash
     python -m venv .venv
     ```

2. Activate the Virtual Environment:

   - On Linux/Mac:

     ```bash
     source .venv/bin/activate
     ```

   - On Windows:

     ```cmd
     .venv\Scripts\activate
     ```

3. Install Dependencies:

   - Once activated, install the required libraries:
     ```bash
     pip install requests
     ```

### Creating a Virtual Switch

The script requires a virtual switch to be in the "on" state to trigger Shabbos mode. Follow these steps to create a virtual switch:

1. Go to [SmartThings Advanced Devices](https://my.smartthings.com/advanced/devices).
2. Click **Add Device** or the **+** icon.
3. Select **Switch** as the device type.
4. Enter a name (e.g., "Yom Tov Switch").
5. Select your location _USE THE SAME LOCATION AS YOUR SHABBOS MODE DEVICE_.
6. Click **Create**.
7. Note the **Device ID** from the device details page for use in the script.

### Setting Up Daily Routines for the Virtual Switch

Create two routines in the SmartThings app to control the virtual switch:

1. **Turn On 18 Minutes Before Sunset**:
   - Open the SmartThings app.
   - Go to **Routines** > **+**.
   - **If**:
     - Condition: **Time** > **Sunset** > **18 minutes** > **Before**.
   - **Then**:
     - Control Devices: Select the virtual switch ("Yom Tov Switch").
     - Set: **Turn On**.
   - Save and name the routine (e.g., "Yom Tov Switch On").
2. **Turn Off at Sunset**:
   - Create another automation.
   - **If**:
     - Condition: **Time** > **Sunset**.
   - **Then**:
     - Control Devices: Select the virtual switch ("Yom Tov Switch").
     - Set: **Turn Off**.
   - Save and name the routine (e.g., "Yom Tov Switch Off").

---

## How to Use the Script

Follow these steps to set up and run the script:

1. **Prepare the CSV File**:

   - Create a file named `yom_tov_dates.csv` (or adjust the script to point to your file’s location).
   - Fill it with Yom Tov dates (see [CSV File Format](#csv-file-format) below).

2. **Set Environment Variables**:

   - Configure the required variables (see [Environment Variables](#environment-variables) below).
   - Example for Unix/macOS:
     ```bash
     export SMARTTHINGS_TOKEN="your_token_here"
     export DEVICE_ID="your_device_id_here"
     export LOCATION_ID="your_location_id_here"
     export VIRTUAL_SWITCH_ID="your_virtual_switch_id_here"
     ```
   - Example for Windows:
     ```cmd
     set SMARTTHINGS_TOKEN=your_token_here
     set DEVICE_ID=your_device_id_here
     set LOCATION_ID=your_location_id_here
     set VIRTUAL_SWITCH_ID=your_virtual_switch_id_here
     ```

3. **Run the Script**:

   - Open a terminal in the script’s directory.
   - Execute:
     ```bash
     python create_yom_tov_rules.py
     ```
   - Watch the console for success messages or errors.

4. **Verify Rules**:
   - Check your SmartThings app or API to confirm the rules were created.

---

## CSV File Format

The script requires a CSV file (`yom_tov_dates.csv`) with these columns:

- `Year`: e.g., `2025`.
- `Yom Tov`: e.g., `Pesach`, `Shavuot`.
- `Start of First Days`: Date in `YYYY-MM-DD` format (e.g., `2025-04-12`).
- `Start of Last Day (After Chol Hamoed)`: Date in `YYYY-MM-DD` format (e.g., `2025-04-20`), or leave blank if not applicable.

**Example:**

```csv
Year,Yom Tov,Start of First Days,Start of Last Day (After Chol Hamoed)
2025,Pesach,2025-04-12,2025-04-20
2025,Shavuot,2025-06-01,
```

---

## Environment Variables

You must set these variables:

- `SMARTTHINGS_TOKEN`: Your SmartThings PAT.
- `DEVICE_ID`: Your refrigerator’s SmartThings device ID.
- `LOCATION_ID`: Your SmartThings location ID.
- `VIRTUAL_SWITCH_ID`: Your virtual switch’s device ID.

Set them in your terminal as shown in the [How to Use the Script](#how-to-use-the-script) section.

---

## Troubleshooting

- **CSV File Not Found**: Ensure `yom_tov_dates.csv` is in the same directory as the script.
- **Date Format Errors**: Use `YYYY-MM-DD` (e.g., `2025-04-12`).
- **API Issues**:
  - **401 Unauthorized**: Verify your token and its scopes.
  - **403 Forbidden**: Check locationId in the query string and deviceId/virtualSwitchId in the request body.
  - **404 Not Found**: Verify device, virtual switch, and location IDs.
  - **429 Too Many Requests**: Increase the delay in the script if needed.
- **Virtual Switch Not Triggering**: Ensure the switch is "on" at the trigger time and routines are set correctly.
- **No Output**: Verify all environment variables are set.

---

## Additional Notes

- **Shabbos Mode Off**: This script only turns Shabbos mode **on**. Create a separate script for turning it **off**.
- **Virtual Switch Dependency**: Rules only trigger if the virtual switch is "on" 18 minutes before sunset.
- **Testing**: Start with a small CSV to test the setup.
- **Time Zone**: Adjust the `TIME_ZONE` variable in the script if it doesn’t match your location.
- **SmartThings Advanced Page**: View and manage your devices, locations, rules, and more at [SmartThings Advanced](https://my.smartthings.com/advanced).
- **SmartThings API Documentation**: Learn more about the available API endpoints at the [SmartThings API Docs](https://developer.smartthings.com/docs/api/public).

---

This README provides everything you need to get started. Happy automating!
