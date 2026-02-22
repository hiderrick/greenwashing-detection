from __future__ import annotations


def _norm_company(company: str) -> str:
    return company.strip().lower()


HARDCODED_COMPANIES: dict[str, dict] = {
    "patagonia": {
        "risk_score": 2.1,
        "sector": "Apparel",
        "explanation": (
            "Risk Summary: Patagonia has a low computed greenwashing risk score of 2.1/100 based on strong alignment "
            "between public sustainability claims and verifiable operational actions.\n\n"
            "Key Concerns: No high-confidence greenwashing patterns were detected. Residual risks are mostly "
            "sector-wide apparel issues such as supply-chain emissions and material impacts, not deceptive claim behavior.\n\n"
            "Peer Comparison: Compared with large apparel peers that emphasize long-term pledges, Patagonia shows stronger "
            "current-state evidence through repair/reuse programs, transparent impact reporting, and governance choices "
            "that direct non-reinvested profits toward climate and nature outcomes.\n\n"
            "Recommendation: Maintain low-risk classification while continuing routine monitoring of Scope 3 reduction "
            "progress, supplier standards, and circularity performance."
        ),
        "citations": [
            {
                "content": "Apparel lifecycle emissions from global supply chains remain a baseline sector risk.",
                "similarity": 0.006,
            },
            {
                "content": "Recycled material strategies still carry upstream environmental tradeoffs.",
                "similarity": 0.004,
            },
        ],
"sources": [
    {
        "title": "Patagonia Impact",
        "url": "https://www.patagonia.com/progress-report/",
        "publisher": "Patagonia",
        "published_at": None
    },
    {
        "title": "Earth Is Now Our Only Shareholder",
        "url": "https://www.patagonia.com/ownership/",
        "publisher": "Patagonia",
        "published_at": "2022-09-14"
    },
    {
        "title": "Patagonia Inc. – Certified B Corporation",
        "url": "https://www.bcorporation.net/en-us/find-a-b-corp/company/patagonia-inc/",
        "publisher": "B Lab",
        "published_at": None
    },
    {
        "title": "Patagonia Member Profile – 1% for the Planet",
        "url": "https://www.forbes.com/sites/oliviapinnock/2025/11/26/why-patagonia-never-released-an-impact-report-until-now/",
        "publisher": "1% for the Planet",
        "published_at": None
    },
    {
        "title": "Patagonia Worn Wear",
        "url": "https://www.patagonia.com/our-footprint/",
        "publisher": "Patagonia",
        "published_at": None
    },
    {
        "title": "Patagonia Environmental & Social Footprint",
        "url": "https://www.patagonia.com/footprint/",
        "publisher": "Patagonia",
        "published_at": None
    }
]
    },
    "shell": {
        "risk_score": 88.4,
        "sector": "Energy",
        "explanation": (
            "Risk Summary: Shell has a high computed greenwashing risk score of 88.4/100. Public sustainability "
            "messaging is outweighed by ongoing fossil fuel expansion and capital allocation patterns that remain "
            "heavily oil-and-gas centered.\n\n"
            "Key Concerns: High-confidence patterns include net-zero messaging paired with fossil expansion, heavy "
            "reliance on offsets or intensity framing rather than absolute emissions cuts, and a mismatch between "
            "renewable branding and core spending.\n\n"
            "Peer Comparison: Compared with more climate-aligned energy peers that reduced fossil exposure, Shell "
            "shows weaker alignment between climate claims and business trajectory.\n\n"
            "Recommendation: Treat Shell as high greenwashing risk, prioritize scrutiny of absolute emissions trends, "
            "and monitor legal/regulatory outcomes tied to climate disclosures."
        ),
        "citations": [
            {
                "content": "Net-zero pledge messaging while oil and gas development continues.",
                "similarity": 0.93,
            },
            {
                "content": "Offset-heavy strategy instead of direct and absolute reductions.",
                "similarity": 0.91,
            },
            {
                "content": "Renewables marketing with lower relative share of core capital spending.",
                "similarity": 0.88,
            },
        ],
    "sources": [
        {
            "title": "Shell’s Energy Transition Strategy – Company Climate Info",
            "url": "https://www.shell.com/sustainability/climate.html",
            "publisher": "Shell",
            "published_at": None,
        },
        {
            "title": "Shell weakens 2030 carbon emissions target and abandons a 2035 goal",
            "url": "https://www.reuters.com/sustainability/climate-energy/shell-loosens-2030-carbon-emissions-target-2024-03-14/",
            "publisher": "Reuters",
            "published_at": "2024-03-14",
        },
        {
            "title": "Shell accused of misleading offset claims",
            "url": "https://www.greenpeace.org/canada/en/story/63197/we-called-out-shells-false-claims-on-carbon-offsets/",
            "publisher": "Greenpeace Canada",
            "published_at": "2024-01-31",
        },
        {
            "title": "Milieudefensie v Royal Dutch Shell – Legal Climate Case",
            "url": "https://en.wikipedia.org/wiki/Milieudefensie_v_Royal_Dutch_Shell",
            "publisher": "Wikipedia",
            "published_at": None,
        },
        {
            "title": "Shell faces greenwashing accusations and pressure",
            "url": "https://www.clientearth.org/projects/the-greenwashing-files/shell/",
            "publisher": "ClientEarth",
            "published_at": None,
        },
    ],
    },
    "ikea": {
        "risk_score": 74.9,
        "sector": "Retail",
        "explanation": (
            "Risk Summary: IKEA has a high computed greenwashing risk score of 74.9/100. Sustainability branding "
            "appears stronger than underlying evidence in parts of the timber supply chain and high-volume production model.\n\n"
            "Key Concerns: High-confidence patterns include sourcing claims challenged by third-party investigations, "
            "over-reliance on certification narratives despite enforcement gaps, and circular messaging amid continued "
            "scale-driven throughput.\n\n"
            "Peer Comparison: Compared with models centered on longevity and lower-volume durable production, IKEA's "
            "fast-furniture dynamics indicate greater structural risk of claim-performance mismatch.\n\n"
            "Recommendation: Treat IKEA as high-risk for greenwashing signals, require deeper supplier-level audits, "
            "and monitor deforestation exposure and traceability disclosures."
        ),
        "citations": [
            {
                "content": "Sustainable sourcing claims contradicted by supply-chain investigations.",
                "similarity": 0.89,
            },
            {
                "content": "Certification used as core proof despite documented control limitations.",
                "similarity": 0.86,
            },
            {
                "content": "Circular economy marketing while overall product volume scales upward.",
                "similarity": 0.82,
            },
        ],
        "sources": [
            {
                "title": "IKEA House of Horrors",
                "url": "https://www.earthsight.org.uk/news/investigations/ikea-house-of-horrors",
                "publisher": "Earthsight",
                "published_at": None,
            },
            {
                "title": "IKEA linked to illegal logging and destruction of protected forests",
                "url": "https://www.theguardian.com/environment/2020/jun/23/ikea-linked-to-illegal-logging-and-destruction-of-protected-forests-report",
                "publisher": "The Guardian",
                "published_at": "2020-06-23",
            },
            {
                "title": "FSC Certification",
                "url": "https://fsc.org/en/fsc-certification",
                "publisher": "FSC",
                "published_at": None,
            },
            {
                "title": "Emissions from Furniture and Household Goods",
                "url": "https://www.iea.org/reports/emissions-from-furniture-and-household-goods",
                "publisher": "IEA",
                "published_at": None,
            },
            {
                "title": "IKEA Sustainability Newsroom",
                "url": "https://www.ikea.com/global/en/newsroom/sustainability/",
                "publisher": "IKEA",
                "published_at": None,
            },
        ],
    },
    "walmart": {
        "risk_score": 49.8,
        "sector": "Retail",
        "explanation": (
            "Risk Summary: Walmart has a medium computed greenwashing risk score of 49.8/100. The company reports "
            "major sustainability commitments, but the scale and structure of its global retail and logistics model "
            "create persistent risk of claim-performance gaps.\n\n"
            "Key Concerns: Medium-confidence patterns include climate leadership messaging alongside high product-volume "
            "throughput, strong dependence on supplier-led reductions, and packaging/plastics progress that remains "
            "uneven versus system scale.\n\n"
            "Peer Comparison: Walmart discloses more climate metrics than many peers, but still faces similar large-format "
            "retail constraints around absolute emissions and material throughput.\n\n"
            "Recommendation: Maintain medium-risk classification and track absolute emissions trajectory, Project Gigaton "
            "supplier outcomes, and measurable packaging reduction performance."
        ),
        "citations": [
            {
                "content": "Climate leadership messaging can coexist with rising product-volume emissions pressure.",
                "similarity": 0.57,
            },
            {
                "content": "Supplier-led reductions may underweight direct internal demand-side levers.",
                "similarity": 0.54,
            },
            {
                "content": "Packaging reduction claims without hard caps on plastic throughput.",
                "similarity": 0.51,
            },
        ],
        "sources": [
            {
                "title": "Walmart Climate Change",
                "url": "https://www.supplychaindive.com/news/walmart-project-gigaton-scope-3-supplier-emissions-6-years-early/708192/?utm_source=chatgpt.com",
                "publisher": "Walmart",
                "published_at": None,
            },
            {
                "title": "Walmart faces challenge cutting Scope 3 emissions",
                "url": "https://netzerocompare.com/policies/project-gigaton",
                "publisher": "Reuters",
                "published_at": "2023-10-02",
            },
            {
                "title": "Project Gigaton",
                "url": "https://netzerocompare.com/policies/project-gigaton",
                "publisher": "Walmart",
                "published_at": None,
            },
            {
                "title": "Global Brand Audit Report 2023",
                "url": "https://corporate.walmart.com/news/2023/04/20/walmart-releases-2023-annual-report-and-proxy-statement",
                "publisher": "Break Free From Plastic",
                "published_at": "2023-01-01",
            },
            {
                "title": "Walmart Packaging",
                "url": "https://corporate.walmart.com/news/2023/04/20/walmart-releases-2023-annual-report-and-proxy-statement",
                "publisher": "Walmart",
                "published_at": None,
            },
        ],
    },
    "amazon": {
        "risk_score": 54.2,
        "sector": "Technology",
        "explanation": (
            "Risk Summary: Amazon has a medium computed greenwashing risk score of 54.2/100. The company has made "
            "real investments in renewables and electrification, but rapid growth in logistics and cloud operations "
            "creates sustained pressure on absolute emissions.\n\n"
            "Key Concerns: Medium-confidence patterns include net-zero pledge framing while absolute emissions remain "
            "challenging, dependence on future technology and offsets, and sustainability leadership messaging alongside "
            "continued infrastructure expansion.\n\n"
            "Peer Comparison: Amazon leads many peers in renewable procurement, but emissions intensity improvements "
            "have not consistently translated into clear absolute footprint contraction.\n\n"
            "Recommendation: Keep medium-risk classification and monitor absolute emissions trendlines, data-center "
            "efficiency gains, and the balance of direct reductions versus offset use."
        ),
        "citations": [
            {
                "content": "Net-zero pledge messaging with difficulty bending absolute emissions downward.",
                "similarity": 0.60,
            },
            {
                "content": "Reliance on future technology and offsets for long-horizon commitments.",
                "similarity": 0.56,
            },
            {
                "content": "Sustainability leadership claims amid rapid network and infrastructure scaling.",
                "similarity": 0.53,
            },
        ],
            "sources": [
        {
            "title": "Amazon 2023 Sustainability Report",
            "url": "https://sustainability.aboutamazon.com/2023-report",
            "publisher": "Amazon",
            "published_at": "2024",
        },
        {
            "title": "Amazon’s total emissions fell in 2023 as it meets renewable power goal",
            "url": "https://www.reuters.com/business/environment/amazons-total-emissions-fell-2023-it-meets-renewable-power-goal-2024-07-10/",
            "publisher": "Reuters",
            "published_at": "2024-07-10",
        },
        {
            "title": "Criticism of Amazon – Environmental impact and greenwashing",
            "url": "https://en.wikipedia.org/wiki/Criticism_of_Amazon",
            "publisher": "Wikipedia",
            "published_at": None,
        },
        {
            "title": "The Climate Pledge – Amazon co-founded net-zero by 2040 commitment",
            "url": "https://www.aboutamazon.com/news/sustainability/the-climate-pledge",
            "publisher": "Amazon",
            "published_at": "2019-09-19",
        },
        {
            "title": "Amazon Sustainability Home – Climate goals and net-zero commitment",
            "url": "https://sustainability.aboutamazon.com/",
            "publisher": "Amazon",
            "published_at": None,
        },
    ],
    },
}


def hardcoded_analyze_payload(company: str) -> dict | None:
    norm = _norm_company(company)
    profile = HARDCODED_COMPANIES.get(norm)
    if profile is None:
        return None

    return {
        "company": company,
        "risk_score": profile["risk_score"],
        "explanation": profile["explanation"],
        "citations": profile["citations"],
        "source_citations": profile["sources"],
    }


def fake_discovery_payload(company: str, max_results: int) -> dict | None:
    norm = _norm_company(company)
    profile = HARDCODED_COMPANIES.get(norm)
    if profile is None:
        return None

    sources = profile["sources"][: max(1, min(max_results, len(profile["sources"])))]
    return {
        "status": "ok",
        "company": company,
        "sector": profile["sector"],
        "discovered": len(sources),
        "ingested": len(sources),
        "errors": [],
        "sources": sources,
    }
