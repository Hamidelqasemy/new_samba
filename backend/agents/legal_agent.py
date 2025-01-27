import re

class LegalAgent:
    def __init__(self, client):
        self.client = client
        self.system_prompt = """You are a corporate lawyer analyzing RFP proposals. Provide:
        1. Compliance score (0-100)
        2. Liability protection score (0-100)
        3. Confidentiality score (0-100)
        4. Overall legal risk score (0-100)
        5. Detailed analysis
        
        Format response as:
        Compliance: [score]/100
        Liability Protection: [score]/100
        Confidentiality: [score]/100
        Overall Legal Risk: [score]/100
        Analysis: [detailed text]"""

    def analyze(self, proposals):
        prompt = "Legal comparison of:\n" + "\n".join(
            f"Proposal {i+1} ({p['filename']}): {p['content'][:3000]}"
            for i, p in enumerate(proposals)
        )
        return self._process_request(prompt)

    def analyze_single(self, proposal):
        prompt = f"""Provide detailed legal analysis for this single proposal:
        {proposal['filename']}
        {proposal['content'][:3000]}
        
        Include:
        1. Compliance assessment
        2. Liability analysis
        3. Confidentiality review
        4. Overall legal risk score (0-100)"""
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
                'compliance': self._extract_score(text, r'Compliance: (\d+)'),
                'liability': self._extract_score(text, r'Liability Protection: (\d+)'),
                'confidentiality': self._extract_score(text, r'Confidentiality: (\d+)'),
                'overall': 100 - (self._extract_score(text, r'Overall Legal Risk: (\d+)') or 0)
            }
        }

    def _extract_score(self, text, pattern):
        match = re.search(pattern, text)
        try:
            return int(match.group(1)) if match else 0  # Default to 0 instead of None
        except (ValueError, AttributeError):
            return 0  # Fallback for invalid numbers