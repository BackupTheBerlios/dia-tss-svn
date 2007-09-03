#   Copyright (C) 2006  Daniel Esser, Oliver Kriehn
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

#ifndef dia-tss_text_string_sep
#define dia-tss_text_string_sep

#include "gamera.hpp"

namespace Gamera {

    /*
     * This implements the Gamera plugin for Text-String-Separation.
     *
     * See the Gamera plugin documentation for more information on how
     * to use this plugin.
     *
     * See the Gamera plugin documentation for more information on how to
     * write Gamera plugins.
    */

    template<class T>
    float textStringSep(T& image) {
        // std::fill(image.vec_begin(), image.vec_end(), white(image));
        return 0;
    }
}

#endif
