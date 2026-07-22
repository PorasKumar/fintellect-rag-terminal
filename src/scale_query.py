class ScaleQuery:
    def __init__(self, query, dense_model, bm25, alpha: int):
        self.query = query
        self.dense_model = dense_model
        self.bm25 = bm25
        self.alpha = alpha
        
        
    def scale_query_func(self):
        #converting the query to dense and sparse values first
        raw_dense_query = self.dense_model.encode(self.query).tolist()
        raw_sparse_query = self.bm25.encode_queries(self.query)

        #clean raw sparse dictionary with proper values
        clean_raw_sparse = {
            "indices": [int(i) for i in raw_sparse_query["indices"]],
            "values": [float(v) for v in raw_sparse_query["values"]]
        }

        #scaling queries
        if((self.alpha<0) or (self.alpha>1)):
            raise ValueError("Alpha should be between 0 and 1")
        
        scaled_dense = [(v*self.alpha) for v in raw_dense_query]
        scaled_sparse = {
                "indices": clean_raw_sparse["indices"],
                "values": [(v*(1-self.alpha))  for v in clean_raw_sparse["values"]]
            }

        return scaled_dense, scaled_sparse