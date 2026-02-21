import streamlit as st
import requests
import streamlit.components.v1 as components

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Greenwashing Risk Detector", page_icon="🌱", layout="wide")

# --- Custom Styling & Three.js Injection ---
st.markdown("""
    <style>
    /* Professional Overrides */
    .block-container {
        padding-top: 2rem;
        max-width: 800px;
    }
    
    /* Remove default Streamlit backgrounds to show Three.js */
    .stApp {
        background: transparent;
    }
    
    header, [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Professional Palette */
    :root {
        --pistachio: #DEF4C6;
        --mint: #73E2A7;
        --forest: #1C7C54;
        --evergreen: #1B512D;
        --bg-light: #F6FAED;
    }

    h1, h2, h3, p, span, label {
        color: var(--evergreen) !important;
        font-family: 'Inter', sans-serif;
    }

    /* Custom Input Styling */
    .stTextInput input {
        border-radius: 8px !important;
        border: 1px solid rgba(28, 124, 84, 0.2) !important;
        padding: 12px 16px !important;
    }

    .stButton button {
        background-color: var(--forest) !important;
        color: var(--pistachio) !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    .stButton button:hover {
        background-color: var(--evergreen) !important;
        box-shadow: 0 4px 12px rgba(27, 81, 45, 0.2) !important;
    }

    /* Results Card */
    .results-card {
        background-color: var(--pistachio);
        padding: 30px;
        border-radius: 12px;
        border: 1px solid rgba(115, 226, 167, 0.4);
        margin-top: 2rem;
        box-shadow: 0 8px 30px rgba(27, 81, 45, 0.05);
    }

    /* Background Container */
    #threejs-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
        background-color: #F6FAED;
    }
    </style>
""", unsafe_allow_html=True)

# Three.js Component
three_js_code = """
<div id="threejs-bg"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.z = 18;
    camera.position.y = 2;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0xF6FAED, 1);
    document.getElementById('threejs-bg').appendChild(renderer.domElement);

    scene.fog = new THREE.FogExp2(0xF6FAED, 0.04);
    
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(5, 10, 7);
    scene.add(dirLight);

    const floatingObjects = [];
    const geometries = [
        new THREE.IcosahedronGeometry(1.2, 0),
        new THREE.TetrahedronGeometry(1.2, 1),
        new THREE.OctahedronGeometry(1.2, 0)
    ];
    const materials = [
        new THREE.MeshStandardMaterial({ color: 0x1C7C54, flatShading: true, roughness: 0.9 }),
        new THREE.MeshStandardMaterial({ color: 0x1B512D, flatShading: true, roughness: 1.0 })
    ];

    for (let i = 0; i < 40; i++) {
        const geo = geometries[Math.floor(Math.random() * geometries.length)].clone();
        const mat = materials[Math.floor(Math.random() * materials.length)];
        
        // Distortion
        const pos = geo.attributes.position;
        for (let j = 0; j < pos.count; j++) {
            pos.setXYZ(j, pos.getX(j) + (Math.random()-0.5)*0.4, pos.getY(j) + (Math.random()-0.5)*0.4, pos.getZ(j) + (Math.random()-0.5)*0.4);
        }
        geo.computeVertexNormals();
        
        const mesh = new THREE.Mesh(geo, mat);
        mesh.scale.setScalar(Math.random() * 0.8 + 0.3);
        mesh.position.set((Math.random()-0.5)*40, (Math.random()-0.5)*40, (Math.random()-0.5)*20 - 5);
        mesh.userData = { 
            rot: new THREE.Vector3((Math.random()-0.5)*0.01, (Math.random()-0.5)*0.01, (Math.random()-0.5)*0.01),
            speed: Math.random() * 0.01 + 0.005 
        };
        floatingObjects.push(mesh);
        scene.add(mesh);
    }

    function animate() {
        requestAnimationFrame(animate);
        floatingObjects.forEach(m => {
            m.position.y += m.userData.speed;
            m.rotation.x += m.userData.rot.x;
            m.rotation.y += m.userData.rot.y;
            if (m.position.y > 20) m.position.y = -25;
        });
        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
</script>
<style>
    body { margin: 0; overflow: hidden; }
    #threejs-bg { position: fixed; width: 100vw; height: 100vh; }
</style>
"""

components.html(three_js_code, height=1)

# --- UI Content ---
st.title("Greenwashing Risk Detector")
st.markdown("##### Authentic ESG Analysis through AI & Knowledge Retrieval")

with st.expander("Ingest ESG Document"):
    SECTOR_OPTIONS = ["Unknown", "Energy", "Utilities", "Materials", "Industrials", "ConsumerDiscretionary", "ConsumerStaples", "HealthCare", "Financials", "InformationTechnology", "CommunicationServices", "RealEstate", "Other"]
    DOC_TYPE_OPTIONS = ["ESGReport", "AnnualReport", "SustainabilityReport", "ClimateReport", "ImpactReport", "CSRReport", "Other"]
    
    with st.form("upload_esg_form"):
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            upload_company = st.text_input("Company Name")
            upload_sector = st.selectbox("Sector", SECTOR_OPTIONS)
        with col_m2:
            upload_doc_type = st.selectbox("Document Type", DOC_TYPE_OPTIONS)
            upload_file = st.file_uploader("ESG File (.txt, .pdf)", type=["txt", "pdf"])
        
        upload_submit = st.form_submit_button("Ingest Report")

    if upload_submit and upload_company and upload_file:
        with st.spinner("Processing..."):
            try:
                files = {"file": (upload_file.name, upload_file.getvalue(), "application/pdf" if upload_file.name.lower().endswith(".pdf") else "text/plain")}
                data = {"company": upload_company.strip(), "sector": upload_sector, "doc_type": upload_doc_type}
                res = requests.post(f"{API_URL}/upload/esg", data=data, files=files, timeout=60)
                if res.status_code == 200:
                    st.success("Successfully ingested.")
                else:
                    st.error(f"Error: {res.status_code}")
            except Exception as e:
                st.error(f"Connection failed: {e}")

company = st.text_input("Analyze Sustainability Claims", placeholder="Enter company name (e.g., Shell, Patagonia)...")

if st.button("Analyze Risk", use_container_width=True):
    if not company:
        st.warning("Please enter a company name.")
    else:
        with st.spinner("Performing AI Analysis..."):
            try:
                res = requests.get(f"{API_URL}/analyze/{company}", timeout=45)
                if res.status_code == 200:
                    data = res.json()
                    score = data["risk_score"]
                    
                    risk_color = "#C62828" if score > 60 else ("#E65100" if score > 30 else "#2E7D32")
                    risk_label = "High Risk" if score > 60 else ("Medium Risk" if score > 30 else "Low Risk")

                    st.markdown(f"""
                        <div class="results-card">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px;">
                                <div>
                                    <p style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin: 0; opacity: 0.7;">Greenwashing Risk Score</p>
                                    <p style="font-size: 48px; font-weight: 700; margin: 0; color: #1B512D !important;">{score}<span style="font-size: 20px; opacity: 0.5;">/100</span></p>
                                </div>
                                <div style="background: white; padding: 8px 16px; border-radius: 20px; border: 1px solid {risk_color}; color: {risk_color} !important; font-weight: 700; font-size: 14px; text-transform: uppercase;">
                                    {risk_label}
                                </div>
                            </div>
                            <hr style="border: 0; border-top: 1px solid rgba(27, 81, 45, 0.1); margin: 20px 0;">
                            <p style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; opacity: 0.7; margin-bottom: 10px;">AI Analysis Findings</p>
                            <p style="font-size: 15px; line-height: 1.6; background: rgba(255,255,255,0.4); padding: 15px; border-radius: 8px;">{data['explanation']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if data.get("citations"):
                        with st.expander("View Evidence & Citations"):
                            for i, cite in enumerate(data["citations"], 1):
                                st.info(f"**Evidence Fragment {i}** (Similarity: {cite['similarity']:.3f})")
                                st.write(cite["content"])
                else:
                    st.error(f"Backend API error: {res.status_code}. Make sure your API key is set and the server is running.")
            except Exception as e:
                st.error(f"Could not connect to analysis engine: {e}")
