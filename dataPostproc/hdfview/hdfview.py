from math import ceil
from dataPostproc.abcH5 import abcH5
from pathlib import Path
from xml.dom import minidom
from xml.etree import ElementTree as ET

class hdfView(abcH5):
    def __init__(self, **kwargs):
        '''
        hdfView: View the HDF5 file through Paraview.
        -- Input:
            _fn:   The HDF5 File.
            _list: The variables you want to plot.
            _blockx: The Block in the x-direction. [Start, Step, End]
            _blocky: The Block in the y-direction. [Start, Step, End]
            _blockz: The Block in the z-direction. [Start, Step, End]
        -- Function:
            _output(_fn): Output the xdmf file for plot.
        '''
        super(hdfView, self).__init__(**kwargs)
        if self._blockx is None:
            self._blockx = [0, 1, self._sx]
        else:
            if len(self._blockx) != 3:
                raise Exception('ERROR: The length of blockx should be 3!')
        if self._blocky is None:
            self._blocky = [0, 1, self._sy]
        else:
            if len(self._blocky) != 3:
                raise Exception('ERROR: The length of blocky should be 3!')
        if self._blockz is None:
            self._blockz = [0, 1, self._sz]
        else:
            if len(self._blockz) != 3:
                raise Exception('ERROR: The length of blockz should be 3!')

    def _output(self, _fn):
        if '.xdmf' not in _fn:
            _fn += '.xdmf'

        _hyperx       = int((self._blockx[2] - self._blockx[0])/self._blockx[1])
        _hypery       = int((self._blocky[2] - self._blocky[0])/self._blocky[1])
        _hyperz       = int((self._blockz[2] - self._blockz[0])/self._blockz[1])

        def _dumpItem(_moo, **kwargs):
            if 'text' in kwargs.keys():
                text = kwargs.pop('text')
            else:
                text = None
            _ret      = ET.SubElement(_moo, 'DataItem', **kwargs)
            _ret.text = text
            return _ret

        def _dumpGeo(_moo):
            _ret = ET.SubElement(_moo, 'Geometry', GeometryType='VXVYVZ')
            _hyper = _dumpItem(_ret, 
                    ItemType='HyperSlab',
                    Dimensions='%i'%_hyperx
                    )
            _dumpItem(_hyper,
                    text = ''' 
                    {} 
                    {}
                    {}'''.format(
                    self._blockx[0],
                    self._blockx[1],
                    _hyperx),
                    Dimensions='3 1',
                    Format = 'XML'
                    )
            _dumpItem(_hyper,
                    text= str(self._fn)+':/'+self._varx,
                    Dimensions=str(self._sx),
                    Precision="8",
                    Format="HDF"
                    )
            _hyper = _dumpItem(_ret, 
                    ItemType='HyperSlab',
                    Dimensions='%i'%_hypery
                    )
            _dumpItem(_hyper,
                    text = ''' 
                    {} 
                    {}
                    {}'''.format(
                    self._blocky[0],
                    self._blocky[1],
                    _hypery),
                    Dimensions='3 1',
                    Format = 'XML'
                    )
            _dumpItem(_hyper,
                    text= str(self._fn)+':/'+self._vary,
                    Dimensions=str(self._sy),
                    Precision="8",
                    Format="HDF"
                    )
            _hyper = _dumpItem(_ret, 
                    ItemType='HyperSlab',
                    Dimensions='%i'%_hyperz
                    )
            _dumpItem(_hyper,
                    text = ''' 
                    {} 
                    {}
                    {}'''.format(
                    self._blockz[0],
                    self._blockz[1],
                    _hyperz),
                    Dimensions='3 1',
                    Format = 'XML'
                    )
            _dumpItem(_hyper,
                    text= str(self._fn)+':/'+self._varz,
                    Dimensions=str(self._sz),
                    Precision="8",
                    Format="HDF"
                    )
            return _ret

        def _dumpAttr(_moo, _var):
            _ret = ET.SubElement(_moo, "Attribute", Name=_var, AttributeType="Scalar", Center="Node")
            _shape        = self._file[_var].shape
            _blockx       = self._blockx[:]
            _blockx[0]   += self._per[_var][1]
            _blocky       = self._blocky[:]
            _blocky[0]   += self._per[_var][0]
            _hyper = _dumpItem(_ret, ItemType="HyperSlab", Dimensions="{} {} {}".format(_hyperz, _hypery, _hyperx))
            _dumpItem(_hyper,
                    text = ''' 
                    {} {} {} 
                    {} {} {}
                    {} {} {}'''.format(
                    self._blockz[0], _blocky[0], _blockx[0],
                    self._blockz[1], _blocky[1], _blockx[1],
                    _hyperz, _hypery, _hyperx),
                    Dimensions = '3 3',
                    Format = "XML")
            _dumpItem(_hyper,
                    text = str(self._fn) + ':/' + _var,
                    Dimensions = '{} {} {}'.format(_shape[0], _shape[1], _shape[2]),
                    Precision = '8',
                    Format = "HDF")
            return _ret

        # Output the Xdmf file
        _fn = Path(_fn).resolve().expanduser()
        # Start to generate the file
        _root   = ET.Element('Xdmf', Version="2.0")
        _domain = ET.SubElement(_root, 'Domain')
        _grid   = ET.SubElement(_domain, 'Grid', Name="Structured Grid", GridType="Uniform")
        # Topology
        ET.SubElement(_grid,
           "Topology",
           TopologyType="3DRectMesh",
           NumberOfElements="{} {} {}".format(_hyperz, _hypery, _hyperx)
           )
        # Geometry
        _dumpGeo(_grid)
        # Attribute
        for _item in self._list:
            _dumpAttr(_grid, _item)

        _tree = ET.ElementTree(_root)
        ET.indent(_tree, space='  ', level=0)
        _tree.write(_fn)
