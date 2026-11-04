from jsonmidicreator import *

# Start by defining the sweeper function, where n is the number of notes being sweep
sweeper = lambda clip, n: (
	clip << (Note() * n << TimeSignature(6) << Resize(Beats(2))) * 4
	<< Gate(0.5) << Title("Office Phone Ring Sound")
)

# Now one creates the Sweep iterator
i_sweep = ISweep(sweeper)

# As you can see, the operator `>>` on a `Transformation` operand, auto calls the usual `Plot` operand.
phone_ring = Clip() >> i_sweep