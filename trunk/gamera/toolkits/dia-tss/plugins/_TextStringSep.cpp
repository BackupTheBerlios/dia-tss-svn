
        
    
  #include "gameramodule.hpp"
  #include "knnmodule.hpp"

    
    #include <string>
  #include <stdexcept>
  #include "Python.h"
  #include <list>

  using namespace Gamera;
  
        
      extern "C" {
#ifndef _MSC_VER
    void init_TextStringSep(void);
#endif
                          }

          static PyMethodDef _TextStringSep_methods[] = {
                            { NULL }
  };

                  
  DL_EXPORT(void) init_TextStringSep(void) {
    Py_InitModule("_TextStringSep", _TextStringSep_methods);
  }
  

