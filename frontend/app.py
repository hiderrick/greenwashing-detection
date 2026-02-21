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
with st.form("upload_esg_form"):
    upload_company = st.text_input("Company", placeholder="e.g. NewEnergyCo")
    upload_sector = st.text_input("Sector", placeholder="e.g. Energy")
    upload_doc_type = st.text_input("Document Type", placeholder="e.g. AnnualReport")
    upload_file = st.file_uploader("ESG file (.txt or .pdf)", type=["txt", "pdf"])
    upload_submit = st.form_submit_button("Upload and Ingest")

if upload_submit:
    if not upload_company or not upload_sector or not upload_doc_type or not upload_file:
        st.warning("Please complete all upload fields and choose a .txt or .pdf file.")
    else:
        try:
            content_type = "application/pdf" if upload_file.name.lower().endswith(".pdf") else "text/plain"
            files = {"file": (upload_file.name, upload_file.getvalue(), content_type)}
            data = {
                "company": upload_company,
                "sector": upload_sector,
                "doc_type": upload_doc_type,
            }
            res = requests.post(f"{API_URL}/upload/esg", data=data, files=files, timeout=180)
            if res.status_code == 200:
                payload = res.json()
                st.success(
                    f"Uploaded and ingested: {payload['saved_as']} "
                    f"({payload['chars']} chars)"
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
