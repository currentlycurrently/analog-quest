"""
embed.py — Generate vector embeddings for equations that SymPy can't parse.

Uses sentence-transformers with all-MiniLM-L6-v2 (384-dim, fast, good enough
for structural similarity on math strings). The input is a lightly normalized
version of the raw LaTeX — not semantic text, but the structural tokens of
the equation.

Why this works: equations with similar structure have similar LaTeX tokens.
\\frac{dN}{dt} = rN(1 - N/K) and \\frac{dP}{dt} = sP(1 - P/C) will embed
close together because the token sequences are nearly identical.
"""

from __future__ import annotations

import re
from typing import List, Optional


def _normalize_latex_for_embedding(latex: str) -> str:
    """Normalize LaTeX into a consistent token sequence for embedding.

    Strategy: replace specific variable names with generic placeholders,
    but keep structural tokens (frac, partial, sum, int, etc.) intact.
    """
    s = latex

    # Remove formatting commands
    for cmd in [r'\left', r'\right', r'\bigl', r'\bigr', r'\displaystyle',
                r'\textstyle', r'\quad', r'\qquad', r'\,', r'\;', r'\!',
                r'\text', r'\mathrm', r'\mathbf', r'\mathcal', r'\mathbb',
                r'\boldsymbol']:
        s = s.replace(cmd, '')

    # Replace Greek letters with canonical forms (keep the structure)
    # Don't strip them — they carry structural meaning
    # But normalize variants: \varepsilon → \epsilon, etc.
    s = s.replace(r'\varepsilon', r'\epsilon')
    s = s.replace(r'\varphi', r'\phi')
    s = s.replace(r'\varrho', r'\rho')
    s = s.replace(r'\vartheta', r'\theta')

    # Replace specific subscripts/superscripts that are just labels
    # e.g., x_{max} → x_{_}, T_{eff} → T_{_}
    s = re.sub(r'_\{[a-zA-Z]{3,}\}', '_{_}', s)

    # Normalize whitespace
    s = re.sub(r'\s+', ' ', s).strip()

    return s


def embed_equations(latex_list: List[str], batch_size: int = 64) -> List[List[float]]:
    """Generate 384-dim embeddings for a list of LaTeX strings.

    Returns a list of embedding vectors (list of floats).
    Requires: pip install sentence-transformers
    """
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Normalize before embedding
    normalized = [_normalize_latex_for_embedding(eq) for eq in latex_list]

    embeddings = model.encode(normalized, batch_size=batch_size, show_progress_bar=False)

    return [emb.tolist() for emb in embeddings]


def embed_equations_batch(latex_list: List[str], batch_size: int = 64) -> Optional[List[List[float]]]:
    """Wrapper that returns None if sentence-transformers isn't installed."""
    try:
        return embed_equations(latex_list, batch_size)
    except ImportError:
        return None
