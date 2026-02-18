from typing import List, Dict
import re

class CustomerAnalyzer:
    # 痛点关键词
    PAIN_KEYWORDS = [
        "looking for", "need", "want", "searching", "recommend",
        "alternative", "better than", "frustrated", "problem",
        "issue", "difficult", "expensive", "complicated", "slow",
        "help", "advice", "suggestion", "anyone know"
    ]
    
    def analyze(self, results: List[Dict], min_score: int = 3) -> List[Dict]:
        """分析并过滤潜在客户"""
        customers = []
        
        for result in results:
            # 过滤低分内容
            if result.get("score", 0) < min_score:
                continue
            
            # 提取痛点
            pain_points = self._extract_pain_points(
                result.get("title", "") + " " + result.get("content", "")
            )
            
            # 至少要有一个痛点关键词
            if not pain_points:
                continue
            
            result["pain_points"] = pain_points
            customers.append(result)
        
        # 按评分排序
        customers.sort(key=lambda x: x.get("score", 0), reverse=True)
        return customers
    
    def _extract_pain_points(self, text: str) -> List[str]:
        """提取痛点关键词"""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.PAIN_KEYWORDS:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords