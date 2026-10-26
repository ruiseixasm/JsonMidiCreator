# Frame
The class `Frame` is one of the most important classes, this class allows the focus on specific elements and parameters,
this woks alike the manipulation of a specific knob in a device, where you decide to do an isolated manipulation.
Frames are exclusive to the `Clip` class, and they mainly target to their elements.

## Element Filter
`Element` filters are the most important frames, because they set the scope of the `Clip` content to ba manipulated.

### Examples
```py
closed_hats = Trigger("Hat") * 16 << Velocity(70) << OnBeat()**Velocity(110)
closed_hats << DrumKit("808") << Title("Sixteen Closed Hats") << Channel(10)
closed_hats * 4 >> Plot()   # Shows the plot bellow
```

In the first line above, the first Velocity sets all the triggers as 70, but the last Velocity setting
is targeted to only the On Beat triggers. The effect of it can be seen in the following image.

![Sixteen Closed Hats](plot/Sixteen_Closed_Hats.png)

