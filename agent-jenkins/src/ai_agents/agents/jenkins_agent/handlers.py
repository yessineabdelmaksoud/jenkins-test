"""Handlers for JenkinsAgent - skeleton implementations.

Each function should accept (state, model, tools, memory, node_type, **kwargs)
and return an updated state dict with a `next` key for the next node name when applicable.
"""

from typing import Dict, Any
import os
import json
from openai import OpenAI
from .jenkins.data_extractor import extract_complete_data
from .jenkins.client import JenkinsClient
from .utils.decision_engine import decide_action_with_llm, decide_action_fallback
from .notifications.email_notifier import notify_email
from .notifications.slack_notifier import notify_slack
from .prompts.template_utils import load_prompt_template, render_prompt_template


def receive_webhook(state: Dict[str, Any], model=None, tools=None, memory=None, node_type=None, **kwargs):
    """Entry node: receive webhook payload and validate it."""
    print("[JenkinsAgent] receive_webhook - entering")
    try:
        payload = state.get("input", {}) or state.get("webhook_data")
        print("[JenkinsAgent] receive_webhook - payload keys:", list(payload.keys()) if isinstance(payload, dict) else type(payload))
        if not payload:
            print("[JenkinsAgent] receive_webhook - no payload provided")
            return {**state, "error": "No webhook payload provided", "next_node": "handle_error"}
        # store payload
        print(f"[JenkinsAgent] receive_webhook - storing webhook_data: {payload}")
        return {**state, "webhook_data": payload, "next_node": "extract_job_data"}
    except Exception as e:
        print(f"[JenkinsAgent] receive_webhook - exception: {e}")
        return {**state, "error": str(e), "next_node": "handle_error"}


def extract_job_data(state: Dict[str, Any], model=None, tools=None, memory=None, node_type=None, **kwargs):
    """Extract logs, jenkinsfile and metadata using extract_complete_data.

    - Prefer values from webhook_data if present
    - Fall back to environment variables for Jenkins URL and credentials
    """
    print("[JenkinsAgent] extract_job_data - entering")
    try:
        payload = state.get("webhook_data") or state.get("input") or {}
        print("[JenkinsAgent] extract_job_data - payload sample:", {k: payload.get(k) for k in list(payload.keys())[:5]} if isinstance(payload, dict) else payload)
        
        # Check if build is finalized and add delay for logs to be available
        build_info = payload.get("build", {})
        if build_info.get("phase") == "FINALIZED":
            import time
            print("[JenkinsAgent] extract_job_data - build finalized, waiting 5 seconds for logs...")
            time.sleep(10)
        
        job_name = payload.get("job_name") or payload.get("name")
        # support different webhook shapes
        build_number = payload.get("build_number") or (payload.get("build", {}) or {}).get("number")
        if build_number is None:
            # try top-level build_number
            build_number = payload.get("buildNumber")

        try:
            build_number_int = int(build_number) if build_number is not None else 0
        except Exception:
            build_number_int = 0

        jenkins_url = payload.get("jenkins_url") or os.getenv("JENKINS_URL")
        username = payload.get("jenkins_user") or os.getenv("JENKINS_USER")
        api_token = payload.get("jenkins_token") or os.getenv("JENKINS_TOKEN")

        if not jenkins_url or not job_name:
            print(f"[JenkinsAgent] extract_job_data - missing jenkins_url or job_name (jenkins_url={jenkins_url}, job_name={job_name})")
            return {**state, "error": "Missing jenkins_url or job_name", "next_node": "handle_error"}

        try:
            print(f"[JenkinsAgent] extract_job_data - calling extract_complete_data (url={jenkins_url}, job={job_name}, build={build_number_int})")
            # Enable sanitization by default, with option to disable via environment variable
            sanitize_logs = os.getenv('JENKINS_SANITIZE_LOGS', 'true').lower() in ('true', '1', 'yes')
            enable_advanced_pii = os.getenv('JENKINS_ENABLE_ADVANCED_PII', 'false').lower() in ('true', '1', 'yes')
            
            extracted = extract_complete_data(
                jenkins_url, job_name, build_number_int, username, api_token,
                sanitize_logs=sanitize_logs, enable_advanced_pii=enable_advanced_pii
            )
            print("[JenkinsAgent] extract_job_data - extraction succeeded; keys:", list(extracted.keys()))
            
            # Check if logs are empty and retry once
            console_log = extracted.get("console_log", "")
            if not console_log or len(console_log.strip()) < 10:
                print("[JenkinsAgent] extract_job_data - logs seem empty, retrying in 10 seconds...")
                import time
                time.sleep(10)
                extracted = extract_complete_data(
                    jenkins_url, job_name, build_number_int, username, api_token,
                    sanitize_logs=sanitize_logs, enable_advanced_pii=enable_advanced_pii
                )
                print("[JenkinsAgent] extract_job_data - retry extraction; new log size:", len(extracted.get("console_log", "")))
                
        except Exception as e:
            print(f"[JenkinsAgent] extract_job_data - extraction failed: {e}")
            return {**state, "error": f"extract_failed: {e}", "next_node": "handle_error"}

        # Merge extracted data into state
        merged = {**state, **extracted}
        # Ensure canonical keys
        merged["job_name"] = job_name
        merged["build_number"] = build_number_int
        # Use status from extracted data, fallback to webhook payload
        build_status = extracted.get("status") or payload.get("build", {}).get("status") or payload.get("status")
        merged["build_status"] = build_status
        merged["jenkins_logs"] = extracted.get("console_log")
        merged["jenkinsfile_content"] = extracted.get("jenkinsfile")
        merged["metadata"] = extracted.get("metadata")
        merged["next_node"] = "analyze_status"
        print(f"[JenkinsAgent] extract_job_data - merged state summary: job={merged.get('job_name')}, build={merged.get('build_number')}, status={merged.get('build_status')}")
        return merged
    except Exception as e:
        print(f"[JenkinsAgent] extract_job_data - exception: {e}")
        return {**state, "error": str(e), "next_node": "handle_error"}


def analyze_status(state: Dict[str, Any], model=None, tools=None, memory=None, node_type=None, **kwargs):
    """Decide path based on build_status"""
    print("[JenkinsAgent] analyze_status - entering")
    status = (state.get("build_status") or "UNKNOWN").upper()
    print(f"[JenkinsAgent] analyze_status - build_status={status}")
    if status == "SUCCESS":
        print("[JenkinsAgent] analyze_status - routing to handle_success")
        return {**state, "next_node": "handle_success"}
    elif status == "FAILURE":
        print("[JenkinsAgent] analyze_status - routing to handle_failure")
        return {**state, "next_node": "handle_failure"}
    else:
        # WAITING / NOT_BUILT / UNSTABLE / ABORTED (and others): simple status email
        print("[JenkinsAgent] analyze_status - other status, routing to handle_other_status")
        return {**state, "next_node": "handle_other_status"}


def handle_other_status(state: Dict[str, Any], model=None, tools=None, memory=None, node_type=None, **kwargs):
    """Handle non-success/non-failure statuses by sending a simple status email.

    Targets statuses like WAITING, NOT_BUILT, UNSTABLE, ABORTED, etc. No LLM.
    """
    print("[JenkinsAgent] handle_other_status - entering")
    try:
        status = state.get("build_status") or "UNKNOWN"
        job = state.get("job_name")
        build = state.get("build_number")
        summary = (
            f"Job '{job}' build #{build} is currently in status: {status}. "
            "No analysis performed. This is a status notification."
        )
        content = {
            "job": job,
            "build": build,
            "status": status,
            "action": "status_update",
            "summary": summary,
        }
        print(f"[JenkinsAgent] handle_other_status - content summary: {content}")
        return {**state, "notification_content": content, "next_node": "send_notifications"}
    except Exception as e:
        print(f"[JenkinsAgent] handle_other_status - exception: {e}")
        return {**state, "error": str(e), "next_node": "handle_error"}


def handle_failure(state: Dict[str, Any], model=None, tools=None, memory=None, node_type=None, prompt_template=None, **kwargs):
    """Analyze failure and prepare decision inputs using LLM with structured prompts."""
    print("[JenkinsAgent] handle_failure - entering LLM analysis")
    try:
        logs = state.get('jenkins_logs') or ''
        job = state.get('job_name')
        build = state.get('build_number')

        # Prepare API key and base URL
        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENROUTER_API_KEY')
        base_url = os.getenv('OPENAI_API_BASE') or os.getenv('OPENROUTER_BASE_URL') or 'https://openrouter.ai/api/v1'
        
        if not api_key:
            print('[JenkinsAgent] handle_failure - No API key found; using fallback analysis')
            failure_analysis = {'cause': 'unknown', 'suggested_actions': [], 'confidence': 0.0, 'category': 'unknown'}
            return {**state, 'failure_analysis': failure_analysis, 'next_node': 'make_decision'}

        client = OpenAI(base_url=base_url, api_key=api_key)

        # Use structured prompt if available
        if prompt_template:
            # Prepare template variables
            template_vars = {
                'job_name': job,
                'build_number': build,
                'build_status': state.get('build_status', 'FAILURE'),
                'timestamp': state.get('timestamp', 'N/A'),
                'console_logs': logs  
            }
            prompt = render_prompt_template(prompt_template, template_vars)
        else:
            # Fallback to original prompt
            log_sample = logs
            if logs:
                if len(logs) <= 4000:
                    log_sample = logs
                else:
                    log_sample = logs[:2000] + "\n\n... [LOG TRUNCATED] ...\n\n" + logs[-2000:]
            
            prompt = ( 
                f"Analyze the following Jenkins build logs for job={job} build={build}. "
                "Return a JSON object with keys: cause (string), suggested_actions (array of strings), confidence (0-1), category (string). "
                "Categories: network, dependency, syntax, configuration, resource, permission, unknown. "
                "Pay special attention to:\n"
                "- Python runtime errors (exceptions, import errors, syntax errors)\n"
                "- Missing dependencies or files\n"
                "- Configuration issues\n"
                "- Connection failures\n"
                "Look for the ACTUAL error at the end of the logs, not just the beginning.\n"
                "Provide only valid JSON as the response.\n\nLogs:\n" + (log_sample if log_sample else "<no logs provided>")
            )

        print('[JenkinsAgent] handle_failure - sending structured prompt to LLM')
        completion = client.chat.completions.create(
            extra_body={},
            model='deepseek/deepseek-r1-0528:free',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.2  # Lower temperature for more consistent analysis
        )

        content = completion.choices[0].message.content
        print('[JenkinsAgent] handle_failure - LLM raw response:', (content[:1000] + '...') if len(content) > 1000 else content)

        # Parse JSON response more robustly
        failure_analysis = _parse_failure_json(content)
        
        if not isinstance(failure_analysis, dict):
            print('[JenkinsAgent] handle_failure - unable to parse JSON from LLM response; using fallback')
            failure_analysis = {'cause': 'unknown', 'suggested_actions': [], 'confidence': 0.0, 'category': 'unknown'}

        # Extract recommendation from structured analysis
        recommendation = failure_analysis.get('recommendation', '')
        if not recommendation:
            # Fallback to first suggested action
            suggested_actions = failure_analysis.get('suggested_actions') if isinstance(failure_analysis.get('suggested_actions'), list) else []
            recommendation = suggested_actions[0] if suggested_actions else 'investigate'

        print(f"[JenkinsAgent] handle_failure - analysis complete: category={failure_analysis.get('category')}, confidence={failure_analysis.get('confidence')}, recommendation={recommendation}")

        return {**state, 'failure_analysis': failure_analysis, 'llm_recommendation': recommendation, 'next_node': 'make_decision'}
    except Exception as e:
        print(f"[JenkinsAgent] handle_failure - exception: {e}")
        return {**state, 'error': str(e), 'next_node': 'handle_error'}


def _parse_failure_json(content: str) -> Dict[str, Any]:
    """Parse JSON from LLM failure analysis response."""
    if not content:
        return {}
    
    t = content.strip()
    
    # Remove markdown formatting
    if t.startswith("```"):
        if t.lower().startswith("```json"):
            t = t[len("```json"):].strip()
        else:
            t = t[3:].strip()
        if t.endswith("```"):
            t = t[:-3].strip()
    
    # Try direct parse
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON object
    start = t.find('{')
    end = t.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(t[start:end+1])
        except json.JSONDecodeError:
            pass
    
    return {}


def make_decision(state: Dict[str, Any], model=None, tools=None, memory=None, node_type=None, prompt_template=None, **kwargs):
    """Enhanced decision making using LLM with structured reasoning."""
    print("[JenkinsAgent] make_decision - entering enhanced decision process")
    try:
        failure_analysis = state.get('failure_analysis', {})
        job = state.get('job_name')
        build = state.get('build_number')
        retry_count = state.get('retry_count', 0)  # Track retry attempts
        llm_recommendation = state.get('llm_recommendation', '')
        
        # Collect recent builds history for context (simplified)
        recent_builds_history = "Last 3 builds: #48(SUCCESS), #49(FAILURE), #50(FAILURE)"  # Placeholder
        
        # Check if LLM suggested retry directly in the failure analysis
        should_retry = False
        cause = failure_analysis.get('cause', '').lower()
        suggested_actions = failure_analysis.get('suggested_actions', [])
        
        # Check for retry indicators in cause and suggested actions
        retry_keywords = ['relance', 'retry', 'restart', 'retrigger', 'network', 'timeout', 'connection', 'temporary']
        
        # Check cause for retry indicators
        if any(keyword in cause for keyword in retry_keywords):
            should_retry = True
            print(f"[JenkinsAgent] make_decision - retry keyword found in cause: {cause}")
        
        # Check suggested actions for retry indicators
        for action in suggested_actions:
            action_lower = action.lower()
            if any(keyword in action_lower for keyword in retry_keywords):
                should_retry = True
                print(f"[JenkinsAgent] make_decision - retry keyword found in action: {action}")
                break
        
        # Use advanced LLM-based decision making
        decision_result = decide_action_with_llm(
            failure_analysis=failure_analysis,
            build_number=build,
            job_name=job,
            retry_count=retry_count,
            recent_builds_history=recent_builds_history
        )
        
        decision = decision_result.get('decision', 'notify')
        reasoning = decision_result.get('reasoning', 'Default reasoning')
        
        # Override decision if retry indicators found and retry count is low
        if should_retry and retry_count < 2:
            if decision != 'retry':
                print(f"[JenkinsAgent] make_decision - overriding LLM decision to 'retry' due to retry indicators")
                decision = 'retry'
                reasoning = f"Override: Detected retry indicators in failure analysis. Original reasoning: {reasoning}"
                decision_result['decision'] = decision
                decision_result['reasoning'] = reasoning
        
        confidence = decision_result.get('confidence', 0.7)
        urgency = decision_result.get('urgency', 'medium')
        
        print(f"[JenkinsAgent] make_decision - Final decision: {decision}")
        print(f"[JenkinsAgent] make_decision - Reasoning: {reasoning}")
        print(f"[JenkinsAgent] make_decision - Confidence: {confidence}, Urgency: {urgency}")
        print(f"[JenkinsAgent] make_decision - Retry count: {retry_count}, Should retry: {should_retry}")
        
        # Store comprehensive decision info in state
        decision_info = {
            'decision': decision,
            'reasoning': reasoning,
            'confidence': confidence,
            'urgency': urgency,
            'estimated_fix_time': decision_result.get('estimated_fix_time', '30min'),
            'should_block_pipeline': decision_result.get('should_block_pipeline', False),
            'notification_channels': decision_result.get('notification_channels', ['email']),
            'follow_up_actions': decision_result.get('follow_up_actions', []),
            'retry_indicators_found': should_retry
        }
        
        return {**state, 'decision': decision, 'decision_info': decision_info, 'retry_count': retry_count, 'next_node': 'execute_action'}
    except Exception as e:
        print(f"[JenkinsAgent] make_decision - exception: {e}")
        # Fallback to simple decision
        fallback_decision = decide_action_fallback(state.get('failure_analysis', {}), state.get('build_number', 0))
        return {**state, 'decision': fallback_decision['decision'], 'decision_info': fallback_decision, 'next_node': 'execute_action'}


def execute_action(state: Dict[str, Any], model=None, tools=None, memory=None, node_type=None, **kwargs):
    """Execute the decided action with enhanced logging and retry tracking."""
    print("[JenkinsAgent] execute_action - entering")
    try:
        decision = state.get('decision')
        decision_info = state.get('decision_info', {})
        job = state.get('job_name')
        build = state.get('build_number')
        retry_count = state.get('retry_count', 0)

        # Resolve Jenkins connection info
        jenkins_url = state.get('jenkins_url') or os.getenv('JENKINS_URL')
        username = state.get('jenkins_user') or os.getenv('JENKINS_USER')
        api_token = state.get('jenkins_token') or os.getenv('JENKINS_TOKEN')

        print(f"[JenkinsAgent] execute_action - decision: {decision}, retry_count: {retry_count}")
        
        if decision == 'retry':
            if not jenkins_url or not job:
                print('[JenkinsAgent] execute_action - missing jenkins_url or job for retry')
                return {**state, 'action_taken': 'retry_failed_missing_info', 'next_node': 'format_notification'}
            
            # Check retry limits
            max_retries = 2
            if retry_count >= max_retries:
                print(f'[JenkinsAgent] execute_action - maximum retry attempts reached ({retry_count}/{max_retries})')
                return {**state, 'action_taken': 'retry_limit_exceeded', 'next_node': 'format_notification'}
            
            try:
                client = JenkinsClient(jenkins_url, username, api_token)
                print(f"[JenkinsAgent] execute_action - triggering build for job={job} (attempt #{retry_count + 1})")
                status = client.trigger_build(job)
                print(f"[JenkinsAgent] execute_action - trigger_build returned: {status}")
                
                # Update retry count
                new_retry_count = retry_count + 1
                
                return {
                    **state, 
                    'action_taken': 'retriggered', 
                    'trigger_result': status, 
                    'retry_count': new_retry_count,
                    'next_node': 'format_notification'
                }
            except Exception as e:
                print(f"[JenkinsAgent] execute_action - trigger failed: {e}")
                return {**state, 'action_taken': 'retry_failed', 'error': str(e), 'next_node': 'format_notification'}

        elif decision == 'investigate':
            print('[JenkinsAgent] execute_action - marking for investigation')
            return {
                **state, 
                'action_taken': 'investigation_required', 
                'investigation_priority': decision_info.get('urgency', 'medium'),
                'next_node': 'format_notification'
            }

        # default: notify only
        print('[JenkinsAgent] execute_action - notification action')
        return {**state, 'action_taken': 'notified', 'next_node': 'format_notification'}

    except Exception as e:
        print(f"[JenkinsAgent] execute_action - exception: {e}")
        return {**state, 'error': str(e), 'next_node': 'handle_error'}


def handle_success(state: Dict[str, Any], model=None, tools=None, memory=None, node_type=None, **kwargs):
    """On success: analyze Jenkinsfile with LLM and propose improvements.

    Sends only the Jenkinsfile to the LLM and stores a structured analysis with
    suggested improvements. Then routes to suggest_improvements and normal
    notifications.
    """
    print("[JenkinsAgent] handle_success - entering")
    try:
        jenkinsfile = state.get('jenkinsfile_content') or state.get('jenkinsfile') or ''
        print(f"[JenkinsAgent] handle_success - jenkinsfile length: {len(jenkinsfile) if jenkinsfile else 0}")

        improvements: list = []
        success_analysis = None

        def _parse_json_safely(text: str):
            if not text:
                return None
            t = text.strip()
            # Strip code fences like ```json ... ```
            if t.startswith("```"):
                if t.lower().startswith("```json"):
                    t = t[len("```json"):].strip()
                else:
                    t = t[3:].strip()
                if t.endswith("```"):
                    t = t[:-3].strip()
            # First try direct parse
            try:
                return json.loads(t)
            except Exception:
                pass
            # Try to extract the first top-level JSON object by brace scanning
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
                            except Exception:
                                continue
            return None

        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENROUTER_API_KEY')
        base_url = os.getenv('OPENAI_API_BASE') or os.getenv('OPENROUTER_BASE_URL') or 'https://openrouter.ai/api/v1'
        if api_key and jenkinsfile:
            try:
                client = OpenAI(base_url=base_url, api_key=api_key)
                prompt = (
                    "Review the following Jenkins Declarative Pipeline (Jenkinsfile). "
                    "Return ONLY a valid JSON object (no markdown, no backticks) with keys: "
                    "summary (string), improvements (array of concise strings), confidence (0-1). "
                    "Focus on best practices (stages, agents, options, timeouts, retries), caching, "
                    "parallelization, reproducibility, security (credentials, secrets), notifications, and maintainability.\n\n"
                    "Jenkinsfile:\n" + jenkinsfile
                )
                print('[JenkinsAgent] handle_success - sending Jenkinsfile to LLM')
                completion = client.chat.completions.create(
                    extra_body={},
                    model='deepseek/deepseek-r1-0528:free',
                    messages=[{'role': 'user', 'content': prompt}],
                )
                content = ''
                try:
                    content = completion.choices[0].message.content
                except Exception:
                    content = getattr(completion.choices[0], 'message', getattr(completion.choices[0], 'text', ''))

                print('[JenkinsAgent] handle_success - LLM raw response:', (content[:600] + '...') if len(content) > 600 else content)

                success_analysis = _parse_json_safely(content)
                if isinstance(success_analysis, dict):
                    imps = success_analysis.get('improvements')
                    if isinstance(imps, list):
                        improvements = [str(x) for x in imps][:10]
                else:
                    success_analysis = {'summary': 'No structured analysis returned', 'improvements': [], 'confidence': 0.0}
            except Exception as e:
                print(f"[JenkinsAgent] handle_success - LLM analysis failed: {e}")
                success_analysis = {'summary': 'LLM analysis failed', 'improvements': [], 'confidence': 0.0}
        else:
            if not api_key:
                print('[JenkinsAgent] handle_success - OPENAI_API_KEY not set; skipping LLM analysis')
            if not jenkinsfile:
                print('[JenkinsAgent] handle_success - Jenkinsfile missing; skipping LLM analysis')
            success_analysis = {'summary': 'No analysis performed', 'improvements': [], 'confidence': 0.0}

        return {**state, 'improvements': improvements, 'success_analysis': success_analysis, 'next_node': 'suggest_improvements'}
    except Exception as e:
        print(f"[JenkinsAgent] handle_success - exception: {e}")
        return {**state, 'error': str(e), 'next_node': 'handle_error'}


def suggest_improvements(state: Dict[str, Any], model=None, tools=None, memory=None, node_type=None, **kwargs):
    """Pass through improvements generated on success.

    Keeps improvements in state; can be extended to filter/rank if needed.
    """
    print("[JenkinsAgent] suggest_improvements - entering")
    try:
        improvements = state.get('improvements', []) or []
        print(f"[JenkinsAgent] suggest_improvements - improvements count: {len(improvements)}")
        return {**state, 'improvements': improvements, 'next_node': 'format_notification'}
    except Exception as e:
        print(f"[JenkinsAgent] suggest_improvements - exception: {e}")
        return {**state, 'error': str(e), 'next_node': 'handle_error'}


def format_notification(state: Dict[str, Any], model=None, tools=None, memory=None, node_type=None, prompt_template=None, **kwargs):
    """Construct enhanced notification content using template."""
    print("[JenkinsAgent] format_notification - entering")
    try:
        status = (state.get('build_status') or '').upper()
        decision_info = state.get('decision_info', {})
        failure_analysis = state.get('failure_analysis', {})
        
        # Prepare base content
        content = {
            'job': state.get('job_name'),
            'build': state.get('build_number'),
            'status': state.get('build_status'),
            'action': state.get('action_taken'),
            'decision_info': decision_info
        }
        
        # Use template if available
        if prompt_template:
            # Prepare template variables for notification formatting
            template_vars = {
                'job_name': state.get('job_name', 'N/A'),
                'build_number': state.get('build_number', 'N/A'),
                'build_status': state.get('build_status', 'UNKNOWN'),
                'action_taken': state.get('action_taken', 'N/A'),
                'decision': decision_info.get('decision', 'N/A'),
                'decision_reasoning': decision_info.get('reasoning', 'N/A'),
                'confidence': decision_info.get('confidence', 'N/A'),
                'urgency': decision_info.get('urgency', 'N/A'),
                'estimated_fix_time': decision_info.get('estimated_fix_time', 'N/A'),
                'retry_count': state.get('retry_count', 0),
                'follow_up_actions': '\n'.join([f"• {action}" for action in decision_info.get('follow_up_actions', [])]) or 'None specified'
            }
            
            # Format analysis summary based on status
            if status == 'SUCCESS':
                success_analysis = state.get('success_analysis', {})
                improvements = state.get('improvements', [])
                if success_analysis:
                    template_vars['analysis_summary'] = f"✅ **Success Analysis**: {success_analysis.get('summary', 'Build completed successfully')}"
                    if improvements:
                        template_vars['analysis_summary'] += f"\n\n💡 **Suggested Improvements**:\n" + '\n'.join([f"• {imp}" for imp in improvements[:5]])
                else:
                    template_vars['analysis_summary'] = "✅ Build completed successfully"
            else:
                # Failure or other status
                if failure_analysis:
                    cause = failure_analysis.get('cause', 'Unknown cause')
                    category = failure_analysis.get('category', 'unknown')
                    confidence = failure_analysis.get('confidence', 0.0)
                    template_vars['analysis_summary'] = f"❌ **Cause**: {cause}\n📂 **Category**: {category.title()}\n🎯 **Confidence**: {confidence:.1%}"
                    
                    suggested_actions = failure_analysis.get('suggested_actions', [])
                    if suggested_actions:
                        template_vars['analysis_summary'] += f"\n\n🔧 **Suggested Actions**:\n" + '\n'.join([f"• {action}" for action in suggested_actions[:3]])
                else:
                    template_vars['analysis_summary'] = f"Status: {status} - No detailed analysis available"
            
            # Render template
            formatted_message = render_prompt_template(prompt_template, template_vars)
            content['formatted_message'] = formatted_message
            content['template_used'] = True
        else:
            # Fallback formatting
            content['template_used'] = False
        
        # Legacy summary for backward compatibility
        if status == 'SUCCESS':
            success_analysis = state.get('success_analysis')
            improvements = state.get('improvements') or []
            content['summary'] = success_analysis or {'improvements': improvements}
        else:
            content['summary'] = failure_analysis or 'No analysis available'

        print(f"[JenkinsAgent] format_notification - content prepared with template: {content.get('template_used', False)}")
        return {**state, 'notification_content': content, 'next_node': 'send_notifications'}
    except Exception as e:
        print(f"[JenkinsAgent] format_notification - exception: {e}")
        return {**state, 'error': str(e), 'next_node': 'handle_error'}


def send_notifications(state: Dict[str, Any], model=None, tools=None, memory=None, node_type=None, **kwargs):
    """Send notifications via available notifiers.

    Uses notify_email and notify_slack. Notification configuration may come from state['notification_config']
    or environment variables.
    """
    print("[JenkinsAgent] send_notifications - entering")
    try:
        content = state.get('notification_content', {})
        print(f"[JenkinsAgent] send_notifications - notification content: {content}")

        notif_cfg = state.get('notification_config', {}) or {}
        # email config
        email_cfg = notif_cfg.get('email', {})
        email_cfg.setdefault('smtp_host', os.getenv('SMTP_HOST', 'smtp.gmail.com'))
        email_cfg.setdefault('smtp_port', int(os.getenv('SMTP_PORT', 587)))
        email_cfg.setdefault('username', os.getenv('EMAIL_SENDER'))
        email_cfg.setdefault('password', os.getenv('EMAIL_PASSWORD'))
        email_cfg.setdefault('to', notif_cfg.get('email', {}).get('to') or os.getenv('EMAIL_TO'))

        # slack config
        slack_cfg = notif_cfg.get('slack', {})
        slack_webhook = slack_cfg.get('webhook_url') or os.getenv('SLACK_WEBHOOK_URL')

        results = {}
        # Send email if email recipients configured
        try:
            if email_cfg.get('username') and (email_cfg.get('to')):
                print(f"[JenkinsAgent] send_notifications - sending email to: {email_cfg.get('to')}")
                notify_email(email_cfg, content)
                results['email'] = 'sent'
            else:
                print('[JenkinsAgent] send_notifications - email not configured, skipping')
                results['email'] = 'skipped'
        except Exception as e:
            print(f"[JenkinsAgent] send_notifications - email send failed: {e}")
            results['email'] = f'error: {e}'

        # Send slack if webhook configured
        try:
            if slack_webhook:
                print(f"[JenkinsAgent] send_notifications - sending slack to webhook")
                notify_slack(slack_webhook, content)
                results['slack'] = 'sent'
            else:
                print('[JenkinsAgent] send_notifications - slack webhook not configured, skipping')
                results['slack'] = 'skipped'
        except Exception as e:
            print(f"[JenkinsAgent] send_notifications - slack send failed: {e}")
            results['slack'] = f'error: {e}'

        print(f"[JenkinsAgent] send_notifications - results: {results}")
        return {**state, 'notification_sent': True, 'notification_results': results, 'next_node': 'end_process'}
    except Exception as e:
        print(f"[JenkinsAgent] send_notifications - exception: {e}")
        return {**state, 'error': str(e), 'next_node': 'handle_error'}


def end_process(state: Dict[str, Any], model=None, tools=None, memory=None, node_type=None, **kwargs):
    print("[JenkinsAgent] end_process - entering, workflow complete")
    return {**state, "status": "done"}


def handle_error(state: Dict[str, Any], model=None, tools=None, memory=None, node_type=None, **kwargs):
    print(f"[JenkinsAgent] handle_error - error state: {state.get('error')}")
    return {**state, "status": "error"}
