from collections import defaultdict

class LeakageTracker:

    def __init__(self):
        self.search_history = []
        self.access_patterns = []

    def record_search(self, trapdoor, results):
        """
        Record search pattern and access pattern
        """

        self.search_history.append(trapdoor)
        self.access_patterns.append(tuple(results))

    def search_pattern_leakage(self):
        """
        Detect repeated queries
        """
        return len(self.search_history) - len(set(self.search_history))

    def access_pattern_leakage(self):
        """
        Count repeated access patterns
        """
        return len(self.access_patterns) - len(set(self.access_patterns))