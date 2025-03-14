from scimilarity import CellQuery

class CellQuerySingleton:
    _instance = None

    def __new__(cls, model_path=None):
        if cls._instance is None:
            if model_path is None:
                raise ValueError("model_path must be provided for the first instantiation")
            cls._instance = CellQuery(model_path)
            # cls._instance = 1
        return cls._instance