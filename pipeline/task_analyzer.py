"""
Task Analyzer Module

Extracts structured features from task descriptions using Claude AI.
Used for smart document matching to understand task requirements.
"""

import json
import os
from typing import Dict, Optional, List
from agents.ai_client import call_sonnet


class TaskAnalyzer:
    """Analyzes task descriptions to extract structured features for matching."""

    # System prompt with caching for cost optimization
    ANALYSIS_PROMPT = """You are a requirements analysis expert. Your job is to analyze task descriptions and extract structured features that will be used to find relevant existing documents.

Extract the following information from the task description:

1. **Keywords**: 3-10 important domain-specific keywords (e.g., "biometric", "authentication", "login")
2. **Intent**: What type of work is this? Choose one:
   - ADD_FEATURE: Adding completely new functionality
   - UPDATE_FEATURE: Enhancing or modifying existing functionality
   - FIX_BUG: Fixing a defect or issue
   - REFACTOR: Code/design improvement without functional changes
   - DOCUMENTATION: Pure documentation work

3. **Scope**: Which component/module/screen is affected? (e.g., "Login Screen", "Payment Module")

4. **Entities**: Specific technical terms, components, or proper nouns mentioned (e.g., "Face ID", "Touch ID", "OAuth")

5. **Document Type Relevance**: For each document type, provide a relevance score (0.0-1.0):
   - ba: Business Analysis documents (requirements, user stories, features)
   - ta: Technical Analysis documents (architecture, design, technical specs)
   - tc: Test Cases (test scenarios, test plans)

6. **Complexity**: Estimate task complexity: "low", "medium", or "high"

7. **Search Query**: Generate an optimized search query (1-2 sentences) that would find relevant documents

Output your analysis as a JSON object with this exact structure:
{
  "keywords": ["keyword1", "keyword2", ...],
  "intent": "ADD_FEATURE",
  "scope": "Component Name",
  "entities": ["Entity1", "Entity2", ...],
  "doc_type_relevance": {"ba": 0.9, "ta": 0.7, "tc": 0.5},
  "complexity": "medium",
  "search_query": "optimized search query string"
}

Be concise and focus on information that would help find relevant existing documents."""

    def __init__(self):
        """Initialize the task analyzer."""
        self.model = "claude-sonnet-4-20250514"  # Use Claude Sonnet 4 for analysis
        # Get API key from environment or secrets
        try:
            import streamlit as st
            self.api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))
        except:
            self.api_key = os.getenv("ANTHROPIC_API_KEY", "")

    def analyze_task(
        self,
        task_description: str,
        jira_key: Optional[str] = None
    ) -> Dict:
        """
        Analyze a task description and extract structured features.

        Args:
            task_description: The task description to analyze
            jira_key: Optional JIRA key for context

        Returns:
            Dict containing:
                - keywords: List of important keywords
                - intent: Task intent (ADD_FEATURE, UPDATE_FEATURE, etc.)
                - scope: Component/module affected
                - entities: Specific technical terms
                - doc_type_relevance: Relevance scores for BA/TA/TC
                - complexity: Task complexity (low/medium/high)
                - search_query: Optimized search query string
        """
        # Build user message
        user_message = f"Task Description:\n{task_description}"
        if jira_key:
            user_message = f"JIRA Key: {jira_key}\n\n{user_message}"

        # Call AI with prompt caching enabled
        result = call_sonnet(
            system_prompt=self.ANALYSIS_PROMPT,
            user_content=user_message,
            api_key=self.api_key,
            model=self.model,
            use_caching=True  # Enable prompt caching for cost optimization
        )

        # call_sonnet returns a dict with 'content' key
        response = result.get("content", "{}")

        # Parse JSON response
        try:
            analysis = json.loads(response)

            # Validate and normalize the response
            analysis = self._validate_analysis(analysis)

            return analysis

        except json.JSONDecodeError as e:
            # Fallback: extract basic features
            print(f"Warning: Failed to parse AI response as JSON: {e}")
            return self._fallback_analysis(task_description)

    def _validate_analysis(self, analysis: Dict) -> Dict:
        """
        Validate and normalize the analysis result.

        Args:
            analysis: Raw analysis from AI

        Returns:
            Validated and normalized analysis
        """
        # Ensure required fields exist
        default_analysis = {
            "keywords": [],
            "intent": "ADD_FEATURE",
            "scope": "Unknown",
            "entities": [],
            "doc_type_relevance": {"ba": 0.5, "ta": 0.5, "tc": 0.5},
            "complexity": "medium",
            "search_query": ""
        }

        # Merge with defaults
        validated = {**default_analysis, **analysis}

        # Validate intent
        valid_intents = {"ADD_FEATURE", "UPDATE_FEATURE", "FIX_BUG", "REFACTOR", "DOCUMENTATION"}
        if validated["intent"] not in valid_intents:
            validated["intent"] = "ADD_FEATURE"

        # Validate complexity
        valid_complexity = {"low", "medium", "high"}
        if validated["complexity"] not in valid_complexity:
            validated["complexity"] = "medium"

        # Validate doc_type_relevance scores
        for doc_type in ["ba", "ta", "tc"]:
            if doc_type not in validated["doc_type_relevance"]:
                validated["doc_type_relevance"][doc_type] = 0.5
            else:
                # Clamp to [0, 1]
                score = validated["doc_type_relevance"][doc_type]
                validated["doc_type_relevance"][doc_type] = max(0.0, min(1.0, score))

        # Ensure lists are lists
        if not isinstance(validated["keywords"], list):
            validated["keywords"] = []
        if not isinstance(validated["entities"], list):
            validated["entities"] = []

        return validated

    def _fallback_analysis(self, task_description: str) -> Dict:
        """
        Fallback analysis when AI parsing fails.
        Extracts basic features using simple heuristics.

        Args:
            task_description: The task description

        Returns:
            Basic analysis result
        """
        # Extract simple keywords (words longer than 4 chars)
        words = task_description.lower().split()
        keywords = [w for w in words if len(w) > 4][:10]

        # Detect intent from keywords
        intent = "ADD_FEATURE"
        if any(word in task_description.lower() for word in ["fix", "bug", "defect", "error"]):
            intent = "FIX_BUG"
        elif any(word in task_description.lower() for word in ["update", "modify", "change", "improve"]):
            intent = "UPDATE_FEATURE"
        elif any(word in task_description.lower() for word in ["refactor", "cleanup", "optimize"]):
            intent = "REFACTOR"

        return {
            "keywords": keywords,
            "intent": intent,
            "scope": "Unknown",
            "entities": [],
            "doc_type_relevance": {"ba": 0.6, "ta": 0.5, "tc": 0.4},
            "complexity": "medium",
            "search_query": task_description[:200]  # First 200 chars
        }


# Convenience function for quick analysis
def analyze_task(task_description: str, jira_key: Optional[str] = None) -> Dict:
    """
    Analyze a task description and extract structured features.

    Args:
        task_description: The task description to analyze
        jira_key: Optional JIRA key for context

    Returns:
        Dict containing extracted features (keywords, intent, scope, etc.)
    """
    analyzer = TaskAnalyzer()
    return analyzer.analyze_task(task_description, jira_key)
