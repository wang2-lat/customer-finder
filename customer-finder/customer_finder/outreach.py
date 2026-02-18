from typing import Dict

class OutreachGenerator:
    def __init__(self, product_name: str):
        self.product_name = product_name
    
    def generate(self, customer: Dict) -> str:
        """生成个性化触达话术"""
        pain_points = ", ".join(customer.get("pain_points", []))
        
        template = f"""Hi {customer['author']},

我在 {customer['platform']} 上看到你关于 "{customer['title'][:50]}" 的讨论。

注意到你提到了 {pain_points} 这些痛点。我们的产品 {self.product_name} 专门解决这类问题。

特点：
- [根据客户痛点定制特点 1]
- [根据客户痛点定制特点 2]
- [根据客户痛点定制特点 3]

如果感兴趣，我可以提供免费试用或详细演示。

原讨论链接：{customer['url']}

期待你的回复！
"""
        return template