from pymongo import MongoClient


class FoodRecallAPI:
    """
    API for querying FDA Food Recall data without needing to know MongoDB
    List structures are set for data involving sorting or filtering.
    Index structures are set for data involving unique keys.
    """
    
    def __init__(self, host='localhost', port=27017):
        """Initialize connection to MongoDB"""
        self.client = MongoClient(f'mongodb://{host}:{port}/')
        self.db = self.client['food_safety']
        self.collection = self.db['recalls']
    

    def get_recalls_by_state(self, limit=15):
        """
        Get recall counts grouped by state
        Param limit : int Number of top states to return (default: 15)
            
        Returns: list of dictionary of recalls by state
        """
        pipeline = [
            { "$group": { "_id": "$state", "count": { "$sum": 1 } } },
            { "$sort": { "count": -1 } },
            { "$limit": limit }
        ]
        results = list(self.collection.aggregate(pipeline))
        
        # Convert to more readable format
        return [{'state': r['_id'], 'count': r['count']} for r in results]
    

    def get_recalls_by_classification(self):
        """
        Get recall counts by severity classification (Class I, II, III)
        
        Returns: dictionary of classified recalls
        """
        pipeline = [
            { "$group": { "_id": "$classification", "count": { "$sum": 1 } } },
            { "$sort": { "count": -1 } }
        ]
        results = list(self.collection.aggregate(pipeline))
        
        return {r['_id']: r['count'] for r in results}
    

    def get_recalls_by_year(self):
        """
        Get recall trends over time (by year)
        
        Returns: list of dictionary of recall trends over time
        """
        pipeline = [
            { "$project": { 
                "year": { "$substr": ["$recall_initiation_date", 0, 4] }
            }},
            { "$group": { "_id": "$year", "count": { "$sum": 1 } } },
            { "$sort": { "_id": 1 } }
        ]
        results = list(self.collection.aggregate(pipeline))
        
        return [{'year': r['_id'], 'count': r['count']} for r in results]
    

    def search_recalls_by_keyword(self, keyword, limit=20):
        """
        Search recalls by keyword in reason_for_recall field
        Param keyword: Keyword to search for (case-insensitive)
        Param limit: Maximum number of results to return
            
        Returns: list of dict: Matching recall documents
        """
        results = self.collection.find({
            "reason_for_recall": { "$regex": keyword, "$options": "i" }
        }).limit(limit)
        
        return list(results)
    
    def get_top_firms_with_recalls(self, limit=10):
        """
        Get firms with the most recalls
        Param limit: Number of top firms to return
            
        Returns: list of dict of firms with most recalls
        """
        pipeline = [
            { "$group": { "_id": "$recalling_firm", "count": { "$sum": 1 } } },
            { "$sort": { "count": -1 } },
            { "$limit": limit }
        ]
        results = list(self.collection.aggregate(pipeline))
        
        return [{'firm': r['_id'], 'count': r['count']} for r in results]
    
    def get_recalls_by_firm_and_classification(self, firm):
        """
        Get classification breakdown for a specific firm
        Param firm: Firm name (exact match)
        
        Returns: dict of classification counts for that firm
        """
        pipeline = [
            { "$match": { "recalling_firm": firm } },
            { "$group": { "_id": "$classification", "count": { "$sum": 1 } } }
        ]
        results = list(self.collection.aggregate(pipeline))
        
        return {r['_id']: r['count'] for r in results}
