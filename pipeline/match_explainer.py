"""
Match Explainer Module

Generates human-readable explanations for document matches and
suggests actions (update existing vs create new).
"""

import json
import os
from typing import Dict, Optional
from agents.ai_client import call_sonnet


class MatchExplainer:
    """Generates explanations and suggestions for document matches."""

    # System prompt for AI-powered explanations
    EXPLANATION_PROMPT = """You are a technical documentation expert. Your job is to explain why a document matches a task and suggest the best action.

Generate a brief explanation (2-3 sentences) in Turkish that:
1. Explains why this document is relevant to the task
2. Highlights which sections or features are most relevant
3. Is clear and actionable for a business analyst

Keep the explanation concise and focused on actionable insights."""

    # System prompt for action suggestions
    SUGGESTION_PROMPT = """You are a technical documentation advisor. Your job is to recommend whether to UPDATE an existing document or CREATE a new one.

Analyze the task and matched document, then recommend one of:
- UPDATE_EXISTING: The document already covers this area and should be updated
- CREATE_NEW: The task is significantly different and needs a new document
- EXTEND_DOCUMENT: The document is related but task needs a separate section

Provide your recommendation as a JSON object:
{
  "suggestion": "UPDATE_EXISTING",
  "reasoning": "Brief explanation in Turkish",
  "update_sections": ["Section 1", "Section 2"],
  "confidence": 0.85
}"""

    def __init__(self):
        """Initialize the match explainer."""
        self.model = "claude-sonnet-4-20250514"  # Use Claude Sonnet for explanations
        # Get API key from environment or secrets
        try:
            import streamlit as st
            self.api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))
        except:
            self.api_key = os.getenv("ANTHROPIC_API_KEY", "")

    def explain_match(
        self,
        task_description: str,
        matched_doc: Dict,
        scores: Dict,
        use_ai: bool = None
    ) -> str:
        """
        Generate explanation for why a document matches a task.

        Uses template-based explanation for simple cases (fast, no cost)
        or AI-generated explanation for complex cases (detailed, costs ~$0.003).

        Args:
            task_description: The task description
            matched_doc: Matched document information
            scores: Score breakdown from matching
            use_ai: Force AI usage (None = auto-decide based on complexity)

        Returns:
            Human-readable explanation in Turkish
        """
        confidence = matched_doc.get("confidence", 0.0)

        # TEMPORARY: Always use template explanation (API key issues)
        # TODO: Re-enable AI explanations when API is configured
        return self._generate_template_explanation(matched_doc, scores)

        # Auto-decide whether to use AI
        if use_ai is None:
            # Use AI for medium/low confidence matches that need detailed explanation
            use_ai = confidence < 0.7

        if use_ai:
            return self._generate_ai_explanation(task_description, matched_doc, scores)
        else:
            return self._generate_template_explanation(matched_doc, scores)

    def _generate_template_explanation(self, matched_doc: Dict, scores: Dict) -> str:
        """
        Generate template-based explanation (fast, no AI cost).

        Args:
            matched_doc: Matched document information
            scores: Score breakdown

        Returns:
            Template-based explanation in Turkish
        """
        doc_title = matched_doc.get("title", "Bu doküman")
        doc_type = matched_doc.get("doc_type", "").upper()
        confidence = matched_doc.get("confidence", 0.0)

        # Get dominant score
        breakdown = scores
        semantic_score = breakdown.get("semantic_score", 0.0)
        keyword_score = breakdown.get("keyword_score", 0.0)

        # Build explanation based on scores
        if semantic_score > keyword_score:
            match_reason = "içerik anlamsal olarak benzer"
        else:
            match_reason = "anahtar kelime eşleşmeleri güçlü"

        # Confidence-based message
        if confidence > 0.75:
            confidence_msg = "Yüksek eşleşme skoruna sahip."
        elif confidence > 0.5:
            confidence_msg = "Orta seviye eşleşme skoruna sahip."
        else:
            confidence_msg = "Düşük eşleşme skoruna sahip, değerlendirme gerekebilir."

        explanation = (
            f"{doc_title} ({doc_type}) dokümeni görevinizle ilgili görünüyor - {match_reason}. "
            f"{confidence_msg}"
        )

        return explanation

    def _generate_ai_explanation(
        self,
        task_description: str,
        matched_doc: Dict,
        scores: Dict
    ) -> str:
        """
        Generate AI-powered explanation (detailed, costs ~$0.003).

        Args:
            task_description: The task description
            matched_doc: Matched document information
            scores: Score breakdown

        Returns:
            AI-generated explanation in Turkish
        """
        # Build context for AI
        user_message = f"""Task Description:
{task_description}

Matched Document:
- Title: {matched_doc.get('title', 'Unknown')}
- Type: {matched_doc.get('doc_type', 'unknown').upper()}
- Confidence: {matched_doc.get('confidence', 0.0):.2f}
- Section Preview: {matched_doc.get('section_matched', '')[:200]}

Scores:
- Semantic: {scores.get('semantic_score', 0.0):.2f}
- Keyword: {scores.get('keyword_score', 0.0):.2f}
- Metadata: {scores.get('metadata_score', 0.0):.2f}

Generate a brief explanation in Turkish (2-3 sentences) explaining why this document matches the task."""

        try:
            result = call_sonnet(
                system_prompt=self.EXPLANATION_PROMPT,
                user_content=user_message,
                api_key=self.api_key,
                model=self.model,
                use_caching=True
            )
            explanation = result.get("content", "")
            return explanation.strip()

        except Exception as e:
            print(f"Warning: AI explanation failed: {e}")
            # Fallback to template
            return self._generate_template_explanation(matched_doc, scores)

    def suggest_action(
        self,
        task_features: Dict,
        matched_doc: Dict,
        confidence: float
    ) -> Dict:
        """
        Suggest action: UPDATE_EXISTING, CREATE_NEW, or EXTEND_DOCUMENT.

        Uses rule-based logic for clear cases, AI for borderline cases.

        Args:
            task_features: Extracted task features
            matched_doc: Matched document information
            confidence: Match confidence score

        Returns:
            Dict with suggestion, reasoning, and update_sections
        """
        # Rule-based suggestions for ALL cases (AI disabled temporarily)
        if confidence > 0.75:
            # High confidence - likely update existing
            return {
                "suggestion": "UPDATE_EXISTING",
                "reasoning": "Doküman görevinizi zaten kapsıyor. Mevcut dokümana ekleme yapılabilir.",
                "update_sections": [],
                "confidence": confidence
            }
        elif confidence < 0.4:
            # Low confidence - likely create new
            return {
                "suggestion": "CREATE_NEW",
                "reasoning": "Mevcut dokümanlar görevinizi tam olarak kapsamıyor. Yeni doküman oluşturulması önerilir.",
                "update_sections": [],
                "confidence": confidence
            }
        else:
            # Medium confidence - use rule-based (AI disabled)
            return {
                "suggestion": "UPDATE_EXISTING" if confidence > 0.5 else "CREATE_NEW",
                "reasoning": "Doküman ilgili görünüyor. Değerlendirme yapılabilir." if confidence > 0.5 else "Yeni doküman oluşturulması önerilir.",
                "update_sections": [],
                "confidence": confidence
            }

    def _generate_ai_suggestion(
        self,
        task_features: Dict,
        matched_doc: Dict,
        confidence: float
    ) -> Dict:
        """
        Generate AI-powered action suggestion for borderline cases.

        Args:
            task_features: Extracted task features
            matched_doc: Matched document information
            confidence: Match confidence score

        Returns:
            Dict with suggestion details
        """
        # Build context for AI
        user_message = f"""Task Features:
- Intent: {task_features.get('intent', 'Unknown')}
- Scope: {task_features.get('scope', 'Unknown')}
- Keywords: {', '.join(task_features.get('keywords', [])[:5])}
- Complexity: {task_features.get('complexity', 'Unknown')}

Matched Document:
- Title: {matched_doc.get('title', 'Unknown')}
- Type: {matched_doc.get('doc_type', 'unknown').upper()}
- Confidence: {confidence:.2f}
- Preview: {matched_doc.get('section_matched', '')[:200]}

Should we UPDATE_EXISTING, CREATE_NEW, or EXTEND_DOCUMENT?
Provide recommendation as JSON."""

        try:
            result = call_sonnet(
                system_prompt=self.SUGGESTION_PROMPT,
                user_content=user_message,
                api_key=self.api_key,
                model=self.model,
                use_caching=True
            )

            # Parse JSON response
            response = result.get("content", "{}")
            suggestion = json.loads(response)

            # Validate and add confidence
            suggestion["confidence"] = confidence

            return suggestion

        except Exception as e:
            print(f"Warning: AI suggestion failed: {e}")
            # Fallback to rule-based
            return {
                "suggestion": "UPDATE_EXISTING" if confidence > 0.5 else "CREATE_NEW",
                "reasoning": "Doküman değerlendirme gerektirir.",
                "update_sections": [],
                "confidence": confidence
            }


# Convenience functions
def explain_match(
    task_description: str,
    matched_doc: Dict,
    scores: Dict,
    use_ai: bool = None
) -> str:
    """
    Generate explanation for a document match.

    Args:
        task_description: The task description
        matched_doc: Matched document information
        scores: Score breakdown from matching
        use_ai: Force AI usage (None = auto-decide)

    Returns:
        Human-readable explanation in Turkish
    """
    explainer = MatchExplainer()
    return explainer.explain_match(task_description, matched_doc, scores, use_ai)


def suggest_action(
    task_features: Dict,
    matched_doc: Dict,
    confidence: float
) -> Dict:
    """
    Suggest action for a matched document.

    Args:
        task_features: Extracted task features
        matched_doc: Matched document information
        confidence: Match confidence score

    Returns:
        Dict with suggestion, reasoning, and update_sections
    """
    explainer = MatchExplainer()
    return explainer.suggest_action(task_features, matched_doc, confidence)
