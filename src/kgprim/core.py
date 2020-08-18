'''
Core primitives like `RigidBody` or Cartesian `Frame`.

All the classes are nothing more than named entities, and are meant to be used
as symbolic models. For example, a `Pose` is represented simply by two instances
of `Frame`, with two different names.
'''

class RigidBody():
    def __init__(self, n):
        '''
        Constructor arguments:
          - `n`: the desired name for this instance
        '''
        self._name = n

    @property
    def name(self):
        '''The name of this rigid body'''
        return self._name

    def __eq__(self, rhs): return isinstance(rhs, RigidBody) and self.name==rhs.name
    def __hash__(self)   : return 47 * hash(self._name)
    def __str__(self)    : return self.name


class Attachable():
    def __init__(self):
        None


class Point(Attachable):
    def __init__(self, n):
        super().__init__()
        self._name = n

    @property
    def name(self): return self._name

    def __eq__(self, rhs): return isinstance(rhs, Point) and self.name==rhs.name
    def __hash__(self)   : return 31 * hash(self._name)
    def __str__(self)    : return self.name



class Frame(Attachable):
    '''
    A Cartesian coordinate frame.
    '''

    def __init__(self, n):
        '''
        Constructor arguments:
          - `n`: the desired name for this instance
        '''
        self._name = n

    @property
    def name(self): return self._name

    def __eq__(self, rhs):
        return isinstance(rhs, Frame) and self._name == rhs._name

    def __hash__(self):
        return 97 * hash(self._name)

    def __str__(self):
        return self.name


class Pose:
    '''
    The relative pose of `target` with respect to `reference`.

    Both `target` and `reference` should be two instances of `Frame`.
    '''

    def __init__(self, target, reference):
        self.target    = target
        self.reference = reference

    def __eq__(self, rhs):
        return isinstance(rhs, Pose) and self.target==rhs.target and self.reference==rhs.reference

    def __hash__(self):
        return 43*hash(self.target) + 11*hash(self.reference)

    def __str__(self):
        return self.target.name + " wrt " + self.reference.name
    def __repr__(self):
        return self.__str__()

class Velocity():
    def __init__(self, target, reference):
        self.target    = target
        self.reference = reference

    def __eq__(self, rhs):
        return isinstance(rhs, Velocity) and self.target==rhs.target and self.reference==rhs.reference

    def __hash__(self):
        return 77*hash(self.target) + 19*hash(self.reference)

    def __str__(self):
        return "V of " + self.target.name + " wrt " + self.reference.name
    def __repr__(self):
        return self.__str__()


def poseCompose(pose1, pose2):
    if pose1.reference != pose2.target :
        raise RuntimeError("Cannot compose {0} with {1}, reference/target mismatch".format(pose1,pose2))
    return Pose(pose1.target, pose2.reference)

def velCompose(v1, v2):
    if v1.reference != v2.target:
        raise RuntimeError("Cannot compose {0} with {1}, reference/target mismatch".format(v1,v2))
    return Velocity(v1.target, v2.reference)


class Attachment():
    '''
    Models the attachment relation between an attachable entity (like a
    Frame) and a RigidBody
    '''
    def __init__(self, entity, body):
        if not isinstance(body, RigidBody) :
            raise ValueError("Things can only be attached to rigid bodies")
        if not isinstance(entity, Attachable) :
            raise ValueError("Only 'attachable' objects like Points can be attached to rigid bodies")

        self._entity = entity
        self._body   = body
        self.attrs   = {}

    @property
    def entity(self): return self._entity
    @property
    def body(self): return self._body

    # Pretend to be the entity
    def __getattr__(self, name):
        return getattr(self.entity, name)

    def __str__(self):
        return self.entity.name + " attached to " + self.body.name
    def __repr__(self):
        return self.entity.name + "@" + self.body.name