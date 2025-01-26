from .financial_agent import FinancialAgent
from .legal_agent import LegalAgent
from .technical_agent import TechnicalAgent
import concurrent.futures
import os
import openai

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
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(agent.analyze, proposals): name
            for name, agent in agents.items()
        }
        
        for future in concurrent.futures.as_completed(futures):
            agent_name = futures[future]
            results[agent_name] = future.result()
    
    final_report = generate_final_report(results)
    return {**results, 'final_report': final_report}

def generate_final_report(domain_reports):
    prompt = f"""Synthesize these expert reports into a final recommendation:
    
    Financial Analysis: {domain_reports['financial']}
    Legal Analysis: {domain_reports['legal']}
    Technical Analysis: {domain_reports['technical']}
    
    Provide top 3 proposals ranked with justification."""
    
    response = client.chat.completions.create(
        model='Meta-Llama-3.1-8B-Instruct',
        messages=[
            {"role": "system", "content": "You are a CEO making strategic decisions"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        top_p=0.1,
        max_tokens=3000
    )
    
    return response.choices[0].message.content