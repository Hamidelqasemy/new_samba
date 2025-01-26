class LegalAgent:
    def __init__(self, client):
        self.client = client
        self.system_prompt = """You are a senior corporate lawyer with expertise in contract law. Analyze:
        - Compliance with relevant regulations
        - Liability clauses
        - Intellectual property ownership
        - Termination conditions
        - Confidentiality agreements
        - Force majeure provisions
        Flag any non-standard or risky contractual terms."""
    
    def analyze(self, proposals):
        prompt = "Evaluate legal aspects of these proposals:\n"
        for idx, p in enumerate(proposals):
            prompt += f"\nProposal {idx+1} ({p['filename']}):\n{p['content'][:3000]}\n"
        
        prompt += "\nProvide detailed legal analysis comparing all documents."
        
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