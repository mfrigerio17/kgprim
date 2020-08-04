'''
A simple DSL to specify rigid motions (the "MotionsDSL").

This package defines a simple language to create objects of the
`kgprim.motions` module. That is, it defines _a_ file format to specify rigid
motions and sequences of rigid motions.

While this package depends on the `kgprim.motions` module, the converse is not
true.

This package also depends on textX, which is used for the grammar of the
language.

A generic entry of a document of the MotionDSL has this format:

`<frame name 1> -> <frame name 2> : <spec>`

which reads: "to go from `frame1` to `frame2`, `<spec>` steps must be taken.
Here is a short sample of the document format:

    Model MotionDSLSample

    // All the motion-steps referenced by this model are to be interpreted
    // in the current, moving frame
    Convention = currentFrame

    // A rotation about X followed by a translation along Y.
    // Use float literals for constant amounts
    fA -> fB : rotx(0.2) try(3.1)

    // Demonstrate the use of variables
    fE -> fF : rotx(q0)
    fF -> fG : roty(q1)

Identifiers appearing as the argument of a motion step are interpreted as
variables. The corresponding `kgprim.motions.MotionStep` object created when
loading the document will have a `kgprim.values.Variable` instance as the value
of its `amount` member.

See sample/sample.motdsl for a slightly larger sample.
'''
