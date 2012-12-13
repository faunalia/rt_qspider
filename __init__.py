# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : RT QSpider
Description          : Convert a table to an event layer or a spider diagram
Date                 : Nov 14, 2012 
copyright            : (C) 2012 by Giuseppe Sucameli (Faunalia)
email                : brush.tyler@gmail.com

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

def name():
    return "RT QSpider"

def description():
    return "Convert the selected table to an event layer (based on an X,Y pair) or to a spider diagram (based on two X,Y pairs)"

def version():
    return "0.3"

def qgisMinimumVersion():
    return "1.6.0"

def author():
    return "Giuseppe Sucameli (Faunalia)"

def authorName():
    return author()

def email():
    return "sucameli@faunalia.it"

def icon():
    return "icons/logo.png"

def classFactory(iface):
    from .plugin import RTQSpiderPlugin
    return RTQSpiderPlugin(iface)
