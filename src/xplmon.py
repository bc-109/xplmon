#!/usr/bin/python
# -*- coding: UTF-8 -*-

#===============================================================================
# C.A.S.A. - Corsican Automation Systems & Applications
# (c) 2011 by Toussaint OTTAVI, bc-109 Soft (t.ottavi@bc-109.com)
#===============================================================================
#
#   xplmon : simple XPL monitor based on Twisted
#   Connects to a XPL hub, and displays every XPL message going through.
#   Uses my xpllib library.
#
#===============================================================================
#
#    This is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#===============================================================================


#===============================================================================
# Version numbering 
#===============================================================================

Version = "1.0"
VersionDate = "03/01/2016"

# History :
# - v1.0 : First public version 


#===============================================================================
# Imports 
#===============================================================================

print "Importing modules..."

import sys, signal, traceback

import xpllib

from twisted.internet.error import CannotListenError
from twisted.internet import reactor


################################################################################
#                                                                              #
#                             DERIVED XPL CLASS                                #
#                                                                              # 
################################################################################

#===============================================================================
# XPL Monitor class (derived from XPL handler class)
# This is a derived class for monitoring XPL traffic
#===============================================================================
 
class cXPLMonitorHandler(xpllib.cXPLHandler):
 
  #--------------------------------------------------------------- Constructor 
   
  def __init__(self):
    
    # Call parent class init
    
    xpllib.cXPLHandler.__init__(self) 
    
    # Specific inits 
    
    self.vendor = 'casa'
    self.device = 'monitor'
    self.instance = xpllib.GenerateRandomIdentifier()
    self.source = xpllib.XPLFormatSource(self.vendor, self.device, self.instance)


  #-------------------------------------------- Creating UDP connection (overloaded)
    
  def CreateUDPConnection(self, interface, port):
    self.ProtocolHandler = cXPLMonitorProtocol(interface=interface, parent=self)
    reactor.listenUDP(port, self.ProtocolHandler, interface=interface)


#===============================================================================
# XPL monitor protocol class (derived from XPL Protocol class)
# Handles incoming XPL messages arriving via UDP
#===============================================================================
 
class cXPLMonitorProtocol(xpllib.cXPLProtocol):
 
  #--------------------------------------------------------------- Constructor
    
  def __init__(self, interface, parent):
         
    xpllib.cXPLProtocol.__init__(self, interface, parent)
    self.HandleMessage = self.Monitor 
  

  #----------------------------- Specific handler for processing received messages
     
  def Monitor(self, msg, address):
  
    # Print message on two lines witn ANSI colors
      
    print DisplayTwoLinesColor(msg)  
    print    


################################################################################
#                                                                              #
#                             DISPLAY PROCEDURES                               #
#                                                                              # 
################################################################################

#===============================================================================
# ANSI Color definitions 
#===============================================================================

# Reset
ANSI_reset="\033[0;39;49m"

# colours bold / bright
ANSI_black="\033[01;30m"    #: Black and bold.
ANSI_red="\033[01;31m"      #: Red and bold.
ANSI_green="\033[01;32m"    #: Green and bold.
ANSI_yellow="\033[01;33m"   #: Yellow and bold.
ANSI_blue="\033[01;34m"     #: Blue and bold.
ANSI_magenta="\033[01;35m"  #: Magenta and bold.
ANSI_cyan="\033[01;36m"     #: Cyan and bold.
ANSI_white="\033[01;37m"    #: White and bold.

# colors not bold/brignt 
ANSI_darkblack="\033[0;39;49m\033[02;30m"   #: Black and not bold.
ANSI_darkred="\033[0;39;49m\033[02;31m"     #: Red and not bold.
ANSI_darkgreen="\033[0;39;49m\033[02;32m"   #: Green and not bold.
ANSI_darkyellow="\033[0;39;49m\033[02;33m"  #: Yellow and not bold.
ANSI_darkblue="\033[0;39;49m\033[02;34m"    #: Blue and not bold.
ANSI_darkmagenta="\033[0;39;49m\033[02;35m" #: Magenta and not bold.
ANSI_darkcyan="\033[0;39;49m\033[02;36m"    #: Cyan and not bold.
ANSI_darkwhite="\033[0;39;49m\033[02;37m"   #: White and not bold.

# Background colors : not very useful
ANSI_Black="\033[40m"    #: Black background
ANSI_Red="\033[41m"      #: Red background
ANSI_Green="\033[42m"    #: Green background
ANSI_Yellow="\033[43m"   #: Yellow background
ANSI_Blue="\033[44m"     #: Blue background
ANSI_Magenta="\033[45m"  #: Magenta background
ANSI_Cyan="\033[46m"     #: Cyan background
ANSI_White="\033[47m"    #: White background


#==============================================================================
# Print message on two lines with ANSI colors
#==============================================================================

def DisplayTwoLinesColor (msg):
  
  rst = ANSI_darkwhite          # Default color
  s = ''
  try:                                                  
    
    # message type
    
    if msg.message_type == "cmnd":
      col = ANSI_red
    elif msg.message_type == "stat":
      col = ANSI_green
    elif msg.message_type == "trig":
      col = ANSI_magenta
    else :
      col = '' 
    tmp = rst + '[' + col + "xpl-" + msg.message_type + rst + '] '
    s = s + tmp
    
    # Source, Target
    
    col = ANSI_white
    tmp = "[source=" + col + msg.source + rst + '] > [target=' + col + msg.target + rst + '] '
    s = s + tmp  
      
    # Schema.class

    if msg.schema_class == "hbeat":   
      col = ANSI_darkcyan
      colbody = ANSI_darkblue
    else:
      col = ANSI_cyan
      colbody = ANSI_blue        
    tmp = col + msg.schema_class + '.' + msg.schema_type + rst + '\n'
    s = s + tmp
    
    # Body, status
 
    tmpbody = "" 
    for key, value in msg.body_itemdict.items():
      if tmpbody<>"" : tmpbody = tmpbody +"; "
      tmpbody = tmpbody + "%s=%s" % (key,value)
    body =  ' ' + colbody + tmpbody + rst + " (%s)" % msg.status
    s = s + body
         
  except:
    s = s + ANSI_red + "<Error formatting message for display>" + rst
  
  return s 


################################################################################
#                                                                              #
#                                MAIN PROGRAM                                  #
#                                                                              # 
################################################################################


#===============================================================================
# Startup 
#===============================================================================

try:
  
  # Initialize XPL handler
  
  xplmon = cXPLMonitorHandler() 
  
  # Prepare tasks for Reactor loop 
  
  print('XPL monitor starting on port %d' % xplmon.port)    
  xplmon()
  
  # Main Reactor loop
    
  reactor.run()
  
  # End
  
  print "Program terminated."
      
      
#=============================================================================== 
# Exceptions 
#===============================================================================

except CannotListenError, exc:
  msg = 'Exception : Port %d is already in use' % xplmon.port
  print (msg)    
      
except:
  exc_type, exc_value, exc_traceback = sys.exc_info()
  msg = "Exception : %s" % (exc_value) 
  trace = traceback.format_tb(exc_traceback)
  print (msg)
  print (trace)     





