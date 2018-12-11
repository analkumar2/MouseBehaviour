#!/usr/bin/env python
"""protocol_to_config.py: 

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
import csv

sdir_ = os.path.dirname(os.path.realpath(__file__ ))

def main():
    protoFile = os.path.join( sdir_, './BehaviourProtocols.csv' )
    protocols = {}
    with open(protoFile, 'r') as f:
        csvdict = csv.DictReader(f)
        for row in csvdict:
            protocols[row['CODE']] = row
    whichProtocol = sys.argv[1]
    if whichProtocol not in protocols:
        print( "Protocol '%s' is not available." % whichProtocol )
        print( "| Available protcols are: %s" % str(protcols.keys()))
        return False

    protocol = protocols[whichProtocol]
    for k, v in protocol.items():
        k = k.replace( '-', '_' )
        k = k.replace( ' ', '_' )
        print( '#define _%s      %s' % (k,v))
    return True

if __name__ == '__main__':
    main()
