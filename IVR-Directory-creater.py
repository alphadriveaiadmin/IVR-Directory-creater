import json
import streamlit as st

st.set_page_config(page_title="Dealership Directory Formatter", layout="wide")

st.title("📞 Dealership Directory Formatter")
st.write("Paste your raw JSON below to generate a formatted phone directory list.")

# --- Input ---
raw_json = st.text_area("Paste JSON here", height=300)

if st.button("Generate Directory"):
    try:
        data = json.loads(raw_json)

        output_lines = []

        # --- Map of department-level phone numbers ---
        dept_phone_map = {
            d["department"]: d["phone_number"]
            for d in data.get("department_phone_numbers", [])
        }

        # --- Group employees by department ---
        dept_employees = {}
        for dept in data.get("department_employees", []):
            department = dept.get("department", "").strip()
            for emp in dept.get("employees", []):
                name = emp.get("contact_name", "").strip()
                position = emp.get("employee_position", "").strip()
                phone = emp.get("office_number", "").strip()
                if not department:
                    continue
                dept_employees.setdefault(department, []).append(
                    (name, position, phone)
                )

        # --- Sort and format output ---
        for department, employees in dept_employees.items():
            dept_header = f"{department} → {dept_phone_map.get(department, '').strip()}"
            output_lines.append(dept_header)

            for name, position, phone in employees:
                if name and phone:
                    output_lines.append(f"{name} ({position}) → {phone}")
            output_lines.append("")  # blank line between departments

        # --- Combine and show result ---
        formatted_output = "\n".join(output_lines).strip()
        st.text_area("📋 Formatted Directory", formatted_output, height=500)
        st.download_button(
            "📥 Download as TXT",
            data=formatted_output,
            file_name="formatted_directory.txt",
            mime="text/plain",
        )

    except Exception as e:
        st.error(f"Error processing JSON: {e}")
