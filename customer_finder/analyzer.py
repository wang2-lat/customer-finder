from typing import List, Dict

def calculate_match_score(item: Dict, keyword: str) -> int:
    """Calculate relevance score (0-100)."""
    score = 0
    keyword_lower = keyword.lower()
    title_lower = item['title'].lower()
    content_lower = item.get('content', '').lower()
    
    # Title match (40 points)
    if keyword_lower in title_lower:
        score += 40
    else:
        # Partial word match
        words = keyword_lower.split()
        matches = sum(1 for w in words if w in title_lower)
        score += int(40 * matches / len(words))
    
    # Content match (30 points)
    if keyword_lower in content_lower:
        score += 30
    else:
        words = keyword_lower.split()
        matches = sum(1 for w in words if w in content_lower)
        score += int(30 * matches / max(len(words), 1))
    
    # Engagement score (30 points)
    engagement = item.get('engagement', 0)
    if engagement > 100:
        score += 30
    elif engagement > 50:
        score += 20
    elif engagement > 10:
        score += 10
    
    return min(score, 100)

def get_match_level(score: int) -> str:
    """Convert score to match level."""
    if score >= 70:
        return "High - Direct match"
    elif score >= 40:
        return "Medium - Related topic"
    else:
        return "Low - Tangential"

def analyze_and_rank(results: List[Dict], keyword: str, limit: int) -> List[Dict]:
    """Analyze and rank results by relevance."""
    
    for item in results:
        item['score'] = calculate_match_score(item, keyword)
        item['match_level'] = get_match_level(item['score'])
    
    # Sort by score and return top N
    ranked = sorted(results, key=lambda x: x['score'], reverse=True)
    return ranked[:limit]