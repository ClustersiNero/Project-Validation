from dataclasses import dataclass
from typing import Any, Sequence, List
import random

# A reproducible RNG bundle.
# Design goals:
# - Single place to control determinism (seed)
# - Allow injection into core logic (preferred)
# - Provide utility methods to reduce random.* scattered usage
@dataclass
class RNG:
    seed: int
    py: random.Random

    def random(self) -> float:
        return self.py.random()
    
    def randint(self, a: int, b: int) -> int:
        return self.py.randint(a,b)
    
    def randrange(self, *args: Any) -> int:
        return self.py.randrange(*args)
    
    def choice(self, seq):
        return self.py.choice(seq)
    
    def choices(self, population, weights=None, k=1):
        return self.py.choices(population, weights=weights, k=k)
    
    def shuffle(self, seq: List[Any]) -> None:
        self.py.shuffle(seq)

    def uniform(self, a: float, b: float) -> float:
        return self.py.uniform(a,b)
    

    # Equivalent distribution to random.choices(items, weights=weights, k=1)[0],
    # but avoids list allocation and keeps all randomness routed through self.random().
    def weighted_index(self, weights: Sequence[float]) -> int:
        if not weights:
            raise ValueError("weights must not be empty")
        
        total = 0.0
        for w in weights:
            if w < 0 :
                raise ValueError("weight must be non-negative")
            total += float(w)

        if total <= 0:
            raise ValueError("sum(weigths) must be > 0")
        
        r = self.random() * total
        acc = 0.0
        for i, w in enumerate(weights):
            acc += float(w)
            if r < acc:
                return i
            
        return len(weights) - 1
    
    def weighted_choice(self, items: Sequence[Any], weights: Sequence[float]) -> Any:
        if len(items) != len(weights):
            raise ValueError("items and weights must have same Length")
        return items[self.weighted_index(weights)]