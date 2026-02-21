import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_report(
    company: str,
    company_claims: list[tuple[str, str, str]],
    greenwash_matches: list[tuple[str, float]],
    peer_comparisons: list[tuple[str, str, float]],
    score: float,
) -> str:
    claims_text = "\n".join(
        f"- [{doc_type}] {content[:500]}"
        for content, _sector, doc_type in company_claims
    ) or "No ESG claims found for this company."

    greenwash_text = "\n".join(
        f"- (similarity {sim:.2f}) {content[:500]}"
        for content, sim in greenwash_matches
    ) or "No matching greenwashing cases found."

    peer_text = "\n".join(
        f"- [{peer_company}] (similarity {sim:.2f}) {content[:500]}"
        for content, peer_company, sim in peer_comparisons
    ) or "No peer disclosures available for comparison."

    prompt = f"""You are a senior ESG analyst specializing in greenwashing detection.

Company under review: {company}
Computed greenwashing risk score: {score}/100

=== Company's Own ESG Claims ===
{claims_text}

=== Matched Known Greenwashing Cases ===
{greenwash_text}

=== Peer Sector Disclosures for Comparison ===
{peer_text}

Based on the above evidence, produce a concise greenwashing risk assessment for {company}. Structure your response as:

1. **Risk Summary** — One-paragraph overall assessment.
2. **Key Concerns** — Bullet points highlighting specific claims that resemble known greenwashing patterns, with references to the matched cases.
3. **Peer Comparison** — How the company's disclosures compare to sector peers.
4. **Recommendation** — Actionable guidance for an investor.

Be specific, cite the evidence provided, and avoid speculation beyond what the data supports."""

    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return resp.choices[0].message.content
    except Exception as exc:
        top_case = greenwash_matches[0][0][:200] if greenwash_matches else "No direct match."
        peer = peer_comparisons[0][1] if peer_comparisons else "N/A"
        return (
            f"Risk Summary: {company} has a computed greenwashing risk score of {score}/100.\n\n"
            f"Key Concerns: Top matched case snippet: \"{top_case}\".\n\n"
            f"Peer Comparison: Closest same-sector peer in retrieval: {peer}.\n\n"
            f"Recommendation: Validate high-impact claims with third-party assurance and require clearer KPIs."
            f"\n\n(LLM fallback mode due to {type(exc).__name__}.)"
        )
