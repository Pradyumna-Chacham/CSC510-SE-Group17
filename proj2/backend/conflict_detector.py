"""
Conflict Detector
Identifies conflicting or inconsistent requirements across use cases
"""
from typing import List, Dict
import re


def detect_conflicts(use_cases: List[Dict]) -> List[Dict]:
    """
    Detect conflicts between use cases
    
    Args:
        use_cases: List of use cases to analyze
        
    Returns:
        List of detected conflicts
    """
    conflicts = []
    
    # Check for conflicting preconditions
    conflicts.extend(detect_conflicting_preconditions(use_cases))
    
    # Check for duplicate functionality
    conflicts.extend(detect_duplicate_functionality(use_cases))
    
    # Check for inconsistent terminology
    conflicts.extend(detect_inconsistent_terminology(use_cases))
    
    # Check for missing dependencies
    conflicts.extend(detect_missing_dependencies(use_cases))
    
    # Check for conflicting outcomes
    conflicts.extend(detect_conflicting_outcomes(use_cases))
    
    return conflicts


def detect_conflicting_preconditions(use_cases: List[Dict]) -> List[Dict]:
    """Detect use cases with conflicting preconditions"""
    conflicts = []
    
    for i, uc1 in enumerate(use_cases):
        for uc2 in use_cases[i+1:]:
            # Check if they have similar titles but different preconditions
            title_similarity = calculate_title_similarity(uc1['title'], uc2['title'])
            
            if title_similarity > 0.5:
                # Similar use cases should have similar preconditions
                precond1 = set([p.lower() for p in uc1.get('preconditions', [])])
                precond2 = set([p.lower() for p in uc2.get('preconditions', [])])
                
                # Find contradicting preconditions
                contradictions = find_contradictions(precond1, precond2)
                
                if contradictions:
                    conflicts.append({
                        "type": "conflicting_preconditions",
                        "severity": "high",
                        "use_case_1": uc1['title'],
                        "use_case_2": uc2['title'],
                        "description": f"Similar use cases have conflicting preconditions",
                        "details": contradictions
                    })
    
    return conflicts


def detect_duplicate_functionality(use_cases: List[Dict]) -> List[Dict]:
    """Detect use cases that may represent duplicate functionality"""
    conflicts = []
    
    for i, uc1 in enumerate(use_cases):
        for uc2 in use_cases[i+1:]:
            # Calculate similarity in titles and main flows
            title_sim = calculate_title_similarity(uc1['title'], uc2['title'])
            flow_sim = calculate_flow_similarity(
                uc1.get('main_flow', []),
                uc2.get('main_flow', [])
            )
            
            # High similarity suggests duplication
            if title_sim > 0.7 or flow_sim > 0.6:
                conflicts.append({
                    "type": "duplicate_functionality",
                    "severity": "medium",
                    "use_case_1": uc1['title'],
                    "use_case_2": uc2['title'],
                    "description": "These use cases may represent duplicate functionality",
                    "similarity_score": max(title_sim, flow_sim)
                })
    
    return conflicts


def detect_inconsistent_terminology(use_cases: List[Dict]) -> List[Dict]:
    """Detect inconsistent terminology across use cases"""
    conflicts = []
    
    # Common terms that should be consistent
    term_variations = {
        'user': ['user', 'customer', 'client', 'member'],
        'login': ['login', 'log in', 'sign in', 'authenticate'],
        'register': ['register', 'sign up', 'create account'],
        'remove': ['remove', 'delete', 'erase'],
        'update': ['update', 'modify', 'edit', 'change'],
        'view': ['view', 'see', 'display', 'show'],
    }
    
    # Check for mixed terminology
    for canonical_term, variations in term_variations.items():
        used_variations = set()
        use_case_examples = {}
        
        for uc in use_cases:
            text = ' '.join([
                uc['title'],
                ' '.join(uc.get('main_flow', [])),
                ' '.join(uc.get('preconditions', []))
            ]).lower()
            
            for variation in variations:
                if variation in text:
                    used_variations.add(variation)
                    if variation not in use_case_examples:
                        use_case_examples[variation] = []
                    use_case_examples[variation].append(uc['title'])
        
        # If multiple variations are used, it's inconsistent
        if len(used_variations) > 1:
            conflicts.append({
                "type": "inconsistent_terminology",
                "severity": "low",
                "description": f"Inconsistent terminology for concept '{canonical_term}'",
                "variations_used": list(used_variations),
                "examples": use_case_examples
            })
    
    return conflicts


def detect_missing_dependencies(use_cases: List[Dict]) -> List[Dict]:
    """Detect when a use case references another that doesn't exist"""
    conflicts = []
    
    # Build list of all use case titles
    all_titles = set([uc['title'].lower() for uc in use_cases])
    
    # Common dependency keywords
    dependency_patterns = [
        r'requires?\s+([^,.]+)',
        r'depends?\s+on\s+([^,.]+)',
        r'after\s+([^,.]+)',
        r'following\s+([^,.]+)',
    ]
    
    for uc in use_cases:
        # Check all text in the use case
        text_to_check = ' '.join([
            ' '.join(uc.get('preconditions', [])),
            ' '.join(uc.get('main_flow', [])),
            ' '.join(uc.get('alternate_flows', []))
        ]).lower()
        
        for pattern in dependency_patterns:
            matches = re.findall(pattern, text_to_check)
            for match in matches:
                # Check if the referenced use case exists
                if match.strip() not in all_titles:
                    conflicts.append({
                        "type": "missing_dependency",
                        "severity": "medium",
                        "use_case": uc['title'],
                        "description": f"References '{match}' which doesn't exist as a use case",
                        "suggestion": "Consider adding this as a separate use case or clarifying the reference"
                    })
    
    return conflicts


def detect_conflicting_outcomes(use_cases: List[Dict]) -> List[Dict]:
    """Detect use cases with potentially conflicting outcomes"""
    conflicts = []
    
    for i, uc1 in enumerate(use_cases):
        for uc2 in use_cases[i+1:]:
            outcomes1 = [o.lower() for o in uc1.get('outcomes', [])]
            outcomes2 = [o.lower() for o in uc2.get('outcomes', [])]
            
            # Check for contradicting outcomes
            for out1 in outcomes1:
                for out2 in outcomes2:
                    # Look for negation patterns
                    if is_contradictory(out1, out2):
                        conflicts.append({
                            "type": "conflicting_outcomes",
                            "severity": "high",
                            "use_case_1": uc1['title'],
                            "use_case_2": uc2['title'],
                            "description": "Use cases have contradictory expected outcomes",
                            "outcome_1": out1,
                            "outcome_2": out2
                        })
    
    return conflicts


# Helper functions

def calculate_title_similarity(title1: str, title2: str) -> float:
    """Calculate similarity between two titles (0-1)"""
    words1 = set(title1.lower().split())
    words2 = set(title2.lower().split())
    
    # Remove stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
    words1 = words1 - stop_words
    words2 = words2 - stop_words
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def calculate_flow_similarity(flow1: List[str], flow2: List[str]) -> float:
    """Calculate similarity between two flows"""
    if not flow1 or not flow2:
        return 0.0
    
    # Convert flows to sets of words
    words1 = set()
    for step in flow1:
        words1.update(step.lower().split())
    
    words2 = set()
    for step in flow2:
        words2.update(step.lower().split())
    
    # Remove stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
    words1 = words1 - stop_words
    words2 = words2 - stop_words
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def find_contradictions(set1: set, set2: set) -> List[str]:
    """Find contradicting statements between two sets"""
    contradictions = []
    
    # Negation patterns
    negation_words = ['not', 'no', 'without', 'never', 'none']
    
    for item1 in set1:
        for item2 in set2:
            # Check if one is negation of the other
            if is_contradictory(item1, item2):
                contradictions.append(f"'{item1}' vs '{item2}'")
    
    return contradictions


def is_contradictory(text1: str, text2: str) -> bool:
    """Check if two texts are contradictory"""
    text1_lower = text1.lower()
    text2_lower = text2.lower()
    
    # Remove negations and compare
    negation_patterns = [
        ('not', ''),
        ('no ', ''),
        ('without', 'with'),
        ('never', 'always'),
        ('none', 'all')
    ]
    
    for neg, pos in negation_patterns:
        # Check if one has negation and the other doesn't
        if neg in text1_lower and neg not in text2_lower:
            text1_normalized = text1_lower.replace(neg, pos)
            if text1_normalized in text2_lower or text2_lower in text1_normalized:
                return True
        
        if neg in text2_lower and neg not in text1_lower:
            text2_normalized = text2_lower.replace(neg, pos)
            if text2_normalized in text1_lower or text1_lower in text2_normalized:
                return True
    
    return False
