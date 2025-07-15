
from datetime import datetime
import calendar
import random
import pandas as pd
from fpdf import FPDF
import streamlit as st
import io

# --- Constants ---
NAMES = ["Brandon", "Erik", "Tony"]
WEEKEND_DAYS = ["Friday", "Saturday", "Sunday"]

# --- Sidebar ---
st.sidebar.title("📅 Calendar Settings")
year = st.sidebar.selectbox("Select Year", list(range(2024, 2031)), index=1)
month = st.sidebar.selectbox("Select Month", list(calendar.month_name)[1:], index=datetime.now().month - 1)
even_dist = st.sidebar.checkbox("Evenly distribute other unselected off days")
auto_fill = st.sidebar.checkbox("Auto-assign names to unselected off days")
require_weekend = st.sidebar.checkbox("Try to give each person a full weekend off")

# --- Calendar Setup ---
month_index = list(calendar.month_name).index(month)
num_days = calendar.monthrange(year, month_index)[1]
days = [datetime(year, month_index, d) for d in range(1, num_days + 1)]

# --- DataFrame to store shifts ---
df = pd.DataFrame({
    "Date": [d.strftime("%Y-%m-%d") for d in days],
    "Day": [d.strftime("%A") for d in days],
    "Off": [None] * len(days)
})

st.title("📆 Shift Scheduler - Color-Coded OFF Days")

# --- UI Grid for shift selection ---
for i, row in df.iterrows():
    col1, col2 = st.columns([1.2, 2])
    col1.markdown(f"**{row['Date']} ({row['Day']})**")
    df.at[i, "Off"] = col2.selectbox(f"Off_{i}", [""] + NAMES, key=f"off_{i}")

# --- Auto-fill logic ---
def assign_weekends_first(df):
    assigned = df.copy()
    name_counts = {name: 0 for name in NAMES}
    weekends = []

    # Group weekend days
    for i in range(len(df) - 2):
        if df.at[i, "Day"] == "Friday" and df.at[i + 1, "Day"] == "Saturday" and df.at[i + 2, "Day"] == "Sunday":
            weekends.append((i, i + 1, i + 2))

    random.shuffle(weekends)
    used = set()

    for i1, i2, i3 in weekends:
        name = min(name_counts, key=name_counts.get)
        if not assigned.at[i1, "Off"]: assigned.at[i1, "Off"] = name
        if not assigned.at[i2, "Off"]: assigned.at[i2, "Off"] = name
        if not assigned.at[i3, "Off"]: assigned.at[i3, "Off"] = name
        name_counts[name] += 3
        used.add(name)
        if len(used) == 3:
            break

    return assigned

def even_distribution(df):
    name_counts = {name: 0 for name in NAMES}
    for name in df["Off"]:
        if name in name_counts:
            name_counts[name] += 1
    for i, row in df.iterrows():
        if not row["Off"]:
            name = min(name_counts, key=name_counts.get)
            df.at[i, "Off"] = name
            name_counts[name] += 1
    return df

if require_weekend:
    df = assign_weekends_first(df)

if even_dist:
    df = even_distribution(df)

if auto_fill:
    for i, row in df.iterrows():
        if not row["Off"]:
            df.at[i, "Off"] = random.choice(NAMES)

# --- PDF Generator ---
def generate_pdf(df, month, year):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"{month} {year} - Shift Schedule (Color-Coded Off Days)", ln=True, align="C")
    pdf.ln(10)

    colors = {"Brandon": (0, 102, 204), "Erik": (0, 153, 76), "Tony": (204, 0, 0)}

    for _, row in df.iterrows():
        name = row["Off"]
        color = colors.get(name, (0, 0, 0))
        pdf.set_text_color(*color)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"{row['Date']} ({row['Day']}): {name if name else '—'}", ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- Download Button ---
if st.button("📄 Generate PDF"):
    pdf = generate_pdf(df, month, year)
    st.download_button(
        label="📥 Download Schedule PDF",
        data=pdf,
        file_name=f"{month}_{year}_Shift_Schedule.pdf",
        mime="application/pdf"
    )
