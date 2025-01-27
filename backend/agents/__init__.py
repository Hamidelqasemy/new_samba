import os
import concurrent.futures
import re
import openai
from .financial_agent import FinancialAgent
from .legal_agent import LegalAgent
from .technical_agent import TechnicalAgent

client = openai.OpenAI(
    api_key="7677e8aa-8a22-47d1-9c98-6beeca0d3696",
    base_url="https://api.sambanova.ai/v1",
)

def analyze_proposals(proposals):
    agents = {
        'financial': FinancialAgent(client),
        'legal': LegalAgent(client),
        'technical': TechnicalAgent(client)
    }
    
    results = {}
    
    if len(proposals) == 1:
        # Single file analysis mode
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(agent.analyze_single, proposals[0]): name
                for name, agent in agents.items()
            }
            for future in concurrent.futures.as_completed(futures):
                agent_name = futures[future]
                results[agent_name] = future.result()
        
        return {
            'financial': results['financial'],
            'legal': results['legal'],
            'technical': results['technical'],
            'final': generate_single_report(results),
            'scores': compile_single_scores(results, proposals[0])
        }
    else:
        # Multi-file comparison mode
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(agent.analyze, proposals): name
                for name, agent in agents.items()
            }
            for future in concurrent.futures.as_completed(futures):
                agent_name = futures[future]
                results[agent_name] = future.result()
        
        return {
            'financial': results['financial'],
            'legal': results['legal'],
            'technical': results['technical'],
            'final': generate_comparison_report(results),
            'scores': compile_comparison_scores(results, proposals)
        }

def compile_single_scores(results, proposal):
    return {
        proposal['filename']: {
            'financial': results['financial']['scores'].get('overall', 0),
            'technical': results['technical']['scores'].get('overall', 0),
            'legal': results['legal']['scores'].get('overall', 0),
            'overall': calculate_overall_score(results, proposal['filename']),
            'technical_breakdown': [
                results['technical']['scores'].get('feasibility', 0),
                results['technical']['scores'].get('innovation', 0),
                results['technical']['scores'].get('scalability', 0),
                results['technical']['scores'].get('security', 0),
                results['technical']['scores'].get('compliance', 0)
            ]
        }
    }

def compile_comparison_scores(results, proposals):
    return {
        p['filename']: {
            'financial': results['financial']['scores'].get('overall', 0),
            'technical': results['technical']['scores'].get('overall', 0),
            'legal': results['legal']['scores'].get('overall', 0),
            'overall': calculate_overall_score(results, p['filename']),
            'technical_breakdown': [
                results['technical']['scores'].get('feasibility', 0),
                results['technical']['scores'].get('innovation', 0),
                results['technical']['scores'].get('scalability', 0),
                results['technical']['scores'].get('security', 0),
                results['technical']['scores'].get('compliance', 0)
            ]
        }
        for p in proposals
    }

def calculate_overall_score(results, filename):
    """Calculate weighted overall score from individual agent scores"""
    # Define scoring weights (adjust these based on your requirements)
    WEIGHTS = {
        'financial': 0.4,   # 40% weight
        'technical': 0.35,  # 35% weight
        'legal': 0.25       # 25% weight
    }
    
    # Get scores with fallback values
    financial_score = results['financial']['scores'].get('overall', 0) or 0
    technical_score = results['technical']['scores'].get('overall', 0) or 0
    legal_score = results['legal']['scores'].get('overall', 0) or 0
    
    # Calculate weighted average
    weighted_sum = (
        financial_score * WEIGHTS['financial'] +
        technical_score * WEIGHTS['technical'] +
        legal_score * WEIGHTS['legal']
    )
    
    # Ensure score is between 0-100
    return max(0, min(100, round(weighted_sum, 2)))

def generate_single_report(results):
    prompt = f"""Generate a comprehensive executive summary report for this single proposal analysis:
    
    Financial Analysis: {results['financial']['analysis']}
    Legal Analysis: {results['legal']['analysis']}
    Technical Analysis: {results['technical']['analysis']}
    
    Include key strengths, weaknesses, and recommendations."""
    
    return client.chat.completions.create(
        model='Meta-Llama-3.1-8B-Instruct',
        messages=[
            {"role": "system", "content": "You are an executive summary writer"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=2000
    ).choices[0].message.content

def generate_comparison_report(results):
    prompt = f"""Generate a comparative analysis report based on these insights:
    
    Financial Comparisons: {results['financial']['analysis']}
    Legal Comparisons: {results['legal']['analysis']}
    Technical Comparisons: {results['technical']['analysis']}
    
    Highlight key differences and provide final recommendations."""
    
    return client.chat.completions.create(
        model='Meta-Llama-3.1-8B-Instruct',
        messages=[
            {"role": "system", "content": "You are a comparative analysis expert"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=3000
    ).choices[0].message.content