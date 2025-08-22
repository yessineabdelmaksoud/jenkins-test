"""Handlers for the Calculator Agent."""

import re
import operator
import math
from typing import Dict, Any, Union


def start_node(state, model=None, tools=None, memory=None, node_type=None, **kwargs):
    """
    Handle the start node for the calculator workflow.
    
    Args:
        state: The current state containing the mathematical expression
        
    Returns:
        dict: Updated state with the expression to process
    """
    expression = state.get("expression", "2 + 2")
    print(f"🧮 Calculator Agent: Starting calculation for '{expression}'")
    
    return {
        **state,
        "expression": expression,
        "operation_type": "arithmetic"
    }


def parse_mathematical_expression(state, model=None, tools=None, memory=None, node_type=None, **kwargs):
    """
    Parse the mathematical expression and validate it.
    
    Args:
        state: The current state containing the expression
        
    Returns:
        dict: Updated state with parsed expression or error
    """
    expression = state.get("expression", "")
    print(f"🔍 Parsing expression: {expression}")
    
    try:
        # Clean the expression (remove extra spaces)
        cleaned_expr = expression.strip()
        
        # Basic validation - only allow numbers, operators, parentheses, and basic math functions
        allowed_pattern = r'^[0-9+\-*/().\s\^sqrt\(\)sin\(\)cos\(\)tan\(\)log\(\)abs\(\)]+$'
        
        if not re.match(allowed_pattern, cleaned_expr.replace('sqrt', '').replace('sin', '').replace('cos', '').replace('tan', '').replace('log', '').replace('abs', '')):
            raise ValueError("Expression contains invalid characters")
        
        # Replace some common mathematical notations
        cleaned_expr = cleaned_expr.replace('^', '**')  # Power operator
        cleaned_expr = cleaned_expr.replace('sqrt(', 'math.sqrt(')
        cleaned_expr = cleaned_expr.replace('sin(', 'math.sin(')
        cleaned_expr = cleaned_expr.replace('cos(', 'math.cos(')
        cleaned_expr = cleaned_expr.replace('tan(', 'math.tan(')
        cleaned_expr = cleaned_expr.replace('log(', 'math.log(')
        cleaned_expr = cleaned_expr.replace('abs(', 'abs(')
        
        # Detect operation type
        operation_type = "arithmetic"
        if any(func in cleaned_expr for func in ['sqrt', 'sin', 'cos', 'tan', 'log']):
            operation_type = "advanced"
        
        parsed_expression = {
            "original": expression,
            "cleaned": cleaned_expr,
            "valid": True
        }
        
        print(f"✅ Expression parsed successfully: {cleaned_expr}")
        
        return {
            **state,
            "parsed_expression": parsed_expression,
            "operation_type": operation_type
        }
        
    except Exception as e:
        print(f"❌ Error parsing expression: {str(e)}")
        return {
            **state,
            "parsed_expression": {"valid": False, "error": str(e)},
            "error": f"Failed to parse expression: {str(e)}"
        }


def perform_calculation(state, model=None, tools=None, memory=None, node_type=None, **kwargs):
    """
    Perform the actual mathematical calculation.
    
    Args:
        state: The current state containing the parsed expression
        
    Returns:
        dict: Updated state with calculation result or error
    """
    parsed_expr = state.get("parsed_expression", {})
    
    if not parsed_expr.get("valid", False):
        error_msg = parsed_expr.get("error", "Invalid expression")
        print(f"❌ Cannot calculate: {error_msg}")
        return {
            **state,
            "error": error_msg,
            "calculation_result": None
        }
    
    try:
        expression = parsed_expr["cleaned"]
        print(f"🔢 Calculating: {expression}")
        
        # Use eval with restricted globals for safety
        allowed_names = {
            "__builtins__": {},
            "math": math,
            "abs": abs,
        }
        
        result = eval(expression, allowed_names)
        
        print(f"✅ Calculation result: {result}")
        
        return {
            **state,
            "calculation_result": result
        }
        
    except ZeroDivisionError:
        error_msg = "Division by zero is not allowed"
        print(f"❌ {error_msg}")
        return {
            **state,
            "error": error_msg,
            "calculation_result": None
        }
    except Exception as e:
        error_msg = f"Calculation error: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            **state,
            "error": error_msg,
            "calculation_result": None
        }


def format_result(state, model=None, tools=None, memory=None, node_type=None, **kwargs):
    """
    Format the calculation result for presentation.
    
    Args:
        state: The current state containing the calculation result
        
    Returns:
        dict: Updated state with formatted result
    """
    result = state.get("calculation_result")
    expression = state.get("expression", "")
    operation_type = state.get("operation_type", "arithmetic")
    error = state.get("error")
    
    if error:
        formatted_result = f"❌ Error: {error}"
        print(f"📝 Formatted error: {formatted_result}")
    elif result is not None:
        # Format the result nicely
        if isinstance(result, float):
            if result.is_integer():
                formatted_result = f"🧮 {expression} = {int(result)}"
            else:
                formatted_result = f"🧮 {expression} = {result:.6f}".rstrip('0').rstrip('.')
        else:
            formatted_result = f"🧮 {expression} = {result}"
        
        print(f"📝 Formatted result: {formatted_result}")
    else:
        formatted_result = "❌ No result available"
        print(f"📝 {formatted_result}")
    
    return {
        **state,
        "formatted_result": formatted_result
    }


def end_node(state, model=None, tools=None, memory=None, node_type=None, **kwargs):
    """
    Handle the end node for the calculator workflow.
    
    Args:
        state: The current state with all processing complete
        
    Returns:
        dict: Final state with summary
    """
    formatted_result = state.get("formatted_result", "No result")
    operation_type = state.get("operation_type", "unknown")
    
    print(f"🏁 Calculator Agent: Completed {operation_type} operation")
    print(f"📊 Final result: {formatted_result}")
    
    return {
        **state,
        "final_answer": formatted_result,
        "status": "completed",
        "agent_type": "calculator"
    }


def handle_error(state, model=None, tools=None, memory=None, node_type=None, **kwargs):
    """
    Handle errors in the calculator workflow.
    
    Args:
        state: The current state when error occurred
        
    Returns:
        dict: Error state
    """
    error = state.get("error", "Unknown error occurred")
    expression = state.get("expression", "")
    
    print(f"🚨 Calculator Agent Error: {error}")
    
    return {
        **state,
        "final_answer": f"❌ Calculator Error: {error}",
        "status": "failed",
        "agent_type": "calculator"
    }
