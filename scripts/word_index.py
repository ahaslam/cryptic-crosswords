"""Position-letter index for fast crossword candidate lookup."""
from collections import defaultdict

class WordIndex:
    def __init__(self, words_by_length):
        self.words = {n: tuple(sorted(words)) for n, words in words_by_length.items()}
        self.lookup = {}
        for length, words in self.words.items():
            for pos in range(length):
                for word in words:
                    self.lookup.setdefault((length, pos, word[pos]), set()).add(word)

    def candidates(self, pattern, used):
        """Return available words matching a pattern of letters and dots."""
        length = len(pattern)
        constraints = [
            self.lookup.get((length, pos, char), set())
            for pos, char in enumerate(pattern) if char != '.'
        ]
        if constraints:
            if any(not group for group in constraints):
                return []
            constraints.sort(key=len)
            pool = constraints[0].intersection(*constraints[1:])
        else:
            pool = self.words.get(length, ())
        return [word for word in pool if word not in used]
