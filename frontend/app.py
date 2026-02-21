import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Greenwashing Risk Detector", page_icon="🌱", layout="wide")

st.title("🌱 Greenwashing Risk Detector")
st.markdown(
    "Analyze a company's ESG disclosures for potential greenwashing risk using "
    "AI-powered semantic search and retrieval-augmented generation."
)

st.divider()

st.subheader("Upload ESG Document")

SECTOR_OPTIONS = [
    "Unknown",
    "Energy",
    "Utilities",
    "Materials",
    "Industrials",
    "ConsumerDiscretionary",
    "ConsumerStaples",
    "HealthCare",
    "Financials",
    "InformationTechnology",
    "CommunicationServices",
    "RealEstate",
    "Other",
]

DOC_TYPE_OPTIONS = [
    "ESGReport",
    "AnnualReport",
    "SustainabilityReport",
    "ClimateReport",
    "ImpactReport",
    "CSRReport",
    "Other",
]

with st.form("upload_esg_form"):
    upload_company = st.text_input("Company", placeholder="e.g. NewEnergyCo")
    upload_sector_choice = st.selectbox("Sector", options=SECTOR_OPTIONS, index=0)
    upload_sector_other = ""
    if upload_sector_choice == "Other":
        upload_sector_other = st.text_input("Custom Sector")

    upload_doc_type_choice = st.selectbox("Document Type", options=DOC_TYPE_OPTIONS, index=0)
    upload_doc_type_other = ""
    if upload_doc_type_choice == "Other":
        upload_doc_type_other = st.text_input("Custom Document Type")

    upload_file = st.file_uploader("ESG file (.txt or .pdf)", type=["txt", "pdf"])
    upload_submit = st.form_submit_button("Upload and Ingest")

if upload_submit:
    sector_value = upload_sector_other.strip() if upload_sector_choice == "Other" else upload_sector_choice
    doc_type_value = (
        upload_doc_type_other.strip() if upload_doc_type_choice == "Other" else upload_doc_type_choice
    )

    if not upload_company.strip() or not upload_file:
        st.warning("Please provide a company name and choose a .txt or .pdf file.")
    elif upload_sector_choice == "Other" and not sector_value:
        st.warning("Please provide a custom sector.")
    elif upload_doc_type_choice == "Other" and not doc_type_value:
        st.warning("Please provide a custom document type.")
    else:
        try:
            content_type = "application/pdf" if upload_file.name.lower().endswith(".pdf") else "text/plain"
            files = {"file": (upload_file.name, upload_file.getvalue(), content_type)}
            data = {
                "company": upload_company.strip(),
                "sector": sector_value,
                "doc_type": doc_type_value,
            }
            res = requests.post(f"{API_URL}/upload/esg", data=data, files=files, timeout=180)
            if res.status_code == 404:
                # Backward compatibility for alternate backend route naming.
                res = requests.post(f"{API_URL}/upload", data=data, files=files, timeout=180)
            if res.status_code == 200:
                payload = res.json()
                st.success(
                    f"Uploaded and ingested: {payload['saved_as']} "
                    f"({payload['chars']} chars)"
                )
            elif res.status_code == 404:
                st.error(
                    "Upload endpoint not found. Restart backend so new upload routes are loaded: "
                    "`/upload/esg` and `/upload`."
                )
            else:
                st.error(f"Upload failed: {res.status_code} — {res.text}")
        except requests.ConnectionError:
            st.error(
                "Could not connect to the backend API. "
                "Make sure the FastAPI server is running on http://localhost:8000."
            )
        except Exception as e:
            st.error(f"Unexpected upload error: {e}")

st.divider()

company = st.text_input("Enter Company Name", placeholder="e.g. GreenCorp")

if st.button("Analyze", type="primary", disabled=not company):
    with st.spinner("Analyzing ESG disclosures..."):
        try:
            res = requests.get(f"{API_URL}/analyze/{company}", timeout=120)

            if res.status_code == 404:
                st.warning(f"No ESG data found for **{company}**. Make sure data has been ingested.")
            elif res.status_code != 200:
                st.error(f"API error: {res.status_code} — {res.text}")
            else:
                data = res.json()
                score = data["risk_score"]

                col1, col2 = st.columns([1, 2])

                with col1:
                    if score < 30:
                        color = "green"
                        label = "Low Risk"
                    elif score < 60:
                        color = "orange"
                        label = "Medium Risk"
                    else:
                        color = "red"
                        label = "High Risk"

                    st.metric(label="Greenwashing Risk Score", value=f"{score}/100")
                    st.markdown(
                        f"<h3 style='color:{color};'>{label}</h3>",
                        unsafe_allow_html=True,
                    )

                with col2:
                    st.subheader("AI Analysis")
                    st.markdown(data["explanation"])

                if data.get("citations"):
                    st.divider()
                    st.subheader("Matched Greenwashing Cases")
                    for i, cite in enumerate(data["citations"], 1):
                        with st.expander(f"Case {i} — Similarity: {cite['similarity']:.3f}"):
                            st.write(cite["content"])

        except requests.ConnectionError:
            st.error(
                "Could not connect to the backend API. "
                "Make sure the FastAPI server is running on http://localhost:8000."
            )
        except Exception as e:
            st.error(f"Unexpected error: {e}")
