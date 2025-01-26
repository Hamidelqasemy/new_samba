class TechnicalAgent:
    def __init__(self, client):
        self.client = client
        self.system_prompt = """You are a chief technology officer with 15+ years experience. Evaluate:
        - Technical implementation plan
        - Technology stack appropriateness
        - Timeline feasibility
        - Scalability considerations
        - Integration capabilities
        - Technical risk factors
        Assess the technical merit and implementation risks."""
    
    def analyze(self, proposals):
        prompt = "Analyze technical aspects of these proposals:\n"
        for idx, p in enumerate(proposals):
            prompt += f"\nProposal {idx+1} ({p['filename']}):\n{p['content'][:3000]}\n"
        
        prompt += "\nProvide detailed technical comparison with emphasis on feasibility."
        
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