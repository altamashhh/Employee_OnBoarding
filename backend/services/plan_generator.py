"""Plan generator — create structured 30-day onboarding plans using Gemini."""

import json
import re

from google import genai

from core.config import settings
from models.schemas import PlanResponse, PlanDay

# ── Gemini client (reused) ──────────────────────────────────
_gemini_client: genai.Client | None = None


def _get_gemini_client() -> genai.Client:
    """Lazy-load the Gemini client."""
    global _gemini_client
    if _gemini_client is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set. Please add it to your .env file.")
        _gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _gemini_client


def generate_plan(role: str, experience: str, department: str = "") -> PlanResponse:
    """Generate a 30-day onboarding plan using Gemini."""

    dept_context = f" in the {department} department" if department else ""

    prompt = f"""You are an HR onboarding specialist. Create a detailed 30-day onboarding plan for a new employee.

Employee Details:
- Role: {role}
- Experience Level: {experience}
- Department: {department or "General"}{dept_context}

Generate a structured 30-day plan. Return ONLY a valid JSON array with exactly 30 objects.
Each object must have:
- "day": integer (1-30)
- "title": string (short title for the day's focus)
- "tasks": array of strings (3-5 specific actionable tasks)

Example format:
[
  {{"day": 1, "title": "Welcome & Setup", "tasks": ["Complete HR paperwork", "Set up workstation", "Meet team lead"]}},
  {{"day": 2, "title": "Company Overview", "tasks": ["Attend company orientation", "Review company handbook"]}}
]

Return ONLY the JSON array, no other text, no markdown code blocks."""

    try:
        client = _get_gemini_client()
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )
        raw_text = response.text or ""
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}")

    # Parse the JSON response
    try:
        # Try to extract JSON from the response (handle markdown code blocks)
        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if json_match:
            plan_data = json.loads(json_match.group())
        else:
            plan_data = json.loads(raw_text)

        plan_days = [
            PlanDay(
                day=item["day"],
                title=item["title"],
                tasks=item["tasks"],
            )
            for item in plan_data
        ]

        return PlanResponse(plan=plan_days)

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise RuntimeError(f"Failed to parse plan from Gemini response: {e}")
