# Anti-Fake Expansion 006

The main false pass risk is fake N>=20 expansion.

Future execution must fail if it uses:

- `ACTION_HANDLES = 20`
- a fixed list of 20 recipes
- semantic action families hidden behind anonymous IDs
- natural language action descriptions as selector features
- renderer text as selector input
- branch logic such as `if N == 7` or `if N == 20`
- action IDs that encode semantic role or public action name

The required object is a variable-N option interface. The number of options must be a property of the input list, not a hard-coded selector branch.
