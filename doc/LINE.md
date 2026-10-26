# Line
A `Line` is intended to target a `Clip` and set its containing elements.

A line has this tree structure:
- `Line`
    - `Token`
        - `Parameter`

## Line components

| Component   | Separator |
|-------------|-----------|
| Token       | `,`       |
| Field       | `:`       |
| Parameter   | `_`       |

### Examples

- `"t:1/16_0m_2S:Snare:40, :_6S, :_9S, :_11S, :_15S,"`
    - In this example one can see 5 tokens separated with `,`, the first token as `"t:1/16_0m_2S:Snare:40"`, where *t* stands for `Trigger`, with the second `Field`, representing
    its `Locus`, placement on the "staff", with the first `Parameter` setting its `Duration`.
    - The following tokens, `":_6S, :_9S, :_11S, :_15S,"`, inherit the previous configurations, so, they are all implicitly triggers ('t'), and they don't set any durations but just positions where 'S' means `Step` and is the default meaning for integer. 


## Token
In a `Line`, the first `Token` is related to the type of `Element`, these are the chars associated to each of those types.

| Acronym | Element         |
|---------|-----------------|
| 'r'     | `Rest`          |
| 't'     | `Trigger`       |
| 'n'     | `Note`          |
| 'c'     | `Chord`         |
| 'cl'    | `Cluster`       |
| 'tp'    | `Tuplet`        |
| 'cc'    | `ControlChange` |
| 'at'    | `Aftertouch`    |
| 'pb'    | `PitchBend`     |
| 'a'     | `Automation`    |
| 'pc'    | `ProgramChange` |
| 'msb'   | `BankSelectMSB` |
| 'lsb'   | `BankSelectLSB` |

### Examples

- `"n:1/4, :1/4, :1/4, :1/4"`
    - In this example the first char means a Note, the default element if none is specified and not inherited, this `Line` represents a sequence of 4 quarter notes at the middle C.
- `"n:1/8:C5#, n_9:1/8::75"`
    - The first `Token`, has `"C5#"`, this is the `Pitch` `Field` in the case of a note, and sets the note as *C#* in the `Octave` `5`, the following token inherits this note pitch if nothing is
    specified in the same field, which in the given example is the case;
    - The second `Token` has `"n_9"`, this stands for `Note` on the midi `Channel` `9`, while the last one, `"75"`, sets the note `Velocity`.

