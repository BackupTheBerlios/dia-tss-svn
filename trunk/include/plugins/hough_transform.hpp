#ifndef INC_HOUGH_TRANSFORM
#define INC_HOUGH_TRANSFORM

#include "gamera.hpp"

namespace Gamera {

    Image* hough_transform( ImageVector &imgVec, FloatVector *angleRange, int r, float t_precision, int orgX, int orgY ) {
        typedef TypeIdImageFactory<FLOAT, DENSE> fact_type;
        ImageVector::iterator it = imgVec.begin();

        int resolution = (int)( 360 / t_precision );
        
        int x = 0,
            y = 0;

        // size for the hough-domain
        int houghX = 360,
            houghY = orgY;//(int)sqrt( ( orgX / 2 ) * ( orgX / 2 ) + ( orgY / 2 ) * ( orgY / 2 ) );

        
        fact_type::image_type *image = fact_type::create( Point( 0, 0 ), Dim( houghX + 1, orgY + 1 ) );
        image->resolution( resolution );
       
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
                
                double rTheta = 0.0; // theta in radian
                int r = 0;

                // calculate
                for( double theta = startAngle; theta <= endAngle; theta += t_precision ) {

                    // convert degree in radian
                    rTheta = ( theta * M_PI ) / 180.0;
                    r = (int)( y - cc->center().y() * cos( rTheta ) ) + ( x - cc->center().x() * sin( rTheta ) );

                    // print some values ( for debuging )
                    printf( "x = %d, y = %d, theta = %6.3f precision = %6.3f result = %d\n", x, y, theta, t_precision, r );

                    if( ( r > 0 ) && ( r <= houghY ) ) {
                        float pixelValue = image->get( Point( theta, r ) );
                        image->set( Point( theta, r ), ( pixelValue + 10 ) );
                    }
                }
            }
        }
        
        return image;
    }
}
#endif

