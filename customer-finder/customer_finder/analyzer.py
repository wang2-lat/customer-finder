import re
from typing import Dict, List


class CustomerProfileAnalyzer:
    """客户画像分析器"""
    
    def generate_profile(self, product_description: str) -> Dict[str, any]:
        """根据产品描述生成客户画像和搜索关键词"""
        
        # 简化版：基于关键词映射生成画像
        keywords = self._extract_keywords(product_description)
        persona = self._generate_persona(product_description)
        
        return {
            "persona": persona,
            "keywords": keywords,
            "pain_points": self._extract_pain_points(product_description)
        }
    
    def _extract_keywords(self, description: str) -> List[str]:
        """提取搜索关键词"""
        base_keywords = []
        
        # 技术关键词映射
        tech_map = {
            "AI": ["artificial intelligence", "machine learning", "AI tool"],
            "代码": ["code review", "developer tool", "programming"],
            "审查": ["code quality", "static analysis"],
            "SaaS": ["software as a service", "cloud software"],
            "API": ["API integration", "REST API"],
            "数据": ["data analysis", "analytics", "business intelligence"],
        }
        
        for key, values in tech_map.items():
            if key in description:
                base_keywords.extend(values)
        
        # 添加通用获客关键词
        base_keywords.extend([
            "looking for tool",
            "need solution",
            "recommend software",
            "alternative to"
        ])
        
        return list(set(base_keywords))[:10]  # 限制10个关键词
    
    def _generate_persona(self, description: str) -> str:
        """生成客户画像描述"""
        if "AI" in description or "代码" in description:
            return "技术团队负责人、CTO、资深开发者"
        elif "数据" in description:
            return "数据分析师、产品经理、业务负责人"
        else:
            return "创业者、产品经理、技术决策者"
    
    def _extract_pain_points(self, description: str) -> List[str]:
        """提取痛点（用于后续邮件个性化）"""
        return [
            "提升效率",
            "降低成本",
            "改善质量"
        ]