[← Back to README](README.md)

# Iterations
There is a special `Transformation` sub `Operand` type called `IteratedTransformation`,
this operand is split in two types:
- IFrame
    - This is the easier and faster way of iterate a given `Clip`, because the source of
    Chaos is placed in the `Frame` with the process of transformation in it.
- ITame
    - This requires more configuration where the source of Chaos (`Tamer`) is in the Operand
    itself together with the process of transformation.

The first type is the recommended one, because it's more intuitive and immediate.




