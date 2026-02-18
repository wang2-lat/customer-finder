from openai import OpenAI
from typing import Dict, List
import json

class CustomerAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def analyze_customer_persona(self, product_description: str) -> Dict:
        """分析客户画像和关键词"""
        prompt = f"""
你是一个客户开发专家。基于以下产品描述，分析潜在付费客户：

产品: {product_description}

请以 JSON 格式输出：
{{
  "target_customers": "目标客户群体（具体职位/角色）",
  "pain_points": "核心痛点（一句话）",
  "keywords": ["关键词1", "关键词2", "关键词3", "关键词4", "关键词5"],
  "platforms": ["最相关的平台1", "平台2", "平台3"]
}}

关键词要包含：问题关键词、解决方案关键词、竞品关键词。
"""
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    
    def generate_outreach_templates(self, persona: Dict, channels: List[Dict]) -> List[Dict]:
        """生成联系方式模板"""
        templates = []
        
        for channel in channels[:3]:
            prompt = f"""
生成一个简短的联系模板（3-4句话），用于在 {channel['platform']} 的 {channel['community']} 社区联系潜在客户。

客户画像: {persona['target_customers']}
痛点: {persona['pain_points']}

要求：
- 不要推销，先提供价值
- 提到他们讨论的具体问题
- 自然、非正式的语气
- 包含一个具体问题或建议
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=200
            )
            
            templates.append({
                "channel": f"{channel['platform']} - {channel['community']}",
                "template": response.choices[0].message.content.strip()
            })
        
        return templates