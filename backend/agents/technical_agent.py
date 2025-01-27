import re

class TechnicalAgent:
    def __init__(self, client):
        self.client = client
        self.system_prompt = """You are a CTO analyzing RFP proposals. Provide:
        1. Feasibility score (0-100)
        2. Innovation score (0-100)
        3. Scalability score (0-100)
        4. Security score (0-100)
        5. Compliance score (0-100)
        6. Overall technical score (0-100)
        7. Detailed analysis
        
        Format response as:
        Feasibility: [score]/100
        Innovation: [score]/100
        Scalability: [score]/100
        Security: [score]/100
        Compliance: [score]/100
        Overall Technical Score: [score]/100
        Analysis: [detailed text]"""

    def analyze(self, proposals):
        prompt = "Technical comparison of:\n" + "\n".join(
            f"Proposal {i+1} ({p['filename']}): {p['content'][:3000]}"
            for i, p in enumerate(proposals)
        )
        return self._process_request(prompt)

    def analyze_single(self, proposal):
        prompt = f"""Provide detailed technical analysis for this single proposal:
        {proposal['filename']}
        {proposal['content'][:3000]}
        
        Include:
        1. Technical feasibility
        2. Innovation assessment
        3. Scalability analysis
        4. Security review
        5. Compliance check
        6. Overall technical score (0-100)"""
        return self._process_request(prompt)

    def _process_request(self, prompt):
        response = self.client.chat.completions.create(
            model='Meta-Llama-3.1-8B-Instruct',
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        return self._parse_response(response.choices[0].message.content)

    def _parse_response(self, text):
        return {
            'analysis': text,
            'scores': {
                'feasibility': self._extract_score(text, r'Feasibility: (\d+)'),
                'innovation': self._extract_score(text, r'Innovation: (\d+)'),
                'scalability': self._extract_score(text, r'Scalability: (\d+)'),
                'security': self._extract_score(text, r'Security: (\d+)'),
                'compliance': self._extract_score(text, r'Compliance: (\d+)'),
                'overall': self._extract_score(text, r'Overall Technical Score: (\d+)')
            }
        }

    def _extract_score(self, text, pattern):
        match = re.search(pattern, text)
        try:
            return int(match.group(1)) if match else 0  # Default to 0 instead of None
        except (ValueError, AttributeError):
            return 0  # Fallback for invalid numbers