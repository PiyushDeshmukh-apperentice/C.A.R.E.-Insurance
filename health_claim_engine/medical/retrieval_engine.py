import pandas as pd
from fuzzywuzzy import process

class RetrievalEngine:
    def __init__(self, db):
        self.db = db

    def get_candidates(self, queries, max_candidates=5):
        candidates = []
        for q in queries:
            # Broad Filter: Simple keyword match in Long Description
            keywords = q.lower().split()
            filtered_db = self.db[self.db['Long Description'].str.lower().apply(lambda desc: any(kw in desc for kw in keywords))]

            if filtered_db.empty:
                continue

            # Fuzzy Match on filtered
            matches = process.extract(q, filtered_db['Long Description'].tolist(), limit=3)
            for match_text, score in matches:
                row = filtered_db[filtered_db['Long Description'] == match_text].iloc[0]
                candidates.append({
                    "code": row['ICD-10 Code'],
                    "desc": row['Long Description'],
                    "score": score
                })

        # Deduplicate by code and sort by score
        seen = set()
        unique_candidates = []
        for c in sorted(candidates, key=lambda x: x['score'], reverse=True):
            if c['code'] not in seen:
                unique_candidates.append(c)
                seen.add(c['code'])
                if len(unique_candidates) >= max_candidates:
                    break

        return unique_candidates