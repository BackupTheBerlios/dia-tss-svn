#ifndef INC_HOUGH_TRANSFORM
#define INC_HOUGH_TRANSFORM

#include "gamera.hpp"

namespace Gamera {

    Image* hough_transform( ImageVector& imgVec, FloatVector *angleRange, int r, float t_precision, int orgX, int orgY ) {
        typedef TypeIdImageFactory<FLOAT, DENSE> fact_type;
        ImageVector::iterator it = imgVec.begin();

        int resolution = 360 / t_precision;
        
        int x = 0,
            y = 0;

        // size for the hough-domain
        int houghX = 360,
            houghY = sqrt( ( orgX / 2 ) * ( orgX / 2 ) + ( orgY / 2 ) * ( orgY / 2 ) );

        
        fact_type::image_type *image = fact_type::create( Point( 0, 0 ), Dim( houghX + 1, houghY + 1 ) );
        image->resolution( 600 );//theta );
       
        int ranges = 0,
            angleVecSize = 0;
        
        angleVecSize = angleRange->size();
        ranges = angleVecSize / 2 ;

        
        // iterate thru the connected components
        for( ;it != imgVec.end(); it++ ) {
            // because ImageVector contains a pair we have to extract the image we operate on
            Image* cc = it->first;
            FloatVector::iterator tupleIt = angleRange->begin();
            
            x = cc->center().x();
            y = cc->center().y();
            
            // print centroids of the connected components ( for debuging )
            printf( "%d, %d\n", x, y );
        
            // iterate thru the range of angles where to
            // calculate rho and theta
            for( ; tupleIt != angleRange->end(); tupleIt++ ) {
                double startAngle = *tupleIt;
                
                // jump to next value, because we have/need two values
                tupleIt++;
                
                double endAngle = *tupleIt;
                double result = 0.0;

                printf( "::::::::::::::::: range = %d - %d\n", startAngle, endAngle );

                // calculate
                for( double i = startAngle; i <= endAngle; i += t_precision ) {
                    
                    // a bissl rumgespielt ;-)

                    result = ( y - cc->center().y() * cos( i ) ) + ( x - cc->center().x() * sin( i ) );

                    // print some values ( for debuging )
                    printf( "x = %d, y = %d, theta = %6.3f precision = %6.3f result = %10.6f\n", x, y, i, t_precision, result );

                    if( ( result > 0 ) && ( i <= houghY ) )
                        image->set( Point( i, result ), 50 );
                }
            }
            // till now we want only calculate for one cc
            break;
        }
        
        return image;
    }
}
#endif

