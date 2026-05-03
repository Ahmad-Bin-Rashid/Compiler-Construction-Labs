# main.py

#  Main Runner — Executes all four lexer approaches on the same input,
#  prints full token streams, and produces a side-by-side comparison
#  of correctness, token counts, and execution time.


import time
import sys
import os

from tokens import Token, TokenType, print_token_stream
from approach1_state_based   import StateBased
from approach2_stateless     import Stateless
from approach3_table_driven  import TableDriven
from approach4_compressed_table  import CompressedLexer


def run_approach(name: str, lexer_cls, source: str, **kwargs):
    """Instantiate lexer, tokenize, time the run, return results."""
    lexer = lexer_cls(source, **kwargs)
    t0    = time.perf_counter()
    toks  = lexer.tokenize()
    t1    = time.perf_counter()
    return toks, (t1 - t0) * 1_000, lexer   # tokens, ms, lexer instance


def compare(results: list[tuple[str, list[Token], float]]):
    """Print a comparison table of all approaches."""
    W = 78
    print('\n' + '═' * W)
    print('  COMPARISON SUMMARY')
    print('═' * W)

    # Header
    print(f"  {'Approach':<38} {'Tokens':>7} {'Errors':>7} {'Time(ms)':>10}")
    print('─' * W)

    for name, toks, ms in results:
        n_tok = len([t for t in toks if t.type != TokenType.EOF])
        n_err = len([t for t in toks if t.type == TokenType.ERROR])
        print(f"  {name:<38} {n_tok:>7} {n_err:>7} {ms:>10.4f}")

    print('─' * W)

    # Verify all approaches produce identical token sequences
    streams = []
    for name, toks, _ in results:
        filtered = [(t.type, t.lexeme) for t in toks
                    if t.type not in (TokenType.EOF,)]
        streams.append((name, filtered))

    ref_name, ref = streams[0]
    all_match = True
    for name, stream in streams[1:]:
        if stream != ref:
            print(f'\n  ⚠  MISMATCH between {ref_name!r} and {name!r}')
            all_match = False
            # Show first difference
            for i, (a, b) in enumerate(zip(ref, stream)):
                if a != b:
                    print(f'     Token #{i}: {ref_name}={a}  {name}={b}')
                    break

    if all_match:
        print(f'\n  ✓  All {len(results)} approaches produce identical token streams.')

    print('═' * W + '\n')


def print_compression_stats(lexer: CompressedLexer):
    stats = lexer.compressed_stats()
    W = 78
    print('═' * W)
    print('  Compressed Table Statistics')
    print('═' * W)
    print(f"  {'States':<35} {stats['states']:>10}")
    print(f"  {'Character classes':<35} {stats['char_classes']:>10}")
    print(f"  {'Dense table cells':<35} {stats['dense_cells']:>10}")
    print(f"  {'Cells after compression':<35} {stats['compressed_cells']:>10}")
    print(f"  {'Memory reduction':<35} {stats['reduction_%']:>9}%")
    print('═' * W + '\n')


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'program.pascal'

    if not os.path.exists(path):
        print(f'Error: file not found: {path}')
        sys.exit(1)

    source = open(path).read()
    print(f'\n  Source file : {path}  ({len(source)} chars, '
          f'{source.count(chr(10))+1} lines)\n')

    approaches = [
        ('Approach 1 — State-Based (Direct Coded)', StateBased),
        ('Approach 2 — Stateless (Functional Dispatch)', Stateless),
        ('Approach 3 — Transition Table Driven', TableDriven),
        ('Approach 4 — Compressed Table Driven', CompressedLexer),
    ]

    results = []
    last_lexer = None

    for name, cls in approaches:
        toks, ms, lexer = run_approach(name, cls, source)
        print_token_stream(toks, name)
        results.append((name, toks, ms))
        last_lexer = (cls, lexer)

    compare(results)

    # Compression stats only for the bonus lexer
    for name, cls in approaches:
        if cls is CompressedLexer:
            _, lexer = last_lexer
            print_compression_stats(lexer)
            break


if __name__ == '__main__':
    main()
