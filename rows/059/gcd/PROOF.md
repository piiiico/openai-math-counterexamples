# Why the weighted GCD check certifies the two products

Alexander Richard Towell, with substantial OpenAI Codex assistance.
The relation and the two product formulas are OpenAI's; this note justifies
the independent arithmetic checker. It is a written proof, not a kernel proof.

## The source statement and finite input

Set d = 3^11 = 177147 and B = {b in Z : 0 < 2b < d, 3 does not divide b}.
The original manuscript's Lemma `seed:product` asks for integer coefficients
with E = sum e_b > 0 and

    product ((d-b)/b)^e_b = 1,
    product (((2d+b)(2d-b))/((3d-b)(d+b)))^e_b = 1.

The supplied JSON lists the nonzero support. The checker requires each index
to belong to B, forbids repeated indices and zero/noninteger coefficients,
and interprets every unlisted index as having coefficient zero. It recomputes
the coefficient sum, absolute sum, support size and largest decimal length
with arbitrary-precision integers and compares all four metadata fields.
It separately requires E > 0. All six integer factors are positive on B.

For each (b,e), the six weighted bases are

| Base | Exponent in first product | Exponent in second product |
| --- | ---: | ---: |
| d-b | e | 0 |
| b | -e | 0 |
| 2d+b | 0 | e |
| 2d-b | 0 | e |
| 3d-b | 0 | -e |
| d+b | 0 | -e |

This is a direct transcription of the two rational products. Negative
exponents are legitimate because all bases are positive. Combining identical
bases adds exponent pairs, so it preserves both products.

## Rewrite invariant

A term is a positive integer base n with an integer pair v. It represents
(n^v[0], n^v[1]) in Q_{>0} x Q_{>0}. A state consists of a pending list and a
stored basis; their combined represented product is invariant.

For a pending (n,v) and stored (a,u), put g = gcd(a,n). If g > 1, remove those
two terms and replace them by

    (a/g, u), (n/g, v), (g, u+v).

The exact equality

    a^u n^v = (a/g)^u (n/g)^v g^(u+v)

holds componentwise for all integer u and v. The divisions are exact. A unit
base or the pair (0,0) represents the identity and may be discarded. The
implementation uses only integer addition, exact division, comparison and GCD;
it never evaluates a base to one of the witness's large exponents.

The stored bases are pairwise coprime: insertion happens only after checking
GCD 1 against every stored base; a collision removes one stored base and puts
all replacement pieces back on the pending list. This also handles overlap
among the replacement pieces, such as gcd(12,18)=6 with quotients 2 and 3.

## Termination and acceptance

Consider the product W of all unweighted bases in the pending list and stored
basis. This positive integer is a proof device; the program does not compute
it. A collision replaces factors a*n by (a/g)*(n/g)*g = a*n/g, so W strictly
decreases. Discarding terms cannot increase it. Thus only finitely many
collisions occur. Each creates at most three pending terms; all other loop
iterations remove one pending term, so the algorithm terminates.

When the returned basis is empty, the invariant proves that both original
products equal 1. This implication needs no primality claim about any base.
Conversely, the final bases are pairwise coprime and greater than 1. If a
remaining exponent pair is nonzero, choose a component where it is nonzero
and a prime divisor of that base. Its valuation in that product is nonzero,
because no other final base is divisible by that prime. That product is not
1. Consequently the empty-basis test decides the two product identities.

The explicit witness's empty normal form, validated indices and positive E
therefore certify this particular witness for Lemma `seed:product`.

## Boundary of the conclusion

The source's trial-division validator and Pico's sieve validator already
verify this relation exactly. This packet supplies a different exact route;
it does not repair a missing arithmetic proof or claim a new counterexample.
It does not compute the cutoff/rank argument, decreasing-remainder chains,
variable counts, spectra, Seifert forms, monodromy, or homeomorphism. The JSON's
upstream `source_sha256` and `input_npz_sha256` are retained provenance fields;
their referenced generation artifacts are not reconstructed or verified here.
Our own source-file hashes bind the supplied witness and manuscript edition.
