import re

class FinancialAgent:
    def __init__(self, client):
        self.client = client
        self.system_prompt = """You are a CFO analyzing RFP proposals. Provide:
        1. Cost effectiveness score (0-100)
        2. ROI potential score (0-100)
        3. Financial risk score (0-100)
        4. Overall financial score (0-100)
        5. Detailed analysis
        
        Format response as:
        Cost Effectiveness: [score]/100
        ROI Potential: [score]/100
        Financial Risk: [score]/100
        Overall Financial Score: [score]/100
        Analysis: [detailed text]"""

    def analyze(self, proposals):
        prompt = "Financial comparison of:\n" + "\n".join(
            f"Proposal {i+1} ({p['filename']}): {p['content'][:3000]}"
            for i, p in enumerate(proposals)
        )
        return self._process_request(prompt)

    def analyze_single(self, proposal):
        prompt = f"""Provide detailed financial analysis for this single proposal:
        {proposal['filename']}
        {proposal['content'][:3000]}
        
        Include:
        1. Cost breakdown
        2. ROI projections
        3. Risk assessment
        4. Overall financial health score (0-100)"""
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
                'cost_effectiveness': self._extract_score(text, r'Cost Effectiveness: (\d+)'),
                'roi': self._extract_score(text, r'ROI Potential: (\d+)'),
                'risk': self._extract_score(text, r'Financial Risk: (\d+)'),
                'overall': self._extract_score(text, r'Overall Financial Score: (\d+)')
            }
        }

    def _extract_score(self, text, pattern):
        match = re.search(pattern, text)
        try:
            return int(match.group(1)) if match else 0  # Default to 0 instead of None
        except (ValueError, AttributeError):
            return 0  # Fallback for invalid numbers