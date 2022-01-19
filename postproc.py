#!/usr/bin/python

import sys
from dataPostproc.output import outputData, outputData_tke
from argparse import ArgumentParser as ap

def main():
    dataPostproc  = ap(prog='dataPostproc', description='API of fileEx')
    _subparses    = dataPostproc.add_subparsers(help='sub-command help')
    #-----------------------------------------#
    #------------- Output Method -------------#
    #-----------------------------------------#
    _output       = _subparses.add_parser('output', help='Add new file in the document.')
    _output.add_argument(
                '-f', '--file',
                required = True,
                help = 'Add the path of the file.(In TKE that will be prefix)',
                metavar = 'Filename'
            )
    _output.add_argument(
                '-d', '--dire',
                required = True,
                help = 'The direction of the postprocess.',
                metavar = 'Direction'
            )
    _output.add_argument(
                '-o', '--output',                # Option Name
                required = False,                # Requirement
                help = 'The output file',        # Help log
                metavar = 'Filename'             # [-f filename]
            )
    _output.add_argument(
                '-v', '--variables',
                action='extend',               # Action of option
                nargs='+',                     # N args
                help='The variables list to output',
                metavar='Variables'
            )
    _output.add_argument(
                '-n', '--normalize',
                action='store_true',            
                default=False,
                help='Open normalization',
            )
    _output.add_argument(
                '-t', '--tke',
                action='store_true',            
                default=False,
                help='Calculate the TKE.',
            )
    _output.add_argument(
                '-x', '--blockx',
                action='extend',            
                nargs=4,                     
                help='Select hyberslab of in x-direction(start, stride, count, block).',
                type=int,
                metavar='Int'
            )
    _output.add_argument(
                '-y', '--blocky',
                action='extend',            
                nargs=4,                     
                help='Select hyberslab of in y-direction(start, stride, count, block).',
                type=int,
                metavar='Int'
            )
    _output.add_argument(
                '-z', '--blockz',
                action='extend',            
                nargs=4,                     
                help='Select hyberslab of in z-direction(start, stride, count, block).',
                type=int,
                metavar='Int'
            )
    _main_args   = dataPostproc.parse_args() 
    # Start the code
    if 'output' in sys.argv:
        _prefix  = _main_args.file
        _of      = _main_args.output
        _varlist = _main_args.variables
        _dire    = _main_args.dire
        _blockx  = _main_args.blockx
        _blocky  = _main_args.blocky
        _blockz  = _main_args.blockz
        if _main_args.tke:
            for _var in _varlist:
                _filename = _prefix + '_' + _var + '.h5'
                _op = outputData_tke(_fn = _filename, _dire = _dire, _var = _var, _blockz = _blockz, _blocky = _blocky, _blockx = _blockx)
                if _main_args.normalize:
                    _op.normalize()
                _sop = _op.outputTke_all()
                _op._output(_of+'_'+_var+'.dat')
                _sop._output(_of+'_all_'+_var+'.dat')
        else:
            _op = outputData(_fn=_prefix, _dire=_dire, _list=_varlist, _blockz = _blockz, _blocky = _blocky, _blockx = _blockx)
            if _main_args.normalize:
                _op.normalize()
            _op._output(_of)

if __name__ == '__main__':
    main()
