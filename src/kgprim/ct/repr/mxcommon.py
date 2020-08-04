from kgprim.motions import Axis
from kgprim.motions import MotionStep
from kgprim.ct      import models

def __rotx__a_x_b(mx, s, c):
    mx[1,1] = c;
    mx[1,2] = -s;
    mx[2,1] = s;
    mx[2,2] = c;

def __rotx__b_x_a(mx, s, c):
    mx[1,1] = c;
    mx[2,1] = -s;
    mx[1,2] = s;
    mx[2,2] = c;

def __roty__a_x_b(mx, s, c):
    mx[0,0] = c;
    mx[0,2] = s;
    mx[2,0] = -s;
    mx[2,2] = c;

def __roty__b_x_a(mx, s, c):
    mx[0,0] = c;
    mx[2,0] = s;
    mx[0,2] = -s;
    mx[2,2] = c;

def __rotz__a_x_b(mx, s, c):
    mx[0,0] = c;
    mx[0,1] = -s;
    mx[1,0] = s;
    mx[1,1] = c;

def __rotz__b_x_a(mx, s, c):
    mx[0,0] = c;
    mx[1,0] = -s;
    mx[0,1] = s;
    mx[1,1] = c;


def __tr_x__a_x_b(mx, length):
    mx[0,3] = length

def __tr_x__b_x_a(mx, length):
    mx[0,3] = -length

def __tr_y__a_x_b(mx, length):
    mx[1,3] = length

def __tr_y__b_x_a(mx, length):
    mx[1,3] = -length

def __tr_z__a_x_b(mx, length):
    mx[2,3] = length

def __tr_z__b_x_a(mx, length):
    mx[2,3] = -length


onRight = models.TransformPolarity.movedFrameOnTheRight
onLeft  = models.TransformPolarity.movedFrameOnTheLeft

X = Axis.X
Y = Axis.Y
Z = Axis.Z

setRot = {
    X : {
        onRight : __rotx__a_x_b,
        onLeft  : __rotx__b_x_a
    },
    Y : {
        onRight : __roty__a_x_b,
        onLeft  : __roty__b_x_a
    },
    Z : {
        onRight : __rotz__a_x_b,
        onLeft  : __rotz__b_x_a
    },
}

setTr = {
    X : {
        onRight : __tr_x__a_x_b,
        onLeft  : __tr_x__b_x_a
    },
    Y : {
        onRight : __tr_y__a_x_b,
        onLeft  : __tr_y__b_x_a
    },
    Z : {
        onRight : __tr_z__a_x_b,
        onLeft  : __tr_z__b_x_a
    },
}

ROT = MotionStep.Kind.Rotation
TR  = MotionStep.Kind.Translation

