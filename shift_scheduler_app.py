
import streamlit as st
from fpdf import FPDF
import calendar
import datetime

# --- CONFIGURATION ---
NAMES = ["Brandon", "Erik", "Tony"]
COLOR_MAP = {
    "Brandon": (255, 204, 204),
    "Erik": (204, 230, 255),
    "Tony": (204, 255, 204)
}

# --- SESSION STATE INIT ---
if "schedule" not in st.session_state:
    st.session_state.schedule = {}

# --- UI: MONTH/YEAR SELECT ---
st.title("Shift Scheduler - Color-Coded OFF Days")
st.caption("Click a day, select who's OFF. PDF will color code and show who’s ON automatically.")

year = st.number_input("Year", min_value=2023, max_value=2100, value=2025)
month = st.selectbox("Month", list(calendar.month_name)[1:], index=7)  # August default

month_num = list(calendar.month_name).index(month)
_, num_days = calendar.monthrange(year, month_num)
first_weekday = calendar.monthrange(year, month_num)[0]  # 0 = Monday

# --- UI: Calendar Grid ---
st.markdown("### Click a day and select who is OFF")

cols = st.columns(7)
day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
for i, name in enumerate(day_names):
    cols[i].markdown(f"**{name}**")

weeks = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month_num)
for week in weeks:
    row = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            row[i].markdown(" ")
        else:
            key = f"{year}-{month_num:02d}-{day:02d}"
            current_off = st.session_state.schedule.get(key, "")
            with row[i]:
                st.markdown(f"**{day}**")
                selected = st.selectbox("", ["", *NAMES], index=NAMES.index(current_off) + 1 if current_off else 0, key=key)
                if selected:
                    st.session_state.schedule[key] = selected
                elif key in st.session_state.schedule:
                    del st.session_state.schedule[key]

# --- PDF GENERATION ---
st.markdown("---")
if st.button("📄 Generate PDF"):
    class ShiftPDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 16)
            self.cell(0, 10, f"{month} {year} Schedule - Color-Coded Off Days", ln=True, align="C")
            self.ln(2)

            self.set_font("Arial", "B", 11)
            labels = ["Brandon OFF", "Erik OFF", "Tony OFF"]
            widths = [40, 35, 35]
            spacing = 10
            x_center = self.w / 2
            total_width = sum(widths) + spacing * 2
            start_x = x_center - total_width / 2
            y = self.get_y()

            for name, color, w in zip(NAMES, COLOR_MAP.values(), widths):
                self.set_fill_color(*color)
                self.rect(start_x, y, w, 8, 'F')
                self.set_xy(start_x, y + 1)
                self.cell(w, 6, f"{name} OFF", align="C")
                start_x += w + spacing
            self.set_y(y + 12)

        def calendar(self, schedule):
            self.set_font("Arial", "B", 12)
            col_width = 38
            for day in day_names:
                self.cell(col_width, 12, day, border=1, align='C')
            self.ln()

            self.set_font("Arial", size=9)
            for week in weeks:
                y_start = self.get_y()
                max_lines = 0
                for i, day in enumerate(week):
                    x = self.get_x() + i * col_width
                    self.set_xy(x, y_start)
                    if day == 0:
                        self.multi_cell(col_width, 6, "", border=1)
                    else:
                        key = f"{year}-{month_num:02d}-{day:02d}"
                        off_name = schedule.get(key, "")
                        if off_name:
                            on_names = [n for n in NAMES if n != off_name]
                            content = f"{day} {off_name} OFF\n{', '.join(on_names)} ON"
                            fill_color = COLOR_MAP[off_name]
                        else:
                            content = f"{day} All ON"
                            fill_color = (255, 255, 255)
                        self.set_fill_color(*fill_color)
                        self.multi_cell(col_width, 6, content, border=1, fill=True)
                        max_lines = max(max_lines, len(content.split("\n")))
                self.set_y(y_start + max_lines * 6)

    pdf = ShiftPDF(orientation="L")
    pdf.add_page()
    pdf.calendar(st.session_state.schedule)

    filename = f"{month}_{year}_Shift_Schedule.pdf"
    pdf.output(filename)
    with open(filename, "rb") as f:
        st.download_button("📥 Download PDF", f, file_name=filename, mime="application/pdf")
