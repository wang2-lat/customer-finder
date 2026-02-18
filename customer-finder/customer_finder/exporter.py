import pandas as pd
from pathlib import Path
from typing import List, Dict


class CSVExporter:
    """CSV导出器"""
    
    def export(self, leads: List[Dict], output_path: Path):
        """导出线索到CSV"""
        df = pd.DataFrame(leads)
        
        # 按分数排序
        if 'score' in df.columns:
            df = df.sort_values('score', ascending=False)
        
        # 重新排列列顺序
        columns = ['platform', 'author', 'email', 'title', 'url', 'source', 'score']
        df = df[[col for col in columns if col in df.columns]]
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')