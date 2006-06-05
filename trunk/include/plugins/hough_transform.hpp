/*
 * call the function out of gamera as follow's:
 *
 * 1. load image and convert to ONEBIT
 * 2. perform cc_analysis on ONEBIT image
 * 3. call hough_transform 
 *      t = tss.plugins.TextStringSep.hough_transform( ccs0, [0.0,270.0], 1, 0.3, 640, 480 )
*/
#ifndef HOUGH_TRANSFORM
#define HOUGH_TRANSFORM

#include "gamera.hpp"

namespace Gamera {

    Image* hough_transform( ImageVector &imgVec, FloatVector *angleRange, int r, float t_precision, int orgX, int orgY ) {
        typedef TypeIdImageFactory<FLOAT, DENSE> fact_type;
        ImageVector::iterator it = imgVec.begin();

        if( t_precision <= 0 ) {
            std::cout << "negative values for t_precision not allowed!" << std::endl;
            return 0;
        }

        // resolution should be calculated, but how and what does it mean???
        int resolution = (int)( 360 / t_precision );        
        
        // set size for the hough-domain
        int houghX = 360,
            houghY = (int)( sqrt( ( orgX / 2 ) * ( orgX / 2 ) + ( orgY / 2 ) * ( orgY / 2 ) ) );

        // create result image
        fact_type::image_type *image = fact_type::create( Point( 0, 0 ), Dim( houghX + 1, houghY + 1 ) );
        image->resolution(100);// resolution );

        int x = 0,
            y = 0;
        
        // iterate thru the connected components
        for( ;it != imgVec.end(); it++ ) {
            // because ImageVector contains a pair we have to extract the image we operate on
            Image* cc = it->first;
            FloatVector::iterator tupleIt = angleRange->begin();
            
            // get centroids of images
            x = cc->center().x();
            y = cc->center().y();
        
            // iterate thru the range of angles for theta
            for( tupleIt = angleRange->begin(); tupleIt != angleRange->end(); tupleIt++ ) {
                double startAngle = *tupleIt;

                tupleIt++;

                double endAngle = *tupleIt;

                double rTheta = 0.0f;
                int rho = 0;
                double dRho = 0.0f;

                // iterate thru angels
                for( double theta = startAngle; theta <= endAngle; theta += t_precision ) {
                    // convert theta from degree in radian
                    rTheta = ( theta * M_PI ) / 180.0f;
                    
                    // calculate rho
                    dRho = ( ( (double)x - ( (double)orgX / 2.0 ) ) * cos( rTheta ) ) +
                          ( ( (double)y - ( (double)orgY / 2.0 ) ) * sin( rTheta ) );

                    rho = (int)dRho;

                    if( dRho >= ( rho + 0.5 ) )
                        rho += 1;

                    rho = -( rho - houghY );

                    // print some values ( for debuging )
                    //printf( "(cc)x = %d, (cc)y = %d, theta = %6.3f precision = %6.3f result = %d\n", x, y, theta, t_precision, rho );

                    if( ( rho > 0 ) && ( rho <= houghY ) ) {
                        float pixelValue = image->get( Point( (int)theta, rho ) );
                        image->set( Point( (int)theta, rho ), ( pixelValue + 10.0 ) );
                    }
                }
            }
            x = 0;
            y = 0;
        }
        
        return image;
    }
}
#endif // declaration end of hough_transform.hpp

