import pandas as pd
from rapidfuzz import process, fuzz

class RetrievalEngine:
    def __init__(self, icd_db_path_or_df):
        """
        Initialize with either a path to the CSV/Excel or an existing DataFrame.
        """
        if isinstance(icd_db_path_or_df, pd.DataFrame):
            self.df = icd_db_path_or_df
        else:
            # Handle both CSV and Excel just in case
            if str(icd_db_path_or_df).endswith('.csv'):
                self.df = pd.read_csv(icd_db_path_or_df)
            else:
                self.df = pd.read_excel(icd_db_path_or_df)
        
        # Ensure we have the standard column names expected
        # Assuming CSV has 'Code' and 'Description' columns based on your file name
        # We normalize column names to be safe
        self.df.columns = [c.lower().strip() for c in self.df.columns]
        
        # Identify code and description columns dynamically
        self.code_col = next((c for c in self.df.columns if 'code' in c), self.df.columns[0])
        self.desc_col = next((c for c in self.df.columns if 'desc' in c or 'name' in c), self.df.columns[1])
        
        # Create a combined lookup text for better fuzzy matching
        self.df['lookup_text'] = self.df[self.code_col].astype(str) + " " + self.df[self.desc_col].astype(str)

    def get_candidates(self, queries, top_k=5):
        """
        Retrieve top K ICD candidates based on search queries.
        """
        candidates = []
        seen_codes = set()

        # Flatten queries if it's a list of lists (defensive coding)
        if isinstance(queries, list) and len(queries) > 0 and isinstance(queries[0], list):
            queries = [item for sublist in queries for item in sublist]

        for query in queries:
            if not query:
                continue
                
            # Use weighted ratio for better medical term matching
            matches = process.extract(
                query, 
                self.df['lookup_text'], 
                scorer=fuzz.WRatio, 
                limit=top_k
            )

            for match in matches:
                # rapidfuzz returns (match_text, score, index)
                text, score, idx = match
                row = self.df.iloc[idx]
                code = row[self.code_col]
                desc = row[self.desc_col]

                if code not in seen_codes:
                    candidates.append({
                        "code": code,
                        "desc": desc,
                        "score": score,
                        "priority": 0.5  # Default priority
                    })
                    seen_codes.add(code)

        # Sort by score descending
        return sorted(candidates, key=lambda x: x['score'], reverse=True)[:top_k*2]