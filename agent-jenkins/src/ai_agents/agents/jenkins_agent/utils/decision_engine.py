"""Advanced decision engine for JenkinsAgent using LLM-based decision making."""

import json
import os
from typing import Dict, Any, Optional
from openai import OpenAI


def decide_action_with_llm(failure_analysis: Dict[str, Any], build_number: int, 
                          job_name: str = "", retry_count: int = 0,
                          recent_builds_history: str = "N/A") -> Dict[str, Any]:
    """
    Make intelligent decision using LLM analysis.
    
    Args:
        failure_analysis: Result from failure analysis
        build_number: Build number
        job_name: Job name for context
        retry_count: Number of previous retry attempts
        recent_builds_history: Recent builds status
        
    Returns:
        Dictionary with decision, reasoning, confidence, etc.
    """
    
    # Prepare API key and base URL
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENROUTER_API_KEY')
    base_url = os.getenv('OPENAI_API_BASE') or os.getenv('OPENROUTER_BASE_URL') or 'https://openrouter.ai/api/v1'
    
    if not api_key:
        print('[DecisionEngine] No API key found, falling back to rule-based decision')
        return decide_action_fallback(failure_analysis, build_number)
    
    try:
        client = OpenAI(base_url=base_url, api_key=api_key)
        
        # Build comprehensive prompt for decision making
        prompt = f"""Vous êtes un expert DevOps chargé de prendre des décisions sur les actions à entreprendre après un échec de build Jenkins.

## Analyse de l'Échec
{json.dumps(failure_analysis, indent=2)}

## Contexte du Build
- **Job**: {job_name}
- **Build**: #{build_number}
- **Tentatives précédentes**: {retry_count} fois
- **Historique récent**: {recent_builds_history}

## Options de Décision
1. **retry** : Relancer le build immédiatement
   - Approprié pour : erreurs temporaires, problèmes réseau, ressources insuffisantes
   - Limite : Maximum 2 tentatives pour éviter les boucles infinies

2. **notify** : Notifier l'équipe sans action automatique
   - Approprié pour : erreurs de code, configuration, dépendances manquantes
   - Permet une intervention humaine

3. **investigate** : Marquer pour investigation approfondie
   - Approprié pour : causes inconnues, erreurs complexes

## Règles de Décision
- Si retry_count >= 2, NE PAS choisir "retry"
- Pour les erreurs de catégorie "network" ou "resource" avec confidence > 0.7, privilégier "retry"
- Pour les erreurs de code/syntaxe, privilégier "notify"
- Pour les causes inconnues, privilégier "investigate"

## Format de Réponse OBLIGATOIRE
Répondez UNIQUEMENT avec un objet JSON valide (sans markdown) :

{{
  "decision": "retry|notify|investigate",
  "reasoning": "Explication détaillée du choix en français",
  "confidence": 0.85,
  "urgency": "low|medium|high|critical",
  "estimated_fix_time": "immediate|30min|2hours|1day",
  "should_block_pipeline": false,
  "notification_channels": ["email", "slack"],
  "follow_up_actions": [
    "Action si retry échoue",
    "Action préventive"
  ]
}}"""

        completion = client.chat.completions.create(
            model='deepseek/deepseek-r1-0528:free',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3  # Lower temperature for more consistent decisions
        )

        content = completion.choices[0].message.content
        print(f'[DecisionEngine] LLM decision response: {content[:500]}...')

        # Parse JSON response
        decision_result = _parse_json_safely(content)
        
        if not decision_result or not isinstance(decision_result, dict):
            print('[DecisionEngine] Failed to parse LLM decision, using fallback')
            return decide_action_fallback(failure_analysis, build_number)
        
        # Validate decision
        decision = decision_result.get('decision', 'notify')
        if decision not in ['retry', 'notify', 'investigate']:
            decision = 'notify'
        
        # Apply safety rules
        if retry_count >= 2 and decision == 'retry':
            print('[DecisionEngine] Override: Too many retries, changing to notify')
            decision = 'notify'
            decision_result['decision'] = 'notify'
            decision_result['reasoning'] += ' (Override: Maximum retry attempts reached)'
        
        # Ensure required fields
        decision_result.setdefault('decision', decision)
        decision_result.setdefault('confidence', 0.7)
        decision_result.setdefault('urgency', 'medium')
        decision_result.setdefault('reasoning', 'LLM decision')
        
        print(f'[DecisionEngine] LLM decision: {decision} (confidence: {decision_result.get("confidence")})')
        return decision_result
        
    except Exception as e:
        print(f'[DecisionEngine] LLM decision failed: {e}, using fallback')
        return decide_action_fallback(failure_analysis, build_number)


def decide_action_fallback(failure_analysis: Dict[str, Any], build_number: int) -> Dict[str, Any]:
    """
    Fallback rule-based decision making.
    
    Args:
        failure_analysis: Result from failure analysis  
        build_number: Build number
        
    Returns:
        Dictionary with decision and reasoning
    """
    cause = failure_analysis.get('cause', '').lower() if isinstance(failure_analysis, dict) else ''
    category = failure_analysis.get('category', 'unknown').lower()
    confidence = failure_analysis.get('confidence', 0.0)
    
    decision = 'notify'
    reasoning = 'Rule-based fallback decision'
    urgency = 'medium'
    
    # Rule-based logic
    if category in ['network', 'resource'] and confidence > 0.7:
        decision = 'retry'
        reasoning = f'Network/resource issue with high confidence ({confidence}) - retry likely to succeed'
        urgency = 'medium'
    elif category in ['syntax', 'dependency', 'configuration']:
        decision = 'notify'
        reasoning = f'Code/config issue ({category}) - requires manual intervention'
        urgency = 'high'
    elif confidence < 0.5:
        decision = 'investigate'
        reasoning = f'Low confidence analysis ({confidence}) - needs investigation'
        urgency = 'medium'
    elif any(keyword in cause for keyword in ['timeout', 'connection', 'network']):
        decision = 'retry'
        reasoning = 'Detected transient network issue'
        urgency = 'low'
    
    return {
        'decision': decision,
        'reasoning': reasoning,
        'confidence': 0.6,
        'urgency': urgency,
        'estimated_fix_time': 'immediate' if decision == 'retry' else '30min',
        'should_block_pipeline': False,
        'notification_channels': ['email'],
        'follow_up_actions': ['Monitor build results', 'Check system resources']
    }


def _parse_json_safely(text: str) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON from LLM response, handling markdown and other formatting.
    
    Args:
        text: Raw text response from LLM
        
    Returns:
        Parsed JSON object or None if parsing fails
    """
    if not text:
        return None
    
    t = text.strip()
    
    # Remove markdown code blocks
    if t.startswith("```"):
        if t.lower().startswith("```json"):
            t = t[len("```json"):].strip()
        else:
            t = t[3:].strip()
        if t.endswith("```"):
            t = t[:-3].strip()
    
    # Try direct JSON parse
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    
    # Try to extract first JSON object by brace matching
    start = None
    depth = 0
    for i, ch in enumerate(t):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    candidate = t[start:i+1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        continue
    
    return None


# Legacy function for backward compatibility
def decide_action(failure_analysis: dict, build_number: int) -> str:
    """Legacy function - returns simple string decision."""
    result = decide_action_fallback(failure_analysis, build_number)
    return result['decision']
