#ifndef dia-tss_text_string_sep
#define dia-tss_text_string_sep

#include "gamera.hpp"

namespace Gamera {

  /* This is a very simple plugin that simply fills the image with white

     See the Gamera plugin documentation for more information on how to
     write Gamera plugins.
   */
    template<class T>
    float textStringSep(T& image) {
//    std::fill(image.vec_begin(), image.vec_end(), white(image));
        return 0;
    }
}

#endif
