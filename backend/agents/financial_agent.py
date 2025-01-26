class FinancialAgent:
    def __init__(self, client):
        self.client = client
        self.system_prompt = """You are a CFO with 20+ years experience. Analyze:
        - Cost structures
        - Payment terms
        - ROI projections
        - Financial risks
        - Hidden costs
        Provide quantitative comparisons and flag any concerning terms."""
    
    def analyze(self, proposals):
        prompt = "Compare these financial proposals:\n"
        for idx, p in enumerate(proposals):
            prompt += f"\nProposal {idx+1} ({p['filename']}):\n{p['content'][:3000]}\n"
        
        response = self.client.chat.completions.create(
            model='Meta-Llama-3.1-8B-Instruct',
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            top_p=0.1,
            max_tokens=2000
        )
        return response.choices[0].message.content