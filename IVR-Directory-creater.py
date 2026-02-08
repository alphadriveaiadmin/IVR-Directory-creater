import json
import streamlit as st
import requests

st.set_page_config(page_title="Dealership Directory Formatter", layout="wide")

st.title("📞 IVR Directory Creator")
st.write("Paste your campaign ID to generate IVR directory")

# --- Input ---
campaign_col, _ = st.columns([1, 3])
with campaign_col:
    campaign_id = st.text_input(
        "Campaign ID",
        max_chars=4,
        placeholder="1234",
        help="Enter the 4-digit campaign ID for the webhook.",
    )

raw_json = ""

if st.button("Generate IVR Directory"):
    if not campaign_id.strip():
        error_message = "Please enter a 4-digit campaign ID before generating."
    elif not campaign_id.isdigit() or len(campaign_id) != 4:
            error_message = "Campaign ID must be exactly 4 digits."
    else:
        try:
            response = requests.post(
                "https://apps.dgaauto.com/virtualAgentData/webhook",
                params={"campaign_id": campaign_id},
                timeout=15,
            )
            response.raise_for_status()
            if response.headers.get("content-type", "").lower().startswith("application/json"):
                raw_json = json.dumps(response.json())
            else:
                raw_json = response.text

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
