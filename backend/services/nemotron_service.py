"""
Replaces external API dependencies with local LLM engine.
"""
from typing import Dict, Any, List
from backend.models.schemas import ExtractedJob
from backend.services.llm_engine import generate_email_content as custom_generate_email_content

def generate_email_content(job: ExtractedJob, candidate_profile: Dict[str, Any]) -> Dict[str, str]:
    """
    Generates personalized job application email using local custom LLM engine.
    """
    return custom_generate_email_content(job, candidate_profile)

def extract_job_with_nemotron(text_chunk: str) -> List[ExtractedJob]:
    """
    Deprecated fallback stub for external LLM API job extraction.
    """
    return []
