import kgprim.ct.repr.mxcommon as common


class RotationMatrixMixin:
    @property
    def matrixSize(self):
        return 3

    def setRotation(self, axis, polarity, mx, s, c):
        common.setRot[axis][polarity](mx, s, c)

    def setTranslation(self, axis, polarity, mx, length):
        pass

class HCoordinatesMixin:
    @property
    def matrixSize(self):
        return 4

    def setRotation(self, axis, polarity, mx, s, c):
        common.setRot[axis][polarity](mx, s, c)

    def setTranslation(self, axis, polarity, mx, length):
        common.setTr[axis][polarity](mx, length)