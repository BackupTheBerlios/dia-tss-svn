#ifndef INC_HOUGH_TRANSFORM
#define INC_HOUGH_TRANSFORM

#include "gamera.hpp"

namespace Gamera {

  /* This is a very simple plugin that simply fills the image with white

     See the Gamera plugin documentation for more information on how to
     write Gamera plugins.
   */
    template<class T>
    PyObject* hough_transform(T& image) {
        PyObject* pyList = PyList_New(10);
        if( pyList == NULL ) {
            //FIXME: Fehler abfangen
            return 0;
        }

        PyObject* pyTuple = PyTuple_New(2);
        if( pyTuple == NULL ) {
            //FIXME: Fehler abfangen
            return 0;
        }

        PyObject* pyF1 = PyFloat_FromDouble( 5.6f );

        PyTuple_SET_ITEM(pyTuple, 0, pyF1);
        PyTuple_SET_ITEM(pyTuple, 1, pyF1);
       
        PyList_Append( pyList, pyTuple);
        return pyList;
    }
}

#endif
