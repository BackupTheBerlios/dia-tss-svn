/*
 * implementation of hough-transformation
*/
#ifndef HOUGH_TRANSFORM
#define HOUGH_TRANSFORM

#include "gamera.hpp"
#include <cmath>

namespace Gamera {

    Image* hough_transform( ImageVector &imgVec, PyObject* resultList, FloatVector *angleRange, double r, float t_precision, int orgX, int orgY) {
        typedef TypeIdImageFactory<FLOAT, DENSE> fact_type;
        ImageVector::iterator it = imgVec.begin();

        if((int)t_precision < 0) {
            std::cout << "negative values for t_precision not allowed!" << std::endl;
            return 0;
        }

        // set size for the hough-domain
        int houghX = 181;
        int houghY = (int)(sqrt(pow((double)orgY, 2) + pow((double)orgX, 2)) * sqrt(2) * 2 / r);
        int midY = houghY / 2; // prevent an odd resolution

        // create result image
        fact_type::image_type *image = fact_type::create(Point(0, 0), Dim(houghX, houghY));
        image->resolution( (houghX + houghY) / 2.0 ); // what is the best resolution?

        // create lists
        PyObject *xList = PyList_New(houghX);
        PyList_Append(resultList, xList);
        
        for(int i = 0; i < houghX; i++) {
            PyObject *yList = PyList_New(houghY);
            PyList_SetItem(xList, i, yList);

            for(int n = 0; n < houghY; n++) {
                PyObject *ccList = PyList_New(0);
                PyList_SetItem(yList, n, ccList);
            }
        }

        int x = 0,
            y = 0;
        
        // iterate thru the connected components
        long pos = 0;
        for(;it != imgVec.end(); it++, pos++) {
            // because ImageVector contains a pair we have to extract the image we operate on
            Image* cc = it->first;
            FloatVector::iterator tupleIt = angleRange->begin();
            
            // get centroids of images
            x = cc->center().x();
            y = cc->center().y();
        
            // iterate thru the range of angles for theta
            for(tupleIt = angleRange->begin(); tupleIt != angleRange->end(); tupleIt++) {
                double startAngle = *tupleIt;

                tupleIt++;

                double endAngle = *tupleIt;

                double dRho = 0.0f,
                       rTheta = 0.0f;
                int rho = 0;

                // iterate thru angels
                for(double theta = startAngle; theta <= endAngle; theta += t_precision) {
                    // convert theta from degree in radian
                    rTheta = ( theta * M_PI ) / 180.0f;

                    // calculate rho
                    dRho = (double)((double)x * cos(rTheta) + (double)y * sin(rTheta));
                    
                    rho = (int)(dRho / r);
                    rho = midY + (rho * -1);

                    // uncomment for debuging
                    // printf( "(cc)x = %d, (cc)y = %d, theta = %6.3f, orig. rho = %6.2f, y = %i\n", x, y, theta, dRho, rho );
                    float pixelValue = image->get( Point((int)theta, rho));
                    image->set(Point((int)theta, rho), (pixelValue + 1.0));

                    PyObject* yl = PyList_GetItem(xList, (int)theta);
                    if(yl == NULL)
                        PyErr_SetString(yl, "yl");

                    PyObject* ccl = PyList_GetItem(yl, rho);
                    if(ccl == NULL)
                        PyErr_SetString(ccl, "ccl");

                    PyObject* pyLong = PyLong_FromLong(pos);
                    if(pyLong == NULL)
                        PyErr_SetString(pyLong, "converting to long");

                    PyList_Append(ccl, pyLong);

                    // decrement reference-pointer at c++ side
                    Py_DECREF(pyLong);
                }
            }
            x = 0;
            y = 0;
        }
        
        // decrement reference-pointer at c++ side
        Py_DECREF(xList);

        return image;
    }
}
#endif // declaration end of hough_transform.hpp

