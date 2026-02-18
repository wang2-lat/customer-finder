from typing import List, Dict

class OutreachGenerator:
    def __init__(self, product_name: str):
        self.product_name = product_name
    
    def generate(self, customers: List[Dict]) -> str:
        """生成触达话术"""
        messages = []
        
        for i, customer in enumerate(customers, 1):
            template = self._create_template(customer)
            messages.append(f"--- 客户 #{i} ---")
            messages.append(f"平台: {customer['platform']}")
            messages.append(f"作者: {customer['author']}")
            messages.append(f"链接: {customer['url']}")
            messages.append(f"\n推荐话术:\n{template}\n")
            messages.append("-" * 80 + "\n")
        
        return "\n".join(messages)
    
    def _create_template(self, customer: Dict) -> str:
        """创建个性化模板"""
        pain_points = ", ".join(customer.get("pain_points", []))
        
        template = f"""Hi {customer['author']},

我看到你在 {customer['platform']} 上提到了关于 "{customer['title'][:50]}" 的讨论。

我注意到你提到了 {pain_points} 这些痛点。我们的产品 {self.product_name} 专门解决这类问题。

[在这里简要说明你的产品如何解决他们的具体痛点]

如果你感兴趣，我很乐意分享更多细节或提供免费试用。

最好的祝愿，
[你的名字]"""
        
        return template