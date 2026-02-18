from typing import Dict

def generate_outreach_templates(item: Dict, keyword: str) -> str:
    """Generate outreach template based on discussion context."""
    
    platform = item['platform']
    score = item['score']
    
    templates = {
        'high_reddit': f"Hey! I saw your discussion about {keyword}. I've been working on something that might help - [brief 1-sentence description]. Would love to hear your thoughts if you're interested. No pressure!",
        
        'medium_reddit': f"Interesting thread! I'm building a tool related to {keyword}. Still early stage but happy to share if anyone wants to try it out and give feedback.",
        
        'high_hn': f"Great discussion. I recently launched something in this space ({keyword}). Here's what we learned: [1-2 key insights]. Happy to answer questions!",
        
        'medium_hn': f"For anyone interested in {keyword}, I've been exploring this problem and built a small tool. Early days but open to feedback: [link]",
        
        'producthunt': f"Launching on ProductHunt soon! We're solving [specific problem related to {keyword}]. Would appreciate any feedback from the community.",
    }
    
    # Select template based on platform and score
    if platform == 'reddit':
        key = 'high_reddit' if score >= 70 else 'medium_reddit'
    elif platform == 'hackernews':
        key = 'high_hn' if score >= 70 else 'medium_hn'
    else:
        key = 'producthunt'
    
    template = templates.get(key, templates['medium_reddit'])
    
    # Add context-specific tips
    tips = "\n\nTips:\n"
    if platform == 'reddit':
        tips += "- Check subreddit rules before posting\n"
        tips += "- Engage genuinely, don't just drop links\n"
        tips += "- Respond to comments quickly"
    elif platform == 'hackernews':
        tips += "- Focus on technical insights\n"
        tips += "- Be transparent about being the creator\n"
        tips += "- Provide value before asking"
    
    return template + tips