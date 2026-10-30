[← Back to README](README.md)

# Iterations
There is a special `Transformation` sub `Operand` type called `IteratedTransformation`,
this operand is split in two types:
- `IMultiFrame`
    - This is intended to generate patterns, when one creates a "grid" of triggers, like 64
    per sample in order to remove the unwanted ones by using the `Action` `Delete`.
- `IFrame`
    - This is the easier and faster way of iterate a given `Clip`, because the source of
    Chaos is placed in the `Frame` with the process of transformation in it.
- `ITame`
    - This requires more configuration where the source of `Chaos` (`Tamer`) is in the `Operand`
    itself together with the process of transformation.

The first type is the recommended one, because it's more intuitive and immediate.

## Moving Steps

```py
# The pattern
simple_pattern = Trigger("Hat") * 16 << Velocity(70) << OnBeat()**Velocity(110)
simple_pattern += Trigger("Kick") * 16 & OnBeat()
simple_pattern << DrumKit("808") << Channel(10) << Title("Iterating Steps")
simple_pattern *= 2
# The iteration
framed_trigger = Equal("Kick")**Chance(1/8)**Step(1)
i_frame = IAdd(framed_trigger, no_repeats=True)
# Finally start iterating
simple_pattern >> Plot(i_frame)
# Realization the Iteration 5 is quite usable
```

![Iterating Steps](plot/Iterating_Steps.png)


## Creating Patterns
The information in a Clip resides in its elements, so, the elements are what defines the range
of a given Pattern of triggers, so, instead of thinking of adding triggers one should think
in removing them from a given occupied range filled with them.

If one wants to have a range of triggers say for four samples, the starting point is the following
```py
from jsonmidicreator import *
# Start by setting the Clip parameters
pattern_grid = Clip() << DrumKit("808") << Title("Triggers Pattern of 64 steps")
pattern_grid += Trigger("Kick") * 64 + Trigger("Snare") * 64 + Trigger("Hat") * 64 + Trigger("Shaker") * 64
pattern_grid << Channel(10) << Disable()    # By default they are disabled
# This is the criteria of triggering, the grid is 64 but the the probabilities bellow are 1 measure based
i_multi_frame = IMultiFrame([
    Equal("Kick")**Chance(1/4)**Enable(),
    Equal("Snare")**Chance(1/2)**Enable(),
    Equal("Hat")**Chance(0.9)**Enable(),
    Equal("Shaker")**Chance(0.95)**Enable()
], no_repeats=True)
# The pattern_grid is just the grid source, the `Plot` always does a copy of the input (decoupling guaranteed)
playable_clip = pattern_grid >> Plot(i_multi_frame)
```
