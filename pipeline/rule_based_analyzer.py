"""
Rule-Based Task Analyzer

Fast, free task analysis using simple NLP and heuristics.
Falls back to AI (Claude) only for complex queries.

Tiered Approach:
- Tier 1: Rule-based analysis (instant, free)
- Tier 2: AI analysis (1-2s, costs money)

Author: BA-QA Platform
Date: 2026-02-16
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ComplexityMetrics:
    """Metrics for measuring query complexity."""
    keyword_count: int
    sentence_count: int
    avg_sentence_length: float
    question_count: int
    technical_term_count: int
    ambiguous_word_count: int
    total_words: int
    has_negation: bool
    has_conditional: bool

    def calculate_score(self) -> float:
        """
        Calculate complexity score (0-1).
        Higher = more complex = needs AI.
        """
        score = 0.0

        # Simple query: 1-2 sentences, 5-15 words, clear intent
        # Complex query: 3+ sentences, 20+ words, multiple conditions

        # Sentence complexity (0-0.3)
        if self.sentence_count > 3:
            score += 0.3
        elif self.sentence_count > 2:
            score += 0.2
        elif self.sentence_count > 1:
            score += 0.1

        # Length complexity (0-0.2)
        if self.total_words > 30:
            score += 0.2
        elif self.total_words > 20:
            score += 0.1

        # Technical complexity (0-0.2)
        if self.technical_term_count > 3:
            score += 0.2
        elif self.technical_term_count > 1:
            score += 0.1

        # Ambiguity (0-0.15)
        if self.ambiguous_word_count > 2:
            score += 0.15
        elif self.ambiguous_word_count > 0:
            score += 0.08

        # Questions (0-0.1)
        if self.question_count > 1:
            score += 0.1
        elif self.question_count > 0:
            score += 0.05

        # Conditionals/Negations (0-0.05)
        if self.has_conditional:
            score += 0.03
        if self.has_negation:
            score += 0.02

        return min(1.0, score)


class RuleBasedAnalyzer:
    """Rule-based task analyzer using simple NLP and heuristics."""

    # Turkish stop words (common words to filter)
    TURKISH_STOP_WORDS = {
        'bir', 'bu', 'şu', 've', 'veya', 'ile', 'için', 'gibi', 'kadar',
        'daha', 'çok', 'az', 'en', 'da', 'de', 'ki', 'mi', 'mı', 'mu', 'mü',
        'ne', 'nasıl', 'neden', 'niçin', 'nerede', 'ne zaman', 'hangi'
    }

    # Intent keywords (Turkish)
    INTENT_KEYWORDS = {
        'ADD_FEATURE': [
            'ekle', 'ekleme', 'yeni', 'oluştur', 'implement', 'add',
            'geliştir', 'entegre', 'dahil et', 'koy'
        ],
        'UPDATE_FEATURE': [
            'güncelle', 'değiştir', 'iyileştir', 'revize', 'update',
            'düzenle', 'modifiye', 'optimize', 'geliştir'
        ],
        'FIX_BUG': [
            'düzelt', 'fix', 'hata', 'bug', 'sorun', 'problem',
            'çözüm', 'tamir', 'repair'
        ],
        'REMOVE_FEATURE': [
            'kaldır', 'sil', 'çıkar', 'remove', 'delete', 'temizle'
        ]
    }

    # Technical domain terms
    TECHNICAL_TERMS = {
        # Authentication
        'authentication', 'login', 'logout', 'password', 'token', 'oauth',
        'biometric', 'face id', 'touch id', 'kimlik doğrulama', 'şifre',
        # UI/UX
        'button', 'buton', 'form', 'input', 'ekran', 'screen', 'modal',
        'dialog', 'menu', 'navigation', 'navigasyon',
        # Data
        'database', 'veritabanı', 'api', 'endpoint', 'request', 'response',
        'json', 'xml', 'query', 'sorgu',
        # Mobile
        'mobile', 'mobil', 'android', 'ios', 'app', 'uygulama',
        # Payment
        'payment', 'ödeme', 'transaction', 'işlem', 'transfer', 'wallet'
    }

    # Ambiguous words (indicate complexity)
    AMBIGUOUS_WORDS = {
        'optimize', 'improve', 'better', 'good', 'bad', 'slow', 'fast',
        'iyileştir', 'optimize et', 'daha iyi', 'iyi', 'kötü', 'yavaş', 'hızlı',
        'maybe', 'belki', 'veya', 'ya da', 'mümkünse', 'tercihen'
    }

    # Conditional words
    CONDITIONAL_WORDS = {'if', 'eğer', 'when', 'ne zaman', 'depending', 'bağlı olarak'}

    # Negation words
    NEGATION_WORDS = {'not', 'no', 'değil', 'yok', 'olmadan', 'without'}

    def analyze_task(self, task_description: str) -> Tuple[Dict, float]:
        """
        Analyze task using rule-based approach.

        Returns:
            (analysis_result, confidence_score)
            confidence: 0-1 (higher = more confident in rule-based result)
        """
        # Extract basic features
        keywords = self._extract_keywords(task_description)
        intent = self._detect_intent(task_description, keywords)
        scope = self._extract_scope(task_description, keywords)
        entities = self._extract_entities(task_description)
        doc_type_relevance = self._calculate_doc_type_relevance(task_description, keywords, intent)

        # Measure complexity
        metrics = self._calculate_complexity(task_description)
        complexity_score = metrics.calculate_score()

        # Determine complexity level
        if complexity_score < 0.3:
            complexity = 'low'
        elif complexity_score < 0.6:
            complexity = 'medium'
        else:
            complexity = 'high'

        # Build search query
        search_query = self._build_search_query(keywords, entities, scope)

        # Calculate confidence (inverse of complexity)
        # Simple queries = high confidence in rule-based analysis
        # Complex queries = low confidence, should use AI
        confidence = 1.0 - complexity_score

        analysis = {
            'keywords': keywords,
            'intent': intent,
            'scope': scope,
            'entities': entities,
            'doc_type_relevance': doc_type_relevance,
            'complexity': complexity,
            'search_query': search_query,
            'analysis_method': 'rule_based',
            'complexity_score': complexity_score,
            'metrics': {
                'keyword_count': metrics.keyword_count,
                'sentence_count': metrics.sentence_count,
                'total_words': metrics.total_words,
                'technical_terms': metrics.technical_term_count,
                'ambiguous_words': metrics.ambiguous_word_count
            }
        }

        return analysis, confidence

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords using simple tokenization and filtering."""
        # Lowercase and split
        words = re.findall(r'\b\w+\b', text.lower())

        # Filter stop words and short words
        keywords = [
            word for word in words
            if word not in self.TURKISH_STOP_WORDS
            and len(word) > 2
        ]

        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for word in keywords:
            if word not in seen:
                seen.add(word)
                unique_keywords.append(word)

        # Limit to top 10
        return unique_keywords[:10]

    def _detect_intent(self, text: str, keywords: List[str]) -> str:
        """Detect intent using keyword matching."""
        text_lower = text.lower()

        # Count matches for each intent
        intent_scores = {}
        for intent, intent_keywords in self.INTENT_KEYWORDS.items():
            score = sum(1 for kw in intent_keywords if kw in text_lower)
            if score > 0:
                intent_scores[intent] = score

        # Return intent with highest score
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]

        # Default: ADD_FEATURE
        return 'ADD_FEATURE'

    def _extract_scope(self, text: str, keywords: List[str]) -> str:
        """Extract scope/module from text."""
        # Look for patterns like "X sayfası", "Y modülü", "Z ekranı"
        scope_patterns = [
            r'(\w+)\s+(?:sayfası|sayfasına|sayfasında)',
            r'(\w+)\s+(?:ekranı|ekranına|ekranında)',
            r'(\w+)\s+(?:modülü|modülüne|modülünde)',
            r'(\w+)\s+(?:screen|page|module)',
        ]

        for pattern in scope_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).capitalize()

        # Fallback: first technical term or first keyword
        text_lower = text.lower()
        for term in self.TECHNICAL_TERMS:
            if term in text_lower:
                return term.capitalize()

        return keywords[0].capitalize() if keywords else 'Unknown'

    def _extract_entities(self, text: str) -> List[str]:
        """Extract technical entities (terms, features)."""
        text_lower = text.lower()

        entities = []
        for term in self.TECHNICAL_TERMS:
            if term in text_lower:
                entities.append(term.title())

        return entities[:5]  # Limit to 5

    def _calculate_doc_type_relevance(
        self,
        text: str,
        keywords: List[str],
        intent: str
    ) -> Dict[str, float]:
        """Calculate relevance for each document type."""
        # Default: BA is most relevant for features
        relevance = {'ba': 0.7, 'ta': 0.5, 'tc': 0.4}

        # Adjust based on keywords
        text_lower = text.lower()

        # Test-related keywords → TC more relevant
        test_keywords = ['test', 'testleme', 'senaryo', 'scenario', 'case']
        if any(kw in text_lower for kw in test_keywords):
            relevance['tc'] = 0.9
            relevance['ta'] = 0.6
            relevance['ba'] = 0.5

        # Technical keywords → TA more relevant
        tech_keywords = ['api', 'endpoint', 'database', 'backend', 'architecture']
        if any(kw in text_lower for kw in tech_keywords):
            relevance['ta'] = 0.9
            relevance['ba'] = 0.6
            relevance['tc'] = 0.5

        return relevance

    def _calculate_complexity(self, text: str) -> ComplexityMetrics:
        """Calculate complexity metrics for the task description."""
        # Sentence count
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)

        # Word count
        words = re.findall(r'\b\w+\b', text)
        total_words = len(words)

        # Average sentence length
        avg_sentence_length = total_words / sentence_count if sentence_count > 0 else 0

        # Keywords
        keywords = self._extract_keywords(text)
        keyword_count = len(keywords)

        # Question marks
        question_count = text.count('?')

        # Technical terms
        text_lower = text.lower()
        technical_term_count = sum(1 for term in self.TECHNICAL_TERMS if term in text_lower)

        # Ambiguous words
        ambiguous_word_count = sum(1 for word in self.AMBIGUOUS_WORDS if word in text_lower)

        # Conditionals
        has_conditional = any(word in text_lower for word in self.CONDITIONAL_WORDS)

        # Negations
        has_negation = any(word in text_lower for word in self.NEGATION_WORDS)

        return ComplexityMetrics(
            keyword_count=keyword_count,
            sentence_count=sentence_count,
            avg_sentence_length=avg_sentence_length,
            question_count=question_count,
            technical_term_count=technical_term_count,
            ambiguous_word_count=ambiguous_word_count,
            total_words=total_words,
            has_negation=has_negation,
            has_conditional=has_conditional
        )

    def _build_search_query(
        self,
        keywords: List[str],
        entities: List[str],
        scope: str
    ) -> str:
        """Build optimized search query from extracted features."""
        # Combine keywords, entities, and scope
        query_parts = []

        # Add scope if meaningful
        if scope and scope.lower() != 'unknown':
            query_parts.append(scope)

        # Add entities
        query_parts.extend(entities)

        # Add top keywords (not already in entities/scope)
        scope_lower = scope.lower()
        entities_lower = [e.lower() for e in entities]

        for kw in keywords:
            if kw not in scope_lower and kw not in entities_lower:
                query_parts.append(kw)

        # Join and limit
        query = ' '.join(query_parts[:15])  # Max 15 terms

        return query


# Singleton instance
_rule_based_analyzer = None


def get_rule_based_analyzer() -> RuleBasedAnalyzer:
    """Get singleton rule-based analyzer instance."""
    global _rule_based_analyzer
    if _rule_based_analyzer is None:
        _rule_based_analyzer = RuleBasedAnalyzer()
    return _rule_based_analyzer
