#!/usr/bin/python

#Copyright (c) 2016, Joshua Lansford @ LaserLinc
#All rights reserved.

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:

#1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import with_statement
from collections import defaultdict

import sys
import cgi

STATE_PASSING_1ST = 0
STATE_PASSING_2ND = 1
STATE_MATCH = 2


class lineCompIndex:
    errorCount = 0
    previouse = None
    state = STATE_PASSING_1ST
    #isMatch = False
    #isPassing2nd = False
    content = ""
    

def main( argv ):
    if( len( argv ) < 3 ):
        print "Usage: JDiff file1 file2 resultFile"
        exit

    filename1 = argv[0]
    filename2 = argv[1]
    output =    argv[2]

    with open( filename1, 'r' ) as fileHandle1:
        with open( filename2, 'r' ) as fileHandle2:
            file1 = fileHandle1.read()
            file2 = fileHandle2.read()

            lastLine = []
            thisLine = []

            #init the root root
            thisIndex = lineCompIndex()
            thisIndex.state = STATE_MATCH
            thisLine.append( thisIndex );

            #init the root top case
            columnIndex = 1
            for char2 in file2:
                thisIndex = lineCompIndex()
                thisIndex.previouse = thisLine[ columnIndex-1 ]
                thisIndex.errorCount = thisIndex.previouse.errorCount+1
                thisIndex.content = char2
                thisIndex.state = STATE_PASSING_2ND
                thisLine.append( thisIndex )
                columnIndex += 1
                
            for char1 in file1:
                lastLine = thisLine
                thisLine = []

                sys.stdout.write( char1 )

                #init the root left case
                thisIndex = lineCompIndex()
                thisIndex.previouse = lastLine[ 0 ]
                thisIndex.errorCount = thisIndex.previouse.errorCount+1
                thisIndex.content = char1
                thisIndex.state = STATE_PASSING_1ST
                thisLine.append( thisIndex )

                columnIndex = 1
                for char2 in file2:
                    thisIndex = lineCompIndex()
        
                    if( char2 == char1 ):
                        thisIndex.previouse = lastLine[ columnIndex-1 ]
                        #To keep from getting speriouse single matches,
                        #see about adding some error in for the first matches.
                        if thisIndex.previouse.state == STATE_MATCH:
                            thisIndex.errorCount = thisIndex.previouse.errorCount
                        else:
                            thisIndex.errorCount = thisIndex.previouse.errorCount #+ 1
                    
                        thisIndex.state = STATE_MATCH
                        thisIndex.content = char2
                    else:
                        if lastLine[ columnIndex ].errorCount < thisLine[ columnIndex-1 ].errorCount:
                            thisIndex.previouse = lastLine[ columnIndex ]
                            thisIndex.content = char1
                            thisIndex.state = STATE_PASSING_1ST
                        else:
                            thisIndex.previouse = thisLine[ columnIndex-1 ]
                            thisIndex.content = char2
                            thisIndex.state = STATE_PASSING_2ND
                            
                        thisIndex.errorCount = thisIndex.previouse.errorCount+1

                    thisLine.append( thisIndex )
                    columnIndex += 1


    def printDiffs( nodesToPrint, outputFile ):
        isblack = True
        isred = False
        isgreen = False

        def escape( inputStr ):
            answer = ""
            if inputStr == " ":
                answer = "&nbsp;"
            elif inputStr == "\t":
                answer = "&nbsp;&nbsp;&nbsp;"
            else:
                answer = cgi.escape( inputStr )
            return answer

        
        for nodeToPrint in nodesToPrint:
            if nodeToPrint.content == "\n":
                outputFile.write( "<br>\n" )
            else:
                if(nodeToPrint.state == STATE_MATCH):
                    if not isblack:
                        outputFile.write( "</font>" )
                        isblack = True
                        isred = False
                        isgreen = False
                elif(nodeToPrint.state == STATE_PASSING_2ND ):
                    if not isred:
                        if not isblack:
                            outputFile.write( "</font>" )
                        outputFile.write( "<font size='5' color='green'>" )
                        isblack = False
                        isred = True
                        isgreen = False
                else:
                    if not isgreen:
                        if not isblack:
                            outputFile.write( "</font>" )
                        outputFile.write( "<font size='5' color='red'>" )
                        isblack = False
                        isred = False
                        isgreen = True

                outputFile.write( escape( nodeToPrint.content ) )
                
        if not isblack:
            outputFile.write( "</font>" )
            isblack = True
            isred = False
            isgreen = False

    backwardsList = []
    currentNode = thisLine[ len( thisLine )-1 ]
    while not currentNode is None:
        backwardsList.append( currentNode )
        currentNode = currentNode.previouse
            
    with open( output, 'w' ) as outFile:
        outFile.write( "<html><head><title>diff of " + filename1 + " and " + filename2 + "</title></head>\n" );
        outFile.write( "<body>\n" );

        backwardsList.reverse()
        printDiffs( backwardsList, outFile )

        outFile.write( "</body>\n" );
        outFile.write( "</html>\n" );
        
                

if __name__ == "__main__":
    main(sys.argv[1:])
