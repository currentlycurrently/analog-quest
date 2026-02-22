#!/usr/bin/env python3
"""
Extract mathematical equations from papers and convert to canonical form.
This is the foundation of REAL isomorphism detection.
"""

import re
import sympy as sp
from sympy import symbols, Function, Eq, diff, simplify
from typing import List, Dict, Optional, Tuple
import json

class EquationExtractor:
    """Extract and canonicalize mathematical equations from scientific papers."""

    def __init__(self):
        # Common symbols in different domains
        self.symbol_mappings = {
            'ecology': {'N': 'population', 'r': 'growth_rate', 'K': 'carrying_capacity'},
            'chemistry': {'A': 'reactant_1', 'B': 'reactant_2', 'k': 'rate_constant'},
            'economics': {'P': 'price', 'Q': 'quantity', 'S': 'supply', 'D': 'demand'},
            'physics': {'x': 'position', 'v': 'velocity', 't': 'time', 'm': 'mass'},
            'neuroscience': {'V': 'voltage', 'I': 'current', 'g': 'conductance'}
        }

    def extract_latex_equations(self, text: str) -> List[str]:
        """Extract LaTeX equations from text."""
        # Match display equations
        display_pattern = r'\$\$(.*?)\$\$'
        inline_pattern = r'\$(.*?)\$'

        equations = []

        # Get display equations first (they're usually more important)
        display_matches = re.findall(display_pattern, text, re.DOTALL)
        equations.extend(display_matches)

        # Get inline equations
        inline_matches = re.findall(inline_pattern, text)
        # Filter out simple variables (single letters/numbers)
        inline_equations = [eq for eq in inline_matches if len(eq) > 3 and any(op in eq for op in ['=', '\\frac', '\\partial', '\\dot'])]
        equations.extend(inline_equations)

        return equations

    def latex_to_sympy(self, latex_eq: str) -> Optional[sp.Expr]:
        """Convert LaTeX equation to SymPy expression."""
        try:
            # Clean up common LaTeX patterns
            latex_eq = latex_eq.strip()

            # Replace common LaTeX commands
            replacements = {
                r'\\dot{(\w+)}': r'd\1_dt',  # Time derivatives
                r'\\partial': 'd',  # Partial derivatives
                r'\\frac{d(\w+)}{dt}': r'd\1_dt',  # Derivatives
                r'\\alpha': 'alpha',
                r'\\beta': 'beta',
                r'\\gamma': 'gamma',
                r'\\lambda': 'lambda',
                r'\\mu': 'mu',
                r'\\sigma': 'sigma',
                r'\\tau': 'tau'
            }

            for pattern, replacement in replacements.items():
                latex_eq = re.sub(pattern, replacement, latex_eq)

            # Try to parse with SymPy
            expr = sp.parse_expr(latex_eq, transformations='all')

            # If it's an equation (Eq), extract the left and right sides
            if isinstance(expr, sp.Eq):
                # For now, just work with the right-hand side (the dynamics)
                return expr.rhs

            return expr

        except Exception as e:
            print(f"Failed to parse: {latex_eq[:50]}... Error: {e}")
            return None

    def canonicalize_equation(self, expr: sp.Expr) -> Dict:
        """Convert equation to canonical form for comparison."""
        if expr is None:
            return None

        canonical = {
            'type': None,
            'order': None,
            'variables': [],
            'parameters': [],
            'structure': None,
            'canonical_form': None
        }

        # Identify equation type
        if expr.has(sp.Derivative):
            canonical['type'] = 'differential'
            # Get order of differential equation
            derivatives = expr.atoms(sp.Derivative)
            max_order = max([d.derivative_count for d in derivatives])
            canonical['order'] = max_order
        elif expr.is_polynomial():
            canonical['type'] = 'polynomial'
            canonical['order'] = sp.degree(expr)
        else:
            canonical['type'] = 'general'

        # Extract variables and parameters
        canonical['variables'] = [str(s) for s in expr.free_symbols]

        # Create structural signature (invariant under renaming)
        canonical['structure'] = self._structural_signature(expr)
        canonical['canonical_form'] = str(simplify(expr))

        return canonical

    def _structural_signature(self, expr: sp.Expr) -> str:
        """Create a structural signature that's invariant under variable renaming."""
        # This is a simplified version - real implementation would be more sophisticated

        # Count operation types
        ops = {
            'add': expr.count_ops([sp.Add]),
            'mul': expr.count_ops([sp.Mul]),
            'pow': expr.count_ops([sp.Pow]),
            'div': expr.count_ops([sp.Div])
        }

        # Create signature
        signature = f"ops:{ops},vars:{len(expr.free_symbols)}"

        if expr.has(sp.Derivative):
            derivatives = expr.atoms(sp.Derivative)
            signature += f",deriv:{len(derivatives)}"

        return signature

    def compare_structures(self, eq1: Dict, eq2: Dict) -> float:
        """Compare two equation structures for similarity."""
        if not eq1 or not eq2:
            return 0.0

        similarity = 0.0

        # Same type bonus
        if eq1['type'] == eq2['type']:
            similarity += 0.3

        # Same order bonus
        if eq1.get('order') == eq2.get('order'):
            similarity += 0.2

        # Similar variable count
        var_diff = abs(len(eq1['variables']) - len(eq2['variables']))
        if var_diff == 0:
            similarity += 0.2
        elif var_diff == 1:
            similarity += 0.1

        # Similar structure signature
        if eq1.get('structure') == eq2.get('structure'):
            similarity += 0.3

        return similarity

def test_lotka_volterra():
    """Test extraction on Lotka-Volterra equations."""

    extractor = EquationExtractor()

    # Predator-prey version (ecology)
    ecology_text = """
    The Lotka-Volterra equations describe predator-prey dynamics:
    $$\\frac{dx}{dt} = ax - bxy$$
    $$\\frac{dy}{dt} = -cy + dxy$$
    where $x$ is prey population and $y$ is predator population.
    """

    # Chemical reaction version
    chemistry_text = """
    The autocatalytic reaction follows:
    $$\\frac{d[A]}{dt} = k_1[A] - k_2[A][B]$$
    $$\\frac{d[B]}{dt} = -k_3[B] + k_4[A][B]$$
    where $[A]$ and $[B]$ are concentrations.
    """

    print("Testing Lotka-Volterra Isomorphism Detection")
    print("=" * 50)

    # Extract equations
    eco_eqs = extractor.extract_latex_equations(ecology_text)
    chem_eqs = extractor.extract_latex_equations(chemistry_text)

    print(f"Found {len(eco_eqs)} ecology equations")
    print(f"Found {len(chem_eqs)} chemistry equations")

    # Convert to canonical form
    eco_canonical = []
    for eq in eco_eqs:
        sympy_eq = extractor.latex_to_sympy(eq)
        if sympy_eq is not None:
            canonical = extractor.canonicalize_equation(sympy_eq)
            eco_canonical.append(canonical)
            print(f"\nEcology: {eq}")
            print(f"Canonical: {canonical}")

    chem_canonical = []
    for eq in chem_eqs:
        sympy_eq = extractor.latex_to_sympy(eq)
        if sympy_eq is not None:
            canonical = extractor.canonicalize_equation(sympy_eq)
            chem_canonical.append(canonical)
            print(f"\nChemistry: {eq}")
            print(f"Canonical: {canonical}")

    # Compare structures
    if eco_canonical and chem_canonical:
        similarity = extractor.compare_structures(eco_canonical[0], chem_canonical[0])
        print(f"\nStructural similarity: {similarity:.2f}")

        if similarity > 0.7:
            print("✓ ISOMORPHISM DETECTED!")
            print("These equations have the same mathematical structure.")
        else:
            print("✗ Different structures")

    return eco_canonical, chem_canonical

if __name__ == "__main__":
    print("Mathematical Equation Extraction System")
    print("Building the foundation for REAL isomorphism detection")
    print()

    # Test on known isomorphism
    eco, chem = test_lotka_volterra()

    print("\n" + "="*50)
    print("This is what we should have been doing all along.")
    print("Finding that dx/dt = ax - bxy IS THE SAME as d[A]/dt = k₁[A] - k₂[A][B]")
    print("Not 'both have feedback loops'.")