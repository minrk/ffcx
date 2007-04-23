"Code generation for the UFC 1.0 format with DOLFIN"

__author__ = "Anders Logg (logg@simula.no)"
__date__ = "2007-03-24 -- 2007-04-05"
__copyright__ = "Copyright (C) 2007 Anders Logg"
__license__  = "GNU GPL Version 2"

# UFC code templates
from ufc import *

# FFC common modules
from ffc.common.utils import *
from ffc.common.debug import *
from ffc.common.constants import *

# FFC language modules
from ffc.compiler.language.restriction import *
from ffc.compiler.language.integral import *

# FFC format modules
import ufcformat

# Specify formatting for code generation
format = ufcformat.format

def write(generated_forms, prefix, options):
    "Generate UFC 1.0 code with DOLFIN wrappers for a given list of pregenerated forms"
    debug("Generating code for UFC 1.0 with DOLFIN wrappers")

    # Generate code for header
    output = ""
    output += generate_header(prefix, options)
    output += "\n"

    # Generate UFC code
    output += ufcformat.generate_ufc(generated_forms, "UFC_" + prefix, options)

    # Generate code for DOLFIN wrappers
    output += __generate_dolfin_wrappers(generated_forms, prefix, options)

    # Generate code for footer
    output += generate_footer(prefix, options)

    # Write file
    filename = "%s.h" % prefix
    file = open(filename, "w")
    file.write(output)
    file.close()
    debug("Output written to " + filename)

def generate_header(prefix, options):
    "Generate file header"

    # Check if BLAS is required
    if options["blas"]:
        blas_include = "\n#include <cblas.h>"
        blas_warning = "\n// Warning: This code was generated with '-f blas' and requires cblas.h."
    else:
        blas_include = ""
        blas_warning = ""
        
    return """\
// This code conforms with the UFC specification version 1.0
// and was automatically generated by FFC version %s.%s
//
// Warning: This code was generated with the option '-l dolfin'
// and contains DOLFIN-specific wrappers that depend on DOLFIN.

#ifndef __%s_H
#define __%s_H

#include <cmath>
#include <ufc.h>%s
""" % (FFC_VERSION, blas_warning, prefix.upper(), prefix.upper(), blas_include)

def generate_footer(prefix, options):
    "Generate file footer"
    return """\
#endif
"""

def __generate_dolfin_wrappers(generated_forms, prefix, options):
    "Generate code for DOLFIN wrappers"

    output = """\
// DOLFIN wrappers

#include <dolfin/Form.h>

"""

    for i in range(len(generated_forms)):
        (form_code, form_data) = generated_forms[i]
        form_prefix = ufcformat.compute_prefix(prefix, generated_forms, i)
        constructor_args = ", ".join(["dolfin::Function& w%d" % i for i in range(form_data.num_coefficients)])
        constructor_body = "\n".join(["    __coefficients.push_back(&w%d);" % i for i in range(form_data.num_coefficients)])
        if constructor_body == "":
            constructor_body = "    // Do nothing"
        output += """\
class %s : public dolfin::Form
{
public:

  %s(%s) : dolfin::Form()
  {
%s
  }

  /// Return UFC form
  virtual const ufc::form& form() const
  {
    return __form;
  }
  
  /// Return array of coefficients
  virtual const dolfin::Array<dolfin::Function*>& coefficients() const
  {
    return __coefficients;
  }

private:

  // UFC form
  UFC_%s __form;

  /// Array of coefficients
  dolfin::Array<dolfin::Function*> __coefficients;

};

""" % (form_prefix, form_prefix, constructor_args, constructor_body, form_prefix)
    
    return output
