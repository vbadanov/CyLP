import numpy as np
from operator import itemgetter
from random import shuffle
from math import floor
from PivotPythonBase import PivotPythonBase
from CyLP.cy.CyClpSimplex import VarStatus


class LIFOPivot(PivotPythonBase):
    '''
    Last-In-First-Out pivot rule implementation.

    **Usage**

    >>> from CyLP.cy import CyClpSimplex
    >>> from CyLP.py.pivots import LIFOPivot
    >>> from CyLP.py.pivots.LIFOPivot import getMpsExample
    >>> # Get the path to a sample mps file
    >>> f = getMpsExample()
    >>> s = CyClpSimplex()
    >>> s.readMps(f)  # Returns 0 if OK
    0
    >>> pivot = LIFOPivot(s)
    >>> s.setPivotMethod(pivot)
    >>> s.primal()
    'optimal'
    >>> round(s.objectiveValue, 5)
    2520.57174

    '''

    def __init__(self, clpModel):
        self.dim = clpModel.nRows + clpModel.nCols
        self.clpModel = clpModel
        #self.banList = np.zeros(self.dim, np.int)
        self.banList = []
        self.priorityList = range(self.dim)

    def pivotColumn(self):
        'Finds the variable with the best reduced cost and returns its index'
        s = self.clpModel
        rc = s.reducedCosts
        dim = s.nCols + s.nRows

        tol = s.dualTolerance

        for i in self.priorityList:
            #flagged or fixed
            if s.flagged(i) or s.getVarStatus(i) == VarStatus.fixed:
                continue

            #TODO: can we just say dualInfeasibility = rc[i] ** 2
            if s.getVarStatus(i) == VarStatus.atUpperBound:  # upperbound
                dualInfeasibility = rc[i]
            elif (s.getVarStatus(i) == VarStatus.superBasic or
                    s.getVarStatus(i) == VarStatus.free):  # free or superbasic
                dualInfeasibility = abs(rc[i])
            else:  # lowerbound
                dualInfeasibility = -rc[i]

            if dualInfeasibility > tol:
                return i

        return -1

    def isPivotAcceptable(self):
        '''
        Inserts the leaving variable index as the first element
        in self.priorityList
        '''
        s = self.clpModel

        pivotRow = s.pivotRow()
        if pivotRow < 0:
            return True

        pivotVariable = s.getPivotVariable()
        leavingVarIndex = pivotVariable[pivotRow]

        self.priorityList.remove(leavingVarIndex)
        self.priorityList.insert(0, leavingVarIndex)

        return True


def getMpsExample():
    import os
    import inspect
    curpath = os.path.dirname(inspect.getfile(inspect.currentframe()))
    return os.path.join(curpath, '../../input/p0033.mps')