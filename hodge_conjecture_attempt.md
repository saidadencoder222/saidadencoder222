# The Hodge Conjecture: what can be proved, and where every attempt stalls

**Status: open (Clay Millennium Problem). This file does NOT contain a proof.**

## 1. Statement
X = smooth projective complex variety of dimension n.
Hodge classes: Hdg^p(X) = H^{2p}(X,Q) ∩ H^{p,p}(X).
Conjecture: Hdg^p(X) is spanned over Q by cohomology classes [Z] of algebraic subvarieties Z of codimension p.

## 2. What is provable

**p = 0, p = n.** Trivial (fundamental class, point class).

**p = 1 (Lefschetz (1,1)).** From the exponential sequence
0 -> Z -> O_X -> O_X^* -> 0 we get
Pic(X) = H^1(O_X^*) -> H^2(X,Z) -> H^2(O_X).
A class in H^2(X,Z) is the c_1 of a line bundle iff it maps to 0 in H^2(O_X),
i.e. iff it has no (0,2) component, i.e. iff (being real) it is of type (1,1).
Line bundle with a section => divisor => algebraic cycle. Rational case: clear denominators.

**p = n-1.** Hard Lefschetz: L^{n-2}: H^2 -> H^{2n-2} is an isomorphism, L = cup with a hyperplane class
(itself algebraic). It preserves Hodge type, so Hdg^{n-1} = L^{n-2} Hdg^1, all algebraic.

**Consequence:** true for n <= 3. First open case: n = 4, p = 2.

## 3. Why the natural attempts fail

1. **Integral version is false.** Atiyah-Hirzebruch (1962): torsion integral Hodge
   classes that are not algebraic. Kollar: non-torsion integral counterexamples
   on a product-type threefold. So any proof must use Q-coefficients seriously, and
   cannot be a "Hodge class -> holomorphic object" argument that works over Z.

2. **Analytic approach (Lefschetz-style).** For p = 1 the obstruction lives in
   H^2(O_X) and the existence of a section is automatic from Riemann-Roch-type results.
   For p >= 2 the relevant objects are rank-p bundles / coherent sheaves, and a
   Hodge class need not be a Chern class of any holomorphic bundle. (Voisin 2002: on
   some Calabi-Yau-type threefolds, Hodge classes in the *Kahler*, non-projective
   setting are NOT combinations of Chern classes of coherent sheaves, so
   projectivity must be used essentially; the Kahler version is false.)

3. **Motivic / Tannakian approach.** Hodge classes are the invariants of the Mumford-Tate group
   MT(X). If one knew all Hodge classes were *absolute* Hodge (Deligne) one would get
   Galois-invariance consequences, but absolute Hodge => algebraic is itself the open step.
   Deligne proved Hodge classes on abelian varieties are absolute Hodge; this still does not
   give algebraicity.

4. **Hodge loci / transcendence (recent).** Cattani-Deligne-Kaplan: the locus where a given
   class stays Hodge is algebraic. Bakker-Klingler-Tsimerman, Bakker-Tsimerman use o-minimal
   geometry to prove algebraicity of period-map images. This controls *where* Hodge classes
   exist in families, not that they are cycles.

5. **Known cases are special.** Abelian varieties of CM type / Weil type (partial, Schoen, Moonen-Zarhin),
   products of elliptic curves, some cubic fourfolds (Hodge classes spanned by
   known surfaces, Zucker/Voisin), Fermat varieties of low degree (Shioda). Each uses
   explicit constructions; none generalises.

## 4. Where a hypothetical proof would have to break new ground
A proof needs a mechanism producing an algebraic subvariety from purely cohomological
(topological + Hodge-theoretic) data. Nothing in Hodge theory presently provides such a
mechanism; every known route either proves a weaker statement (above) or reduces the
conjecture to another equally open one (Grothendieck's standard conjectures, Tate
conjecture over finite fields, absolute-Hodge => algebraic).

## 5. Bottom line
- Proven: dim <= 3, plus assorted special families.
- Open: dimension 4 in general (e.g. Hdg^2 on a general fourfold), and everything beyond.
- I can explain any of the proofs above in detail, but I cannot supply a proof of the full conjecture.

## Further reading
- Deligne, *The Hodge conjecture* (Clay problem statement)
- Lewis, *A Survey of the Hodge Conjecture*
- Voisin, *Hodge Theory and Complex Algebraic Geometry I & II*
- Bakker-Klingler-Tsimerman, *Tame topology of arithmetic quotients and algebraicity of Hodge loci*
