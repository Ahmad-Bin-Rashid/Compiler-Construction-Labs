"""
=============================================================
 Symbol Table Manager  —  Lab 13
=============================================================

 Implements:
   Task 1 — Hash table with separate chaining (insert /
             lookup / delete / print) for a single scope.
   Task 2 — Scope stack (beginScope / endScope /
             lookup across enclosing scopes).
   Task 4 — Pretty-print in tabular form.
=============================================================
"""

# ──────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────
TABLE_SIZE = 211          # prime → fewer collisions

# Numeric codes for "kind"  (kept as human-readable strings below)
KIND_VAR   = "variable"
KIND_CONST = "constant"
KIND_FUNC  = "function"
KIND_PARAM = "parameter"
KIND_ARRAY = "array"

# Numeric codes for "type"
TYPE_INT   = "integer"
TYPE_REAL  = "real"
TYPE_BOOL  = "boolean"
TYPE_CHAR  = "char"
TYPE_VOID  = "void"


# ──────────────────────────────────────────────────────────────
# Task 1a — djb2 hash function
# ──────────────────────────────────────────────────────────────
def _hash(name: str) -> int:
    """
    djb2 hash function for strings.
    h = 5381 ; for each char c: h = h * 33 + ord(c)
    Returns an index in [0, TABLE_SIZE).
    """
    h = 5381
    for ch in name:
        h = ((h << 5) + h) + ord(ch)   # h * 33 + ord(ch)
    return h % TABLE_SIZE


# ──────────────────────────────────────────────────────────────
# Task 1b — Symbol-table Entry (singly-linked list node)
# ──────────────────────────────────────────────────────────────
class Entry:
    """
    One record in the symbol table.

    Attributes
    ----------
    name        : identifier lexeme
    kind        : one of KIND_* constants  (variable / function / …)
    type_       : one of TYPE_* constants  (integer / real / …)
    scope_level : depth of the scope where this name was declared
    line        : source line number of the declaration
    next_       : next Entry in the same hash-slot chain (chaining)
    """

    def __init__(self, name: str, kind: str, type_: str,
                 scope_level: int, line: int):
        self.name        = name
        self.kind        = kind
        self.type_       = type_
        self.scope_level = scope_level
        self.line        = line
        self.next_: "Entry | None" = None   # chaining pointer

    def __repr__(self) -> str:
        return (f"Entry({self.name!r}, {self.kind}, {self.type_}, "
                f"scope={self.scope_level}, line={self.line})")


# ──────────────────────────────────────────────────────────────
# Task 1c — Single-scope Hash Table
# ──────────────────────────────────────────────────────────────
class HashTable:
    """
    One hash table representing a single lexical scope.

    Uses an array of TABLE_SIZE slots; each slot is the head of
    a singly-linked list of Entry objects (separate chaining).

    Attributes
    ----------
    scope_level : depth of this scope (0 = global)
    parent      : enclosing HashTable, or None for the global scope
    slots       : array of TABLE_SIZE linked-list heads
    _count      : number of entries currently stored
    """

    def __init__(self, scope_level: int, parent: "HashTable | None" = None):
        self.scope_level = scope_level
        self.parent: "HashTable | None" = parent
        self.slots: list["Entry | None"] = [None] * TABLE_SIZE
        self._count = 0

    # ── Task 1c-i : lookup_current ────────────────────────────
    def lookup_current(self, name: str) -> "Entry | None":
        """
        Search ONLY this scope's hash table.
        Returns the Entry if found, None otherwise.
        Used internally by insert() to detect duplicates.
        """
        idx = _hash(name)
        e = self.slots[idx]
        while e is not None:
            if e.name == name:
                return e
            e = e.next_
        return None

    # ── Task 1c-ii : insert ───────────────────────────────────
    def insert(self, name: str, kind: str, type_: str, line: int
               ) -> "Entry | None":
        """
        Insert a new symbol into this scope.

        Returns the new Entry on success.
        Returns None (duplicate) if *name* is already declared in
        the current scope.  The caller is responsible for reporting
        the error.
        """
        if self.lookup_current(name) is not None:
            return None                         # duplicate declaration

        idx = _hash(name)
        e = Entry(name, kind, type_, self.scope_level, line)
        e.next_       = self.slots[idx]         # prepend to chain
        self.slots[idx] = e
        self._count  += 1

        print(f"  [Scope {self.scope_level}] insert {name:<12} : "
              f"{kind}, {type_}, line {line}")
        return e

    # ── Task 1c-iii : delete ─────────────────────────────────
    def delete(self, name: str) -> bool:
        """
        Remove the entry for *name* from this scope's table.
        Returns True if the entry was found and removed, False otherwise.
        """
        idx = _hash(name)
        prev = None
        e = self.slots[idx]
        while e is not None:
            if e.name == name:
                if prev is None:
                    self.slots[idx] = e.next_
                else:
                    prev.next_ = e.next_
                self._count -= 1
                return True
            prev = e
            e = e.next_
        return False

    # ── Task 1c-iv : print (single scope) ────────────────────
    def print_table(self) -> None:
        """Print every entry in this scope (for debugging)."""
        entries = self._all_entries()
        if not entries:
            print(f"    (scope {self.scope_level} is empty)")
            return
        for e in entries:
            print(f"    {e.name:<14} : {e.kind}, {e.type_}, line {e.line}")

    def _all_entries(self) -> list[Entry]:
        """Return all Entry objects in this table (insertion order not preserved)."""
        result = []
        for head in self.slots:
            e = head
            while e is not None:
                result.append(e)
                e = e.next_
        # Sort by line number for deterministic output
        result.sort(key=lambda x: x.line)
        return result

    def __len__(self) -> int:
        return self._count


# ──────────────────────────────────────────────────────────────
# Task 2 — Scope Manager (stack of HashTables)
# ──────────────────────────────────────────────────────────────
class SymbolTableManager:
    """
    Manages a *stack* of HashTable objects — one per lexical scope.

    The stack is implemented as a Python list; the *top* (current scope)
    is at index -1 (the last element).

    Design A from the lab spec: one hash table per scope.
    """

    def __init__(self):
        self._stack: list[HashTable] = []
        self._scope_counter = 0        # monotonically-increasing scope id
        # Open the global scope immediately
        self.begin_scope()

    # ── Properties ───────────────────────────────────────────
    @property
    def current(self) -> HashTable:
        """Return the top (innermost) scope table."""
        return self._stack[-1]

    @property
    def depth(self) -> int:
        return len(self._stack) - 1

    # ── Task 2a : beginScope ─────────────────────────────────
    def begin_scope(self) -> None:
        """
        Push a new empty hash table onto the scope stack.
        The new scope's scope_level equals the current stack depth.
        """
        level  = len(self._stack)
        parent = self._stack[-1] if self._stack else None
        table  = HashTable(scope_level=level, parent=parent)
        self._stack.append(table)
        print(f"[Scope {level}] Enter")

    # ── Task 2b : endScope ───────────────────────────────────
    def end_scope(self) -> None:
        """
        Pop the top scope, pretty-print it, then discard it.
        Raises RuntimeError if there are no scopes to pop.
        """
        if not self._stack:
            raise RuntimeError("end_scope() called with empty scope stack")

        top = self._stack.pop()
        level = top.scope_level
        print(f"[Scope {level}] Exit, dump:")
        # Task 4 — pretty-print this scope before discarding
        self.pretty_print_scope(top)

    # ── Task 2c : insert (delegates to current scope) ────────
    def insert(self, name: str, kind: str, type_: str, line: int
               ) -> "Entry | None":
        """
        Insert *name* in the current (innermost) scope.
        Returns the Entry on success, or None on duplicate.
        """
        return self.current.insert(name, kind, type_, line)

    # ── Task 2d : lookup (searches outward) ──────────────────
    def lookup(self, name: str) -> "Entry | None":
        """
        Search for *name* from the current scope outward.
        Returns the innermost matching Entry, or None if not found.
        """
        for table in reversed(self._stack):
            e = table.lookup_current(name)
            if e is not None:
                print(f"  [Scope {self.current.scope_level}] "
                      f"lookup {name:<12} → found at scope {e.scope_level}")
                return e
        print(f"  [Scope {self.current.scope_level}] "
              f"lookup {name:<12} → NOT FOUND")
        return None

    # ── Task 2e : lookup_current (current scope only) ────────
    def lookup_current(self, name: str) -> "Entry | None":
        """Search only the current scope (used for duplicate detection)."""
        return self.current.lookup_current(name)

    # ── Task 2f : delete (current scope only) ────────────────
    def delete(self, name: str) -> bool:
        """Delete *name* from the current scope only."""
        result = self.current.delete(name)
        if result:
            print(f"  [Scope {self.current.scope_level}] delete {name}")
        return result

    # ── Task 4 : pretty_print ────────────────────────────────
    def pretty_print_scope(self, table: HashTable) -> None:
        """
        Task 4 — Print the contents of one scope as a neat ASCII table.

        Example output:
        +----+-----------+----------+---------+-------+------+
        | ID | Name      | Kind     | Type    | Scope | Line |
        +----+-----------+----------+---------+-------+------+
        |  1 | x         | variable | integer |   1   |   2  |
        +----+-----------+----------+---------+-------+------+
        """
        entries = table._all_entries()
        if not entries:
            print(f"    (scope {table.scope_level} is empty)")
            return

        # Column widths (dynamic based on content)
        col_id   = max(2, len(str(len(entries))))
        col_name = max(4, max(len(e.name)  for e in entries))
        col_kind = max(4, max(len(e.kind)  for e in entries))
        col_type = max(4, max(len(e.type_) for e in entries))
        col_scp  = max(5, len(str(table.scope_level)))
        col_line = max(4, max(len(str(e.line)) for e in entries))

        def sep() -> str:
            return (f"+{'-'*(col_id+2)}+{'-'*(col_name+2)}"
                    f"+{'-'*(col_kind+2)}+{'-'*(col_type+2)}"
                    f"+{'-'*(col_scp+2)}+{'-'*(col_line+2)}+")

        def row(id_: str, name: str, kind: str, type_: str,
                scope: str, line: str) -> str:
            return (f"| {id_:>{col_id}} | {name:<{col_name}} "
                    f"| {kind:<{col_kind}} | {type_:<{col_type}} "
                    f"| {scope:^{col_scp}} | {line:^{col_line}} |")

        print(sep())
        print(row("ID", "Name", "Kind", "Type", "Scope", "Line"))
        print(sep())
        for idx, e in enumerate(entries, start=1):
            print(row(str(idx), e.name, e.kind, e.type_,
                      str(e.scope_level), str(e.line)))
        print(sep())

    def pretty_print_all(self) -> None:
        """Pretty-print every scope currently on the stack (outermost first)."""
        for table in self._stack:
            print(f"\n── Scope {table.scope_level} ──────────────────────────")
            self.pretty_print_scope(table)


# ──────────────────────────────────────────────────────────────
# Standalone test driver (Task 1 + Task 2 unit tests)
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Symbol Table Manager — Standalone Unit Tests")
    print("=" * 60)

    stm = SymbolTableManager()   # opens global scope (scope 0)

    # ── Task 1 tests: 10 inserts, 5 lookups, 3 deletes ────────
    print("\n--- Task 1: inserts ---")
    stm.insert("globalConst", KIND_CONST, TYPE_INT,  1)
    stm.insert("pi",          KIND_CONST, TYPE_REAL, 2)

    # ── Task 2 tests: nested scopes ────────────────────────────
    print("\n--- Task 2: begin inner scope 1 ---")
    stm.begin_scope()
    stm.insert("x",     KIND_VAR, TYPE_INT,  5)
    stm.insert("y",     KIND_VAR, TYPE_INT,  6)
    stm.insert("alpha", KIND_VAR, TYPE_REAL, 7)
    stm.insert("beta",  KIND_VAR, TYPE_REAL, 8)
    stm.insert("count", KIND_VAR, TYPE_INT,  9)

    print("\n--- Task 2: begin inner scope 2 ---")
    stm.begin_scope()
    stm.insert("z",     KIND_VAR,  TYPE_INT, 12)
    stm.insert("temp",  KIND_VAR,  TYPE_REAL,13)
    stm.insert("x",     KIND_VAR,  TYPE_INT, 14)   # shadows outer x
    stm.insert("flag",  KIND_CONST,TYPE_BOOL,15)
    stm.insert("func1", KIND_FUNC, TYPE_VOID,16)

    print("\n--- Lookups (5 total, includes misses) ---")
    stm.lookup("x")           # found at scope 2 (shadow)
    stm.lookup("y")           # found at scope 1 (climb up)
    stm.lookup("globalConst") # found at scope 0
    stm.lookup("missing")     # NOT FOUND
    stm.lookup("pi")          # found at scope 0

    print("\n--- Deletes (3) ---")
    stm.delete("temp")
    stm.delete("flag")
    stm.delete("nonexistent")  # returns False silently

    print("\n--- End scope 2 (pretty-print) ---")
    stm.end_scope()

    print("\n--- End scope 1 (pretty-print) ---")
    stm.end_scope()

    # Duplicate declaration test
    print("\n--- Duplicate declaration test ---")
    result = stm.insert("globalConst", KIND_VAR, TYPE_INT, 99)
    if result is None:
        print("  ✔  Correctly rejected duplicate 'globalConst'")

    print("\n--- End global scope ---")
    stm.end_scope()
