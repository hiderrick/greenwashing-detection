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
