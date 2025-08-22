"""
Utilities for loading and rendering prompt templates with variable substitution.
"""

import os
from string import Template
from typing import Dict, Any, Optional


def load_prompt_template(template_dir: str, handler_name: str) -> Optional[str]:
    """
    Load a prompt template file for the given handler.
    
    Args:
        template_dir: Directory containing template files
        handler_name: Name of the handler (e.g., 'analyze_failure')
        
    Returns:
        Template content as string, or None if file not found
    """
    template_path = os.path.join(template_dir, f"{handler_name}.tpl")
    
    if os.path.exists(template_path):
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"[TemplateUtils] Error loading template {template_path}: {e}")
            return None
    
    return None


def render_prompt_template(template_content: str, variables: Dict[str, Any]) -> str:
    """
    Render a prompt template with variable substitution.
    
    Args:
        template_content: Template string with $variable placeholders
        variables: Dictionary of variables to substitute
        
    Returns:
        Rendered template string
    """
    if not template_content:
        return ""
    
    try:
        # Convert all variables to strings for template substitution
        str_variables = {}
        for key, value in variables.items():
            if isinstance(value, (dict, list)):
                # Convert complex objects to formatted strings
                import json
                str_variables[key] = json.dumps(value, indent=2)
            elif value is None:
                str_variables[key] = "N/A"
            else:
                str_variables[key] = str(value)
        
        # Use Template for safe substitution
        template = Template(template_content)
        return template.safe_substitute(str_variables)
        
    except Exception as e:
        print(f"[TemplateUtils] Error rendering template: {e}")
        # Return template with error placeholder
        return f"[Template Error: {e}]\n\n{template_content}"


def build_failure_analysis_prompt(job_name: str, build_number: int, console_logs: str, 
                                build_status: str = "FAILURE", timestamp: str = None) -> str:
    """
    Build a structured prompt for failure analysis.
    
    Args:
        job_name: Name of the Jenkins job
        build_number: Build number
        console_logs: Console logs from the build
        build_status: Build status (default: FAILURE)
        timestamp: Build timestamp
        
    Returns:
        Formatted prompt string
    """
    template_vars = {
        'job_name': job_name,
        'build_number': build_number,
        'console_logs': console_logs,
        'build_status': build_status,
        'timestamp': timestamp or "N/A"
    }
    
    # Load template (you would typically get this from template_dir)
    template_content = """Analysez l'échec du build suivant:

Job: $job_name
Build: #$build_number
Status: $build_status
Timestamp: $timestamp

Logs:
$console_logs

Fournissez une analyse structurée avec cause, catégorie, actions suggérées et recommandation."""

    return render_prompt_template(template_content, template_vars)


def build_decision_prompt(failure_analysis: Dict[str, Any], job_name: str, 
                         build_number: int, retry_count: int = 0,
                         recent_builds_history: str = "N/A") -> str:
    """
    Build a structured prompt for decision making.
    
    Args:
        failure_analysis: Result from failure analysis
        job_name: Name of the Jenkins job
        build_number: Build number
        retry_count: Number of previous retry attempts
        recent_builds_history: Recent builds status
        
    Returns:
        Formatted prompt string
    """
    template_vars = {
        'failure_analysis': failure_analysis,
        'job_name': job_name,
        'build_number': build_number,
        'retry_count': retry_count,
        'recent_builds_history': recent_builds_history
    }
    
    template_content = """Prenez une décision basée sur cette analyse:

Analyse de l'échec: $failure_analysis

Job: $job_name
Build: #$build_number
Tentatives précédentes: $retry_count
Historique récent: $recent_builds_history

Décidez: retry, notify, ou investigate avec justification."""

    return render_prompt_template(template_content, template_vars)
