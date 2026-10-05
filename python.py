










import streamlit as st
import serial
import time
import pandas as pd

# =====================================================
# SERIAL PORT
# =====================================================
ser = serial.Serial('COM9', 115200, timeout=1)

# GIVE ESP TIME TO RESET
time.sleep(2)

# =====================================================
# PAGE TITLE
# =====================================================
st.title("Smart Street Light Dashboard")

# =====================================================
# ENERGY VARIABLES
# =====================================================
total_energy_mWh_1 = 0
total_energy_mWh_2 = 0

# =====================================================
# TRADITIONAL STREET LIGHT VARIABLES
# =====================================================
demo_voltage = 5.14
demo_current = 7.0  # mA PER BULB

demo_total_energy = 0

# =====================================================
# TIMER
# =====================================================
last_time = time.time()

# =====================================================
# LIVE PLACEHOLDER
# =====================================================
placeholder = st.empty()

# =====================================================
# MAIN LOOP
# =====================================================
while True:

    try:

        # =================================================
        # READ SERIAL DATA
        # =================================================
        line = ser.readline().decode('utf-8', errors='ignore').strip()

        # FORMAT:
        # voltage1,current1,voltage2,current2
        v1, c1, v2, c2 = line.split(",")

        # =================================================
        # CONVERT TO FLOAT
        # =================================================
        v1 = float(v1)
        c1 = float(c1)

        v2 = float(v2)
        c2 = float(c2)

        # =================================================
        # POWER CALCULATION
        # =================================================
        p1_mw = v1 * c1
        p2_mw = v2 * c2

        # =================================================
        # TIME
        # =================================================
        current_time = time.time()

        elapsed_hours = (current_time - last_time) / 3600.0

        last_time = current_time

        # =================================================
        # ENERGY CALCULATION
        # =================================================
        total_energy_mWh_1 += p1_mw * elapsed_hours
        total_energy_mWh_2 += p2_mw * elapsed_hours

        # =================================================
        # TOTAL UNITS
        # =================================================
        total_units_1 = total_energy_mWh_1 / 1000000.0
        total_units_2 = total_energy_mWh_2 / 1000000.0

        # =================================================
        # TRADITIONAL STREET LIGHT (6 BULBS)
        # =================================================

        # TOTAL CURRENT FOR 6 BULBS
        traditional_current = demo_current * 6

        # TOTAL POWER FOR 6 BULBS
        traditional_power_mw = demo_voltage * traditional_current

        # ENERGY UPDATE
        demo_total_energy += traditional_power_mw * elapsed_hours

        # TOTAL UNITS
        traditional_units = demo_total_energy / 1000000.0

        # SINGLE LIVE ROW
        power_history = [{
            "Time": time.strftime("%H:%M:%S"),
            "Voltage (V)": round(demo_voltage, 2),
            "Current Total (mA)": round(traditional_current, 2),
            "Power Total (mW)": round(traditional_power_mw, 2),
            "Power Used Total (mWh)": round(demo_total_energy, 4),
            "Units Total (kWh)": round(traditional_units, 8)
        }]

        # =================================================
        # DASHBOARD UI
        # =================================================
        with placeholder.container():

            # =================================================
            # SECTION 1
            # =================================================
            st.subheader("Section 1")

            col1, col2, col3 = st.columns(3)

            col1.metric("Voltage 1", f"{v1:.2f} V")
            col2.metric("Current 1", f"{c1:.2f} mA")
            col3.metric("Power 1", f"{p1_mw:.2f} mW")

            col4, col5 = st.columns(2)

            col4.metric(
                "Power Used 1",
                f"{total_energy_mWh_1:.4f} mWh"
            )

            col5.metric(
                "Units Used 1",
                f"{total_units_1:.8f} kWh"
            )

            # ALERTS
            if c1 > 60:
                st.error("⚠️ Theft Detected in Section 1")

            if c1 <= -0.5:
                st.warning("⚠️ Fault Detected in Section 1")

            st.divider()

            # =================================================
            # SECTION 2
            # =================================================
            st.subheader("Section 2")

            col6, col7, col8 = st.columns(3)

            col6.metric("Voltage 2", f"{v2:.2f} V")
            col7.metric("Current 2", f"{c2:.2f} mA")
            col8.metric("Power 2", f"{p2_mw:.2f} mW")

            col9, col10 = st.columns(2)

            col9.metric(
                "Power Used 2",
                f"{total_energy_mWh_2:.4f} mWh"
            )

            col10.metric(
                "Units Used 2",
                f"{total_units_2:.8f} kWh"
            )

            # ALERTS
            if c2 > 60:
                st.error("⚠️ Theft Detected in Section 2")

            if c2 <= -0.5:
                st.warning("⚠️ Fault Detected in Section 2")

            st.divider()

            # =================================================
            # COMBINED SMART STREET LIGHT TABLE
            # =================================================
            st.subheader("Smart Street Light Combined Consumption")

            combined_voltage = v2
            combined_current = c1 + c2
            combined_power = p1_mw + p2_mw
            combined_energy = total_energy_mWh_1 + total_energy_mWh_2
            combined_units = total_units_1 + total_units_2

            combined_table = pd.DataFrame([{
                "Voltage Total (V)": round(combined_voltage, 2),
                "Current Total (mA)": round(combined_current, 2),
                "Power Total (mW)": round(combined_power, 2),
                "Power Used Total (mWh)": round(combined_energy, 4),
                "Units Total (kWh)": round(combined_units, 8)
            }])

            st.table(combined_table)

            st.divider()

            # =================================================
            # TRADITIONAL STREET LIGHT TABLE
            # =================================================
            st.subheader("Traditional Street Light Power Consumption Table {6 bulbs}")

            df = pd.DataFrame(power_history)

            st.table(df)

            st.divider()

            # =================================================
            # POWER SAVING COMPARISON TABLE
            # =================================================
            st.subheader("Power Saving Analysis")

            # POWER SAVED
            power_saved = traditional_power_mw - combined_power

            # PERCENTAGE POWER SAVED
            percent_saved = (
                (power_saved / traditional_power_mw) * 100
            )

            # TABLE
            saving_table = pd.DataFrame([{
                "Traditional Power Total (mW)": round(traditional_power_mw, 2),

                "Smart System Power Total (mW)": round(combined_power, 2),

                "Power Saved (mW)": round(power_saved, 2),

                "% Power Saved": round(percent_saved, 2)
            }])

            st.table(saving_table)

    except:
        pass