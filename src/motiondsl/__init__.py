'''
A DSL (Domain Specific Language) to specify rigid motions - the "MotionsDSL"

This package defines a simple language to represent objects of the
`kgprim.motions` module. That is, it defines *a* file format to specify rigid
motions and sequences of rigid motions.

A generic entry of a document of the MotionDSL has this format:

`<frame name 1> -> <frame name 2> : <spec>`

which reads: "to go from `frame1` to `frame2`, `<spec>` steps must be taken.
Here is a short sample of a complete document:

    Model MotionDSLSample

    Convention = currentFrame
    // -> all the motion-steps referenced by this model are to be interpreted
    // in the current, moving frame

    fA -> fB : rotx(0.2) try(3.1)
    // A rotation about X followed by a translation along Y.
    // Use float literals for constant amounts

    // Demonstrate the use of variables
    fE -> fF : rotx(q0)
    fF -> fG : roty(q1)

Identifiers appearing as the argument of a motion step are interpreted as
variables. The corresponding `kgprim.motions.MotionStep` object created when
loading the document will have a `kgprim.values.Variable` instance as the value
of its `amount` member.

See the file `sample/sample.motdsl` for a slightly larger sample.

While this package depends on the `kgprim.motions` module, the
converse is not true.

We use [textX](https://github.com/textX/textX) to create the parser of the
language.
'''
