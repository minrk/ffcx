__author__ = "Anders Logg (logg@simula.no)"
__date__ = "2004-09-27 -- 2006-09-20"
__copyright__ = "Copyright (C) 2004-2006 Anders Logg"
__license__  = "GNU GPL Version 2"

# Python modules
import sys

# FFC common modules
sys.path.append("../../")
from ffc.common.debug import *
from ffc.common.exceptions import *

# FFC format modules
from ffc.format import dolfin
from ffc.format import latex

# FFC compiler modules
from index import *
from algebra import *
from reassign import *
from finiteelement import *
from elementtensor import *

class Form:
    """A Form represents a multi-linear form typically appearing in
    the variational formulation of partial differential equation.
    
    Attributes:

        sum     - a Sum representing the multi-linear form
        name    - a string, the name of the multi-linear form

    The following data is generated by the compiler:

        AK          - interior ElementTensor
        ASe          - exterior boundary ElementTensor
        ASi          - interior boundary ElementTensor
        cK           - list of precomputed coefficient declarations for interior
        cSe          - list of precomputed coefficient declarations for exterior boundary
        cSi          - list of precomputed coefficient declarations for interior boundary
        rank         - primary rank of the multi-linear form
        dims         - list of primary dimensions
        indices      - list of primary indices
        nfunctions   - number of functions (coefficients)
        nprojections - number of projections (coefficients)
        nconstants   - number of constants
        test         - FiniteElement defining the test space
        trial        - FiniteElement defining the trial space
        elements     - list of FiniteElements for Functions
        projections  - list of corresponding projections
        format       - the format used to build the Form (a dictionary)
        shape        - shape on which the form is defined
        num_ops      - number of operations in computation of element tensor

    A multi-linear form is first expressed as an element of the
    algebra (a Sum) and is then post-processed to generate a sum
    of ElementTensors, where each ElementTensor is expressed as
    a product of a ReferenceTensor and a GeometryTensor."""

    def __init__(self, sum, name):
        "Create Form."

        # Initialize Form
        self.sum         = Sum(sum)
        self.name        = name
        self.AK          = None
        self.ASe         = None
        self.ASi         = None
        self.cK          = None
        self.cSe         = None
        self.cSi         = None
        self.rank        = None
        self.dims        = None
        self.indices     = None
        self.nfunctions  = 0
        self.projections = 0
        self.nconstants  = 0
        self.test        = None
        self.trial       = None
        self.elements    = None
        self.projections = None
        self.format      = None

        # Reassign indices
        debug("Before index reassignment: " + str(sum), 2)
        reassign_indices(self.sum)

        return

    def reference_tensor(self, term = None):
        "Return interior reference tensor for given term."
        if term == None:
            if len(self.AK.terms) > 1:
                raise FormError, (self, "Form has more than one term and term not specified.")
            else:
                return self.AK.terms[0].A0.A0
        else:
            return self.AK.terms[term].A0.A0

    def primary_indices(self, term = None):
        "Return primary indices for interior reference tensor."
        if term == None:
            if len(self.AK.terms) > 1:
                raise FormError, (self, "Form has more than one term and term not specified.")
            else:
                return self.AK.terms[0].A0.i.indices
        else:
            return self.AK.terms[term].A0.i.indices

    def secondary_indices(self, term = None):
        "Return primary indices for interior reference tensor."
        if term == None:
            if len(self.AK.terms) > 1:
                raise FormError, (self, "Form has more than one term and term not specified.")
            else:
                return self.AK.terms[0].A0.a.indices
        else:
            return self.AK.terms[term].A0.a.indices

    def __repr__(self):
        "Print nicely formatted representation of Form."
        return str(self.sum)
