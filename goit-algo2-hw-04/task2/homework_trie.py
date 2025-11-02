
from dataclasses import dataclass, field
from typing import Dict, Optional, Iterable

@dataclass
class _TrieNode:
    children: Dict[str, "_TrieNode"] = field(default_factory=dict)
    is_end: bool = False

class Trie:
    def __init__(self):
        self.root = _TrieNode()

    def put(self, word: str, value: Optional[int] = None) -> None:
        if not isinstance(word, str):
            raise TypeError("word must be a string")
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, _TrieNode())
        node.is_end = True

    def _walk_prefix(self, prefix: str) -> Optional[_TrieNode]:
        node = self.root
        for ch in prefix:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def _iterate_from(self, node: _TrieNode, prefix: str) -> Iterable[str]:
        if node.is_end:
            yield prefix
        for ch, nxt in node.children.items():
            yield from self._iterate_from(nxt, prefix + ch)

    def __contains__(self, word: str) -> bool:
        node = self._walk_prefix(word)
        return bool(node and node.is_end)

class Homework(Trie):
    def count_words_with_suffix(self, pattern) -> int:
        if not isinstance(pattern, str):
            raise TypeError("pattern must be a string")
        if pattern == "":
            return sum(1 for _ in self._iterate_from(self.root, ""))
        cnt = 0
        for w in self._iterate_from(self.root, ""):
            if w.endswith(pattern):
                cnt += 1
        return cnt

    def has_prefix(self, prefix) -> bool:
        if not isinstance(prefix, str):
            raise TypeError("prefix must be a string")
        if prefix == "":
            return True
        node = self._walk_prefix(prefix)
        return node is not None

if __name__ == "__main__":
    trie = Homework()
    words = ["apple", "application", "banana", "cat"]
    for i, word in enumerate(words):
        trie.put(word, i)

    assert trie.count_words_with_suffix("e") == 1
    assert trie.count_words_with_suffix("ion") == 1
    assert trie.count_words_with_suffix("a") == 1
    assert trie.count_words_with_suffix("at") == 1

    assert trie.has_prefix("app") == True
    assert trie.has_prefix("bat") == False
    assert trie.has_prefix("ban") == True
    assert trie.has_prefix("ca") == True
