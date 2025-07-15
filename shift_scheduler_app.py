
import streamlit as st
from datetime import date, timedelta
import calendar
from fpdf import FPDF

st.set_page_config(layout="wide")
st.title("Monthly Shift Scheduler")

names = ["Brandon", "Tony", "Erik"]
year = 2025
month = 8
month_name = calendar.month_name[month]

# Helper to build default schedule
def get_default_schedule():
    start_date = date(year, month, 1)
    end_date = date(year, month, calendar.monthrange(year, month)[1])
    current = start_date
    return {current + timedelta(days=i): "" for i in range((end_date - start_date).days + 1)}

# UI: Calendar input
shift_data = get_default_schedule()
cols = st.columns(7)
for i, (day, name) in enumerate(shift_data.items()):
    col = cols[day.weekday()]
    with col:
        shift_data[day] = st.selectbox(
            f"{day.strftime('%a %d')}", [""] + names, key=day
        )

# Color picker logic
def get_color(name):
    if name == "Brandon":
        return (0, 0, 255)
    elif name == "Tony":
        return (200, 0, 0)
    elif name == "Erik":
        return (0, 130, 0)
    else:
        return (0, 0, 0)

# PDF class to draw calendar
class CalendarPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, f"{month_name} {year} - Shift Calendar", ln=True, align="C")

    def draw_calendar(self, year, month, schedule):
        self.set_font("Arial", "B", 10)
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        cell_w = 40
        cell_h = 25

        for day in days:
            self.cell(cell_w, 10, day, border=1, align="C", fill=True)
        self.ln()

        cal = calendar.Calendar(firstweekday=6)
        weeks = cal.monthdatescalendar(year, month)

        for week in weeks:
            for date_cell in week:
                x = self.get_x()
                y = self.get_y()
                if date_cell.month == month:
                    name = schedule.get(date_cell, "")
                    r, g, b = get_color(name)
                    self.set_draw_color(0)
                    self.set_fill_color(255, 255, 255)
                    self.rect(x, y, cell_w, cell_h)
                    self.set_xy(x + 2, y + 2)
                    self.set_text_color(0)
                    self.cell(cell_w - 4, 5, str(date_cell.day), ln=1)
                    self.set_text_color(r, g, b)
                    self.set_xy(x + 2, y + 10)
                    self.set_font("Arial", "", 10)
                    self.multi_cell(cell_w - 4, 5, name)
                    self.set_xy(x + cell_w, y)
                else:
                    self.cell(cell_w, cell_h, "", border=1)
            self.ln()

# PDF Generation
if st.button("Generate PDF"):
    pdf = CalendarPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.draw_calendar(year, month, shift_data)
    pdf_path = "shift_scheduler_app_calendar_output.pdf"
    pdf.output(pdf_path)
    with open(pdf_path, "rb") as f:
        st.download_button("Download Calendar PDF", f, file_name=pdf_path)
