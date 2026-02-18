from typing import List, Dict
import re

class CustomerAnalyzer:
    # 痛点关键词
    PAIN_KEYWORDS = [
        "looking for", "need", "want", "searching", "recommend",
        "alternative", "better than", "frustrated", "problem",
        "issue", "difficult", "expensive", "complicated", "slow"
    ]
    
    def analyze(self, results: List[Dict], keywords: str, min_score: int = 3) -> List[Dict]:
        """分析并过滤潜在客户"""
        customers = []
        
        for result in results:
            # 过滤低分内容
            if result["score"] < min_score:
                continue
            
            # 识别痛点
            text = f"{result['title']} {result['content']}".lower()
            pain_points = [kw for kw in self.PAIN_KEYWORDS if kw in text]
            
            if not pain_points:
                continue
            
            result["pain_points"] = pain_points
            result["relevance_score"] = self._calculate_relevance(text, keywords)
            customers.append(result)
        
        # 按相关性排序
        customers.sort(key=lambda x: x["relevance_score"], reverse=True)
        return customers
    
    def _calculate_relevance(self, text: str, keywords: str) -> float:
        """计算相关性分数"""
        keyword_list = keywords.lower().split()
        matches = sum(1 for kw in keyword_list if kw in text)
        return matches / len(keyword_list) if keyword_list else 0