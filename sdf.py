#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, struct
import numpy as np


idLen = 32  # Max length of ID strings in SDF.
stringLen = 64  # Max length of strings in SDF.


# ***
# The mesh associated with a variable is always node-centred, ie. the values
# written as mesh data specify the nodal values of a grid. Variables may be
# defined at points which are offset from this grid due to grid staggering in
# the code. The "stagger" entry specifies where the variable is defined
# relative to the mesh. Since we have already defined the number of points
# that the associated mesh contains, this determines how many points are required
# to display the variable. The entry is represented by a bit-mask where each
# bit corresponds to a shift in coordinates by half a grid cell in the direction
# given by the bit position. Therefore the value "1" (or "0001" in binary)
# is a shift by \e dx/2 in the \e x direction, "2" (or "0010" in binary) is
# a shift by \e dy/2 in the \e y direction and "4" (or "0100" in binary) is
# a shift by \e dz/2 in the \e z direction. These can be combined to give shifts
# in more than one direction. The system can also be extended to account for
# more than three directions (eg. "8" for direction 4).
# 
# For convenience, a list of pre-defined constants are defined for the typical
# cases.
# ***
SDF_STAGGER = [
    # * Cell centred. At the midpoint between nodes.
    # * Implies an <em>(nx,ny,nz)</em> grid. */
    'SDF_STAGGER_CELL_CENTRE',
    # * Face centred in X. Located at the midpoint between nodes on the Y-Z
    # * plane.
    # * Implies an <em>(nx+1,ny,nz)</em> grid. */
    'SDF_STAGGER_FACE_X',
    # * Face centred in Y. Located at the midpoint between nodes on the X-Z
    # * plane.
    # * Implies an <em>(nx,ny+1,nz)</em> grid. */
    'SDF_STAGGER_FACE_Y',
    # * Face centred in Z. Located at the midpoint between nodes on the X-Y
    # * plane.
    # * Implies an <em>(nx,ny,nz+1)</em> grid. */
    'SDF_STAGGER_EDGE_Z',
    # * Edge centred along X. Located at the midpoint between nodes along the
    # * X-axis.
    # * Implies an <em>(nx,ny+1,nz+1)</em> grid. */
    'SDF_STAGGER_FACE_Z',
    # * Edge centred along Y. Located at the midpoint between nodes along the
    # * Y-axis.
    # * Implies an <em>(nx+1,ny,nz+1)</em> grid. */
    'SDF_STAGGER_EDGE_Y',
    # * Edge centred along Z. Located at the midpoint between nodes along the
    # * Z-axis.
    # * Implies an <em>(nx+1,ny+1,nz)</em> grid. */
    'SDF_STAGGER_EDGE_X',
    # * Node centred. At the same place as the mesh.
    # * Implies an <em>(nx+1,ny+1,nz+1)</em> grid. */
    'SDF_STAGGER_VERTEX'
]


SDF_DIMENSION = [
    'SDF_DIMENSION_IRRELEVANT',
    'SDF_DIMENSION_1D',
    'SDF_DIMENSION_2D',
    'SDF_DIMENSION_3D'
]


# The "geometry_type" specifies the geometry of the current block and it can
# take one of the following values:
SDF_GEOMETRY = [
    'SDF_GEOMETRY_NULL',        # *< Unspecified geometry. This is an error. */
    'SDF_GEOMETRY_CARTESIAN',   # *< Cartesian geometry. */
    'SDF_GEOMETRY_CYLINDRICAL', # *< Cylindrical geometry. */
    'SDF_GEOMETRY_SPHERICAL'    # *< Spherical geometry. */
]


SDF_DATATYPE  = [
    'SDF_DATATYPE_NULL',     # *< No datatype specified. This is an error. */
    'SDF_DATATYPE_INTEGER4', # *< 4-byte integers. */
    'SDF_DATATYPE_INTEGER8', # *< 8-byte integers. */
    'SDF_DATATYPE_REAL4',    # *< 4-byte floating point (ie. single precision). */
    'SDF_DATATYPE_REAL8',    # *< 8-byte floating point (ie. double precision). */
    'SDF_DATATYPE_REAL16',   # *< 16-byte floating point (ie. quad precision). */
    'SDF_DATATYPE_CHARACTER',# *< 1-byte characters. */
    'SDF_DATATYPE_LOGICAL',  # *< Logical variables. (Represented as 1-byte
                             # *  characters */
    'SDF_DATATYPE_OTHER'     # *< Unspecified datatype. The type of data in the
                             # *  block must be inferred from the block type. */
]


SDF_TYPE_FOR_NUMPY = (
    None,           #  SDF_DATATYPE_NULL = 0,
    np.int32,    #  SDF_DATATYPE_INTEGER4,
    np.int64,    #  SDF_DATATYPE_INTEGER8,
    np.float32,  #  SDF_DATATYPE_REAL4,
    np.float64,  #  SDF_DATATYPE_REAL8,
    None,           #  SDF_DATATYPE_REAL16,
    None,           #  SDF_DATATYPE_CHARACTER,
    None,           #  SDF_DATATYPE_LOGICAL,
    None            #  SDF_DATATYPE_OTHER,
)


SDF_TYPE_FOR_STRUCT = (
    None,   #  SDF_DATATYPE_NULL = 0,
    'i',    #  SDF_DATATYPE_INTEGER4,
    'q',    #  SDF_DATATYPE_INTEGER8,
    'f',    #  SDF_DATATYPE_REAL4,
    'd',    #  SDF_DATATYPE_REAL8,
    None,   #  SDF_DATATYPE_REAL16,
    'c',    #  SDF_DATATYPE_CHARACTER,
    None,   #  SDF_DATATYPE_LOGICAL,
    None    #  SDF_DATATYPE_OTHER,
)


SDF_TYPE_SIZES = (
    0,  #  SDF_DATATYPE_NULL = 0,
    4,  #  SDF_DATATYPE_INTEGER4,
    8,  #  SDF_DATATYPE_INTEGER8,
    4,  #  SDF_DATATYPE_REAL4,
    8,  #  SDF_DATATYPE_REAL8,
    16, #  SDF_DATATYPE_REAL16,
    1,  #  SDF_DATATYPE_CHARACTER,
    1,  #  SDF_DATATYPE_LOGICAL,
    0   #  SDF_DATATYPE_OTHER,
)


# 31 types
SDF_BLOCKTYPE = [
    # * Unknown block type. This is an error. */
    'SDF_BLOCKTYPE_NULL',
    # * Block describing a plain mesh or grid. */
    'SDF_BLOCKTYPE_PLAIN_MESH',
    # * Block describing a point mesh or grid. */
    'SDF_BLOCKTYPE_POINT_MESH',
    # * Block describing a variable on a plain mesh. */
    'SDF_BLOCKTYPE_PLAIN_VARIABLE',
    # * Block describing a variable on a point mesh. */
    'SDF_BLOCKTYPE_POINT_VARIABLE',
    # * A simple constant not associated with a grid. */
    'SDF_BLOCKTYPE_CONSTANT',
    # * A simple array not associated with a grid. */
    'SDF_BLOCKTYPE_ARRAY',
    # * Information about the simulation. */
    'SDF_BLOCKTYPE_RUN_INFO',
    # * Embedded source code block. */
    'SDF_BLOCKTYPE_SOURCE',
    # * List of blocks to combine as a tensor or vector. */
    'SDF_BLOCKTYPE_STITCHED_TENSOR',
    # * List of blocks to combine as a multi-material mesh. */
    'SDF_BLOCKTYPE_STITCHED_MATERIAL',
    # * List of blocks to combine as a multi-material variable. */
    'SDF_BLOCKTYPE_STITCHED_MATVAR',
    # * List of blocks to combine as a species mesh. This is similar to a
    # * multi-material mesh except there is no interface in a mixed cell. */
    'SDF_BLOCKTYPE_STITCHED_SPECIES',
    # * Information about a particle species. */
    'SDF_BLOCKTYPE_SPECIES',
    # * This blocktype is never actually written to an SDF file. It is used
    # * within the C-library and VisIt to represent a plain variable whose
    # * content is generated dynamically based on other data in the file. */
    'SDF_BLOCKTYPE_PLAIN_DERIVED',
    # * As above, this blocktype is never actually written to an SDF file. It
    # * serves the same purpose as SDF_BLOCKTYPE_PLAIN_DERIVED, except the
    # * variable is defined on a point mesh. */
    'SDF_BLOCKTYPE_POINT_DERIVED',
    # * This is the same as SDF_BLOCKTYPE_STITCHED_TENSOR, except that all the
    # * data for the stitched variables is contained in the data section of
    # * this block rather than the blocks which are referenced. */
    'SDF_BLOCKTYPE_CONTIGUOUS_TENSOR',
    # * Same as above, for SDF_BLOCKTYPE_STITCHED_MATERIAL */
    'SDF_BLOCKTYPE_CONTIGUOUS_MATERIAL',
    # * Same as above, for SDF_BLOCKTYPE_STITCHED_MATVAR */
    'SDF_BLOCKTYPE_CONTIGUOUS_MATVAR',
    # * Same as above, for SDF_BLOCKTYPE_STITCHED_SPECIES */
    'SDF_BLOCKTYPE_CONTIGUOUS_SPECIES',
    # * Information about the parallel domain decomposition. */
    'SDF_BLOCKTYPE_CPU_SPLIT',
    # * List of blocks to combine as an obstacle mesh. */
    'SDF_BLOCKTYPE_STITCHED_OBSTACLE_GROUP',
    # * Block describing an unstructured mesh or grid. */
    'SDF_BLOCKTYPE_UNSTRUCTURED_MESH',
    # * Block describing a stitched variable.
    # * This allows any arbitrary set of variables to be grouped together. */
    'SDF_BLOCKTYPE_STITCHED',
    # * This is the same as SDF_BLOCKTYPE_STITCHED, except that all the
    # * data for the stitched variables is contained in the data section of
    # * this block rather than the blocks which are referenced. */
    'SDF_BLOCKTYPE_CONTIGUOUS',
    # * Block describing a Lagrangian mesh or grid. */
    'SDF_BLOCKTYPE_LAGRANGIAN_MESH',
    # * Block describing a station point. */
    'SDF_BLOCKTYPE_STATION',
    # * As with SDF_BLOCKTYPE_PLAIN_DERIVED, this blocktype is never actually
    # * written to an SDF file. It serves the same purpose as
    # * SDF_BLOCKTYPE_PLAIN_DERIVED, except the variable is defined as a
    # * station variable. */
    'SDF_BLOCKTYPE_STATION_DERIVED',
    # * Raw data with a checksum. */
    'SDF_BLOCKTYPE_DATABLOCK',
    # * Name/value pairs. */
    'SDF_BLOCKTYPE_NAMEVALUE',

    # * ***********************************/
    # * Deleted block. Should be ignored. */
    'SDF_BLOCKTYPE_SCRUBBED'
]


# --------------------------------------------------
# sdf_block_data
# This is the super class of all data type classes.

class sdf_block_data(object):
    def __init__(self, parentObj, blockInfo):
        self.block = parentObj

        # self.blockInfo contains the content of the info area of a block.
        # It's filled in by subclasses.
        self.blockInfo = {}

        # self.dataInfo collects all useful information about the data area of a block.
        # Part of its content is implemented by subclasses.
        self.dataInfo = {}

        # self.dataInfoShowKeys decides which items of self.dataInfo will be displayed by self.show function.
        # Part of its content is implemented by subclasses.
        self.dataInfoShowKeys = []
        self.dataInfoShowKeys += ['blockName', 'blockID', 'blockTypeName',
                                'dataNumOfDimensions', 'dataTypeName',
                                'FileName', 'time', 'step']

        self.p = self.quickPlot

        self.dataInfo['FileName'] = self.block.FileName
        self.dataInfo['blockIndex'] = self.block.blockIndex
        self.dataInfo['time'] = self.block.sdf.SDFHeader['time']
        self.dataInfo['step'] = self.block.sdf.SDFHeader['step']
        self.dataInfo['dataLocation'] = self.block.blockHeader['dataLocation']
        self.dataInfo['dataLen'] = self.block.blockHeader['dataLen']
        dataType = self.block.blockHeader['dataType']
        self.dataInfo['dataType'] = dataType
        self.dataInfo['dataTypeName'] = SDF_DATATYPE[dataType]
        self.dataInfo['dataTypeSize'] = SDF_TYPE_SIZES[dataType]
        self.dataInfo['dataNumOfDimensions'] = self.block.blockHeader['numberOfDimensions']
        blockType = self.block.blockHeader['blockType']
        self.dataInfo['blockType'] = blockType
        self.dataInfo['blockTypeName'] = SDF_BLOCKTYPE[blockType]
        self.dataInfo['blockID'] = self.block.blockHeader['blockID']
        self.dataInfo['blockName'] = self.block.blockHeader['blockName']

    def __repr__(self):
        return '<Data : %s : %s in %s>' % (self.dataInfo['blockName'], self.dataInfo['blockID'], self.dataInfo['FileName'])

    def __len__(self):
        # How many numbers in the data area. Equals dataLen/dataTypeSize.

        if not self.dataInfo['dataTypeSize'] == 0:
            return self.dataInfo['dataLen'] / self.dataInfo['dataTypeSize']
        else:
            return 0

    def __call__(self):
        return self.get()

    def __getattr__(self, attrName):
        return self.dataInfo[attrName]

    def show(self, full_info = False, full_path = False):
        if not full_info:
            fileName = self.dataInfo['FileName']
            blockIndicator = ''
            if full_path:
                blockIndicator = 'block'
            else:
                fileName = fileName[-8:-4]
            print ('Data: %s : %s : %dD %s : %s ' + blockIndicator + '[%d]') % (
                    self.dataInfo['blockName'],
                    self.dataInfo['blockID'],
                    self.dataInfo['dataNumOfDimensions'],
                    SDF_BLOCKTYPE[self.dataInfo['blockType']][14:],
                    fileName,
                    self.dataInfo['blockIndex'])
        else:
            print ('Data: %d %s:') % (
                    len(self),
                    self.dataInfo['dataTypeName'][13:])
            for dataInfoKey in self.dataInfoShowKeys:
                print dataInfoKey, '=', self.dataInfo[dataInfoKey]

    def reduce_shape(self, shape):
        reshape = []
        for i in shape:
            if not i == 1:
                reshape.append(i)
        if reshape == []:
            reshape = [1]
        return tuple(reshape)

    def retrieveData(self):
        # Retrieve data in the data area of a block from the sdf file.

        dataLen = self.dataInfo['dataLen']
        if dataLen == 0:
            return np.arange(0.)
        dataF = open(self.dataInfo['FileName'])
        dataF.seek(self.dataInfo['dataLocation'])
        dataStr = dataF.read(dataLen)
        dataF.close()
        return np.fromstring(dataStr, dtype = SDF_TYPE_FOR_NUMPY[self.dataInfo['dataType']])

    # Can be rewrite by subclasses.
    def get(self):
        return self.retrieveData()

    # Used by self.quickPlot.
    # Subclasses must rewrite this function if they want to provide quick data visualization.
    def getp(self):
        return []

    def quickPlot(self):
        quickData = self.getp()
        if quickData == []:
            print 'Data cannot be plotted.'
            return
        if self.dataInfo.has_key('quickPlotSpecified'):
            if self.dataInfo['quickPlotSpecified'] == 'points':
                self.pointPlot(quickData)
            else:
                self.plainPlot(quickData)
        else:
            self.plainPlot(quickData)

    def pointPlot(self, quickData):
        numDim = len(quickData)
        if numDim == 1:
            print 'We don\'t deal with 1 dimensional scatter plots for the moment.'
        elif numDim == 2:
            import matplotlib.pyplot as plt

            plt.figure()
            plt.scatter(quickData[0], quickData[1], s = 2, marker = '.', lw = 0)
            plt.xlim(np.min(quickData[0]), np.max(quickData[0]))
            plt.ylim(np.min(quickData[1]), np.max(quickData[1]))
            plt.show()
        elif numDim == 3:
            print 'We don\'t deal with 3 dimensional scatter plots for the moment.'
        else:
            print 'We don\'t deal with high dimensional scatter plots for the moment.'

    def plainPlot(self, quickData):
        numDim = quickData.ndim
        if numDim == 1:
            import matplotlib.pyplot as plt

            plt.figure()
            plt.plot(quickData)
            plt.show()
        elif numDim == 2:
            import matplotlib.pyplot as plt
            from matplotlib import cm

            fig = plt.figure()
            ax = fig.add_subplot(111)
            im = ax.imshow(quickData, cmap = cm.rainbow, origin = 'lower')
            cbar = plt.colorbar(im)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            plt.show()
        elif numDim == 3:
            print 'We don\'t deal with 3 dimensional data for the moment.'
        else:
            print 'We don\'t deal with high dimensional data for the moment.'

# sdf_block_data
# --------------------------------------------------


# Data object abstracts the data area of a block.
# Data object do the following job:
# 1. fill in self.blockInfo in class constructor.
# 2. implement self.dataInfo in class constructor.
# 3. implement self.dataInfoShowKeys in class constructor.
# 4. rewrite self.get() when necessary.
# 5. rewrite self.getp() when necessary.

class SDF_BLOCK_null(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_plain_mesh(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

        ndims = self.dataInfo['dataNumOfDimensions']
        self.blockInfo['mults'] = struct.unpack('d' * ndims, blockInfo[0:(8 * ndims)])
        blockInfo = blockInfo[(8 * ndims):]
        self.blockInfo['labels'] = []
        for i in range(ndims):
            self.blockInfo['labels'].append(blockInfo[0:32].strip())
            blockInfo = blockInfo[32:]
        self.blockInfo['units'] = []
        for i in range(ndims):
            self.blockInfo['units'].append(blockInfo[0:32].strip())
            blockInfo = blockInfo[32:]
        self.blockInfo['geometry'] = (struct.unpack('i', blockInfo[0:4]))[0]
        blockInfo = blockInfo[4:]
        self.blockInfo['minVal'] = struct.unpack('d' * ndims, blockInfo[0:(8 * ndims)])
        blockInfo = blockInfo[(8 * ndims):]
        self.blockInfo['maxVal'] = struct.unpack('d' * ndims, blockInfo[0:(8 * ndims)])
        blockInfo = blockInfo[(8 * ndims):]
        self.blockInfo['dims'] = struct.unpack('i' * ndims, blockInfo)

        self.dataInfo['geometry'] = self.blockInfo['geometry']
        self.dataInfo['geometryName'] = SDF_GEOMETRY[self.blockInfo['geometry']]

        self.dataInfo['units'] = self.blockInfo['units']
        self.dataInfo['labels'] = self.blockInfo['labels']
        self.dataInfo['dims'] = self.blockInfo['dims']
        self.dataInfo['minVal'] = self.blockInfo['minVal']
        self.dataInfo['maxVal'] = self.blockInfo['maxVal']

        # data_mesh_order describes the order in which each dimesion of the mesh is represented
        self.dataInfo['data_mesh_order'] = '[x, y, z]'

        self.dataInfoShowKeys += ['units', 'labels', 'dims', 'minVal', 'maxVal', 'data_mesh_order']

    def get(self):
        data = self.retrieveData()
        dataInDim = []
        for dim in self.dataInfo['dims']:
            dataInDim.append(data[:dim])
            data = data[dim:]
        return dataInDim

class SDF_BLOCK_point_mesh(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

        ndims = self.dataInfo['dataNumOfDimensions']
        self.blockInfo['mults'] = struct.unpack('d' * ndims, blockInfo[0:(8 * ndims)])
        blockInfo = blockInfo[(8 * ndims):]
        self.blockInfo['labels'] = []
        for i in range(ndims):
            self.blockInfo['labels'].append(blockInfo[0:32].strip())
            blockInfo = blockInfo[32:]
        self.blockInfo['units'] = []
        for i in range(ndims):
            self.blockInfo['units'].append(blockInfo[0:32].strip())
            blockInfo = blockInfo[32:]
        self.blockInfo['geometry'] = (struct.unpack('i', blockInfo[0:4]))[0]
        blockInfo = blockInfo[4:]
        self.blockInfo['minVal'] = struct.unpack('d' * ndims, blockInfo[0:(8 * ndims)])
        blockInfo = blockInfo[(8 * ndims):]
        self.blockInfo['maxVal'] = struct.unpack('d' * ndims, blockInfo[0:(8 * ndims)])
        blockInfo = blockInfo[(8 * ndims):]
        self.blockInfo['numberOfPoints'] = (struct.unpack('q', blockInfo[0:8]))[0]
        self.blockInfo['speciesID'] = blockInfo[8:].strip()

        self.dataInfo['geometry'] = self.blockInfo['geometry']
        self.dataInfo['geometryName'] = SDF_GEOMETRY[self.blockInfo['geometry']]

        self.dataInfo['units'] = self.blockInfo['units']
        self.dataInfo['labels'] = self.blockInfo['labels']
        self.dataInfo['numberOfPoints'] = self.blockInfo['numberOfPoints']
        self.dataInfo['speciesID'] = self.blockInfo['speciesID']
        self.dataInfo['minVal'] = self.blockInfo['minVal']
        self.dataInfo['maxVal'] = self.blockInfo['maxVal']

        # data_dimension_order describes in which dimension order the data is stored.
        # For example, in a point_mesh block,
        # '[x, y, z]' means x coordinates of the N points are stored first,
        # then y coordinates of the N points, and finally z coordinates.
        self.dataInfo['data_dimension_order'] = '[x, y, z]'
        self.dataInfo['quickPlotSpecified'] = 'points'

        self.dataInfoShowKeys += ['units', 'labels', 'minVal', 'maxVal',
                        'numberOfPoints', 'speciesID',
                        'data_dimension_order', 'quickPlotSpecified']

    def get(self):
        shape = (self.dataInfo['dataNumOfDimensions'], self.dataInfo['numberOfPoints'])
        return self.retrieveData().reshape(shape)

    def getp(self):
        return self.get()

class SDF_BLOCK_plain_variable(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

        self.blockInfo['mults'] = (struct.unpack('d', blockInfo[0:8]))[0]
        self.blockInfo['units'] = blockInfo[8:40].strip()
        self.blockInfo['meshID'] = blockInfo[40:72].strip()
        self.blockInfo['dims'] = struct.unpack('i' * (len(blockInfo[72:-4]) / 4), blockInfo[72:(len(blockInfo) - 4)])
        self.blockInfo['stagger'] = (struct.unpack('i', blockInfo[-4:]))[0]

        self.dataInfo['stagger'] = self.blockInfo['stagger']
        self.dataInfo['staggerName'] = SDF_STAGGER[self.blockInfo['stagger']]

        self.dataInfo['units'] = self.blockInfo['units']
        self.dataInfo['meshID'] = self.blockInfo['meshID']
        self.dataInfo['dims'] = self.blockInfo['dims']

        # data_order and data_shape describe the dimesional shape of a variable,
        # which is stored as a multi-dimesional array in linear list form.
        # For example, ['F', '[x, y, z]'] means, in FORTRAN('F') code,
        # you retrieve the value at (x[i], y[j], z[k]) by arr[i, j, k],
        # so the x dimension is stored continuously.
        # And, ['C', '[z, y, x]'] means, in C('C') code,
        # you retrieve the value at (x[i], y[j], z[k]) by arr[k][j][i]
        # so again the x dimension is stored continuously.
        self.dataInfo['data_order'] = ['F', '[x, y, z]']  # so the x dimension is stored continuously.
        self.dataInfo['data_shape'] = self.blockInfo['dims']
        self.dataInfo['data_shape_reduced'] = self.reduce_shape(self.dataInfo['data_shape'])

        self.dataInfo['data_order_c'] = ['C', '[z, y, x]']
        self.dataInfo['data_shape_c'] = self.dataInfo['data_shape'][::-1]
        self.dataInfo['data_shape_c_reduced'] = self.dataInfo['data_shape_reduced'][::-1]

        self.dataInfoShowKeys += ['units', 'meshID', 'dims',
                                'data_order_c', 'data_shape_c', 'data_shape_c_reduced']

    def get(self, shapeReduction = True):
        shape = self.dataInfo['data_shape_c']
        if shapeReduction:
            shape = self.dataInfo['data_shape_c_reduced']
        return self.retrieveData().reshape(shape, order = 'C')

    def getp(self):
        return self.get(True)

class SDF_BLOCK_point_variable(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

        self.blockInfo['mults'] = (struct.unpack('d', blockInfo[0:8]))[0]
        self.blockInfo['units'] = blockInfo[8:40].strip()
        self.blockInfo['meshID'] = blockInfo[40:72].strip()
        self.blockInfo['numberOfPoints'] = (struct.unpack('q', blockInfo[72:80]))[0]
        self.blockInfo['speciesID'] = blockInfo[80:].strip()

        self.dataInfo['units'] = self.blockInfo['units']
        self.dataInfo['meshID'] = self.blockInfo['meshID']
        self.dataInfo['numberOfPoints'] = self.blockInfo['numberOfPoints']
        self.dataInfo['speciesID'] = self.blockInfo['speciesID']

        self.dataInfoShowKeys += ['units', 'meshID', 'numberOfPoints', 'speciesID']

class SDF_BLOCK_constant(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

        varTypeStruct = SDF_TYPE_FOR_STRUCT[self.dataInfo['dataType']]
        varLen = len(blockInfo) / SDF_TYPE_SIZES[self.dataInfo['dataType']]
        self.blockInfo['constValue'] = struct.unpack(varTypeStruct * varLen, blockInfo)

        self.dataInfo['constValue'] = self.blockInfo['constValue']

        self.dataInfoShowKeys += ['constValue']

class SDF_BLOCK_array(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_run_info(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

        self.blockInfo['version'] = (struct.unpack('i', blockInfo[0:4]))[0]
        self.blockInfo['revision'] = (struct.unpack('i', blockInfo[4:8]))[0]
        self.blockInfo['commitID'] = blockInfo[8:72].strip()
        self.blockInfo['sha1sum'] = blockInfo[72:136].strip()
        self.blockInfo['compileMachine'] = blockInfo[136:200].strip()
        self.blockInfo['compileFlags'] = blockInfo[200:264].strip()
        self.blockInfo['defines'] = (struct.unpack('q', blockInfo[264:272]))[0]
        self.blockInfo['compileDate'] = (struct.unpack('i', blockInfo[272:276]))[0]
        self.blockInfo['runDate'] = (struct.unpack('i', blockInfo[276:280]))[0]
        self.blockInfo['ioDate'] = (struct.unpack('i', blockInfo[280:284]))[0]
        self.blockInfo['minorRevision'] = (struct.unpack('i', blockInfo[284:288]))[0]

class SDF_BLOCK_source(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_stitched_tensor(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_stitched_material(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_stitched_matvar(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_stitched_species(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_species(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_plain_derived(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_point_derived(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_contiguous_tensor(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_contiguous_material(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_contiguous_matvar(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_contiguous_species(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_cpu_split(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

        self.blockInfo['geometry'] = (struct.unpack('i', blockInfo[0:4]))[0]
        dim = len(blockInfo) / 4 - 1
        self.blockInfo['dims'] = struct.unpack('i' * dim, blockInfo[4:])

        if self.blockInfo['geometry'] > 3:
            warningStr = ''
            warningStr += self.dataInfo['FileName'] + ', ' + self.dataInfo['blockName'] + ', '
            warningStr += 'geometry = ' + str(self.blockInfo['geometry']) + ', out of range (0-3 expected), set to 0'
            self.blockInfo['geometry'] = 0
            self.block.sdf.d.warningStrings.append(warningStr)

        self.dataInfo['geometry'] = self.blockInfo['geometry']
        self.dataInfo['geometryName'] = SDF_GEOMETRY[self.blockInfo['geometry']]

        self.dataInfo['dims'] = self.blockInfo['dims']

        self.dataInfo['data_cpu_split_dim_order'] = '[x, y, z]'

        self.dataInfoShowKeys += ['dims', 'data_cpu_split_dim_order']

    def get(self):
        data = self.retrieveData()
        dataInDim = []
        dataVmaxInDim = []
        for blockObj in self.block.sdf.blocks:
            blockObjID = blockObj.blockHeader['blockID'].lower()
            while blockObjID[-1] == '\x00':
                blockObjID = blockObjID[:-1]
            if blockObjID == 'grid':
                for vmax in blockObj.blockInfo['dims']:
                    dataVmaxInDim.append(vmax - 1)
                break
        for dim in self.dataInfo['dims']:
            dataInDim.append(np.concatenate((data[:dim], [dataVmaxInDim[0]])))
            dataVmaxInDim = dataVmaxInDim[1:]
            data = data[dim:]
        return dataInDim

    def getp(self):
        dataInDim = self.get()
        stride = 4
        Max = 7
        dataP = 0
        unit = 0
        for oneDim in dataInDim:
            unitList = []
            preStep = 0
            for step in oneDim:
                unitList += [unit] * (step - preStep)
                preStep = step
                unit = (unit + stride) % Max
            dataP = np.array(unitList)
            unit = np.array(unitList)
        return dataP

class SDF_BLOCK_stitched_obstacle_group(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_unstructured_mesh(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_stitched(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_contiguous(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_lagrangian_mesh(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_station(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_station_derived(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_datablock(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_namevalue(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)

class SDF_BLOCK_scrubbed(sdf_block_data):
    def __init__(self, parentObj, blockInfo):
        sdf_block_data.__init__(self, parentObj, blockInfo)


SDF_BLOCK = [
    SDF_BLOCK_null,
    SDF_BLOCK_plain_mesh,
    SDF_BLOCK_point_mesh,
    SDF_BLOCK_plain_variable,
    SDF_BLOCK_point_variable,
    SDF_BLOCK_constant,
    SDF_BLOCK_array,
    SDF_BLOCK_run_info,
    SDF_BLOCK_source,
    SDF_BLOCK_stitched_tensor,
    SDF_BLOCK_stitched_material,
    SDF_BLOCK_stitched_matvar,
    SDF_BLOCK_stitched_species,
    SDF_BLOCK_species,
    SDF_BLOCK_plain_derived,
    SDF_BLOCK_point_derived,
    SDF_BLOCK_contiguous_tensor,
    SDF_BLOCK_contiguous_material,
    SDF_BLOCK_contiguous_matvar,
    SDF_BLOCK_contiguous_species,
    SDF_BLOCK_cpu_split,
    SDF_BLOCK_stitched_obstacle_group,
    SDF_BLOCK_unstructured_mesh,
    SDF_BLOCK_stitched,
    SDF_BLOCK_contiguous,
    SDF_BLOCK_plain_mesh,   # SDF_BLOCK_lagrangian_mesh, but use plain_mesh class.
    SDF_BLOCK_station,
    SDF_BLOCK_station_derived,
    SDF_BLOCK_datablock,
    SDF_BLOCK_namevalue,
    SDF_BLOCK_scrubbed
]


class _block(object):
    # Describes a block of an sdf file.
    # Contains a self.blockData object which abstracts the data area of the block.

    def __init__(self, blockNum, parentObj, dataFileName, blockLocation, blockHeader, blockInfo):
        self.FileName = dataFileName
        self.blockNo = blockNum
        self.blockIndex = blockNum - 1
        self.blockLocation = blockLocation

        self.sdf = parentObj

        # Contains block header content.
        self.blockHeader = {}

        # An data object that contains data information and provides data operation.
        # It's of different class type according to block type.
        self.blockData = None

        # Contains content from info area of a block. Filled by data object.
        self.blockInfo = None

        # Collection of all useful information about the data area of a block.
        self.DataInfo = None

        self.blockHeader['nextBlockLocation'] = (struct.unpack('q', blockHeader[:8]))[0]
        self.blockHeader['dataLocation'] = (struct.unpack('q', blockHeader[8:16]))[0]
        self.blockHeader['blockID'] = blockHeader[16:48].strip()
        self.blockHeader['dataLen'] = (struct.unpack('q', blockHeader[48:56]))[0]
        self.blockHeader['blockType'] = (struct.unpack('i', blockHeader[56:60]))[0]
        self.blockHeader['dataType'] = (struct.unpack('i', blockHeader[60:64]))[0]
        self.blockHeader['numberOfDimensions'] = (struct.unpack('i', blockHeader[64:68]))[0]
        self.blockHeader['blockName'] = blockHeader[68:132].strip()
        self.blockHeader['blockInfoLen'] = (struct.unpack('i', blockHeader[132:136]))[0]   # blockInfoLen contains only info, no header

        self.blockData = SDF_BLOCK[self.blockHeader['blockType']](self, blockInfo)

        self.blockInfo = self.blockData.blockInfo
        self.dataInfo = self.blockData.dataInfo

    def __repr__(self):
        return '<Block [%d] in %s : %s : %s>' % (self.blockIndex, self.FileName, self.blockHeader['blockName'], self.blockHeader['blockID'])

    def show(self, full_info = False):
        if not full_info:
            print 'block: %s : %s : %dD %s' % (self.blockHeader['blockName'],
                    self.blockHeader['blockID'],
                    self.blockHeader['numberOfDimensions'],
                    SDF_BLOCKTYPE[self.blockHeader['blockType']][14:])
        else:
            print 'block [%d] in %s : %s : %s : %dD %s : time=%r(s) : step=%d' % (self.blockIndex,
                    self.FileName,
                    self.blockHeader['blockName'],
                    self.blockHeader['blockID'],
                    self.blockHeader['numberOfDimensions'],
                    SDF_BLOCKTYPE[self.blockHeader['blockType']][14:],
                    self.sdf.SDFHeader['time'],
                    self.sdf.SDFHeader['step'])

    def __call__(self):
        return self.blockData

class _SDF(object):
    # Represent an sdf file.
    # Contains a list of block object(_block).

    def __init__(self, dataFileName, parentObj):
        self.d = parentObj

        self.FileName = dataFileName

        # Contains content of SDF header.
        self.SDFHeader = {}

        # A list holds the block objects.
        self.blocks = []

        f = open(dataFileName, 'rb')
        headerStr = f.read(112)

        self.SDFHeader['SDFMagic'] = headerStr[0:4]
        self.SDFHeader['constEndianness'] = (struct.unpack('i', headerStr[4:8]))[0]
        self.SDFHeader['sdfVersion'] = (struct.unpack('i', headerStr[8:12]))[0]
        self.SDFHeader['sdfRevision'] = (struct.unpack('i', headerStr[12:16]))[0]
        self.SDFHeader['codeName'] = headerStr[16:48].strip()
        self.SDFHeader['firstBlockLocation'] = (struct.unpack('q', headerStr[48:56]))[0]
        self.SDFHeader['summaryLocation'] = (struct.unpack('q', headerStr[56:64]))[0]
        self.SDFHeader['summarySize'] = (struct.unpack('i', headerStr[64:68]))[0]
        self.SDFHeader['numberOfBlocks'] = (struct.unpack('i', headerStr[68:72]))[0]
        self.SDFHeader['blockHeaderLength'] = (struct.unpack('i', headerStr[72:76]))[0]
        self.SDFHeader['step'] = (struct.unpack('i', headerStr[76:80]))[0]
        self.SDFHeader['time'] = (struct.unpack('d', headerStr[80:88]))[0]
        self.SDFHeader['jobID'] = {}
        self.SDFHeader['jobID']['startSeconds'] = (struct.unpack('i', headerStr[88:92]))[0]
        self.SDFHeader['jobID']['startMilliSeconds'] = (struct.unpack('i', headerStr[92:96]))[0]
        self.SDFHeader['stringLen'] = (struct.unpack('i', headerStr[96:100]))[0]
        self.SDFHeader['codeIOVersion'] = (struct.unpack('i', headerStr[100:104]))[0]
        self.SDFHeader['restartFlag'] = (struct.unpack('i', headerStr[104:108]))[0]
        self.SDFHeader['constNonRestartFlag'] = (struct.unpack('i', headerStr[108:112]))[0]

        numBlocks = 0
        nextBlockLocation = self.SDFHeader['firstBlockLocation']
        while numBlocks < self.SDFHeader['numberOfBlocks']:
            thisBlockLocation = nextBlockLocation
            f.seek(thisBlockLocation)
            numBlocks = numBlocks + 1

            blockHeader = f.read(self.SDFHeader['blockHeaderLength'])
            blockInfoLen = (struct.unpack('i', blockHeader[132:136]))[0]
            blockInfo = f.read(blockInfoLen)
            self.blocks.append(_block(numBlocks, self, dataFileName, thisBlockLocation, blockHeader, blockInfo))
            nextBlockLocation = (struct.unpack('q', blockHeader[:8]))[0]

        f.close()

    def __repr__(self):
        return '<SDF File : %s>' % (self.FileName)

    def __getitem__(self, index):
        return self.blocks[index]

    def __len__(self):
        return len(self.blocks)

    def __call__(self, *args, **kwargs):
        return self.sd(*args, **kwargs)

    def show(self, full_info = False):
        if not full_info:
            print 'SDF: %s time=%r(s) step=%d' % (self.FileName, self.SDFHeader['time'], self.SDFHeader['step'])
        else:
            print 'SDF: %s time=%r(s) step=%d' % (self.FileName, self.SDFHeader['time'], self.SDFHeader['step'])
            print '-----block list-----'
            index = 0
            for block in self.blocks:
                print '[%d]: ' % (index),
                block.show(full_info = False)
                index += 1

    def list(self):
        self.show(full_info = True)

    def sd(self, *args, **kwargs):
        dataList = []
        for block in self.blocks:
            dataList.append(block.blockData)
        return _searched_data(dataList).sd(*args, **kwargs)


class _d(object):
    # Abstracts an SDF file collection.
    # Maintains all SDF files. Origin for all other objects and operations.
    # Created only once and only one instance.
    # Contains a dictionary of SDF object(_SDF).

    def __init__(self, wd):
        self.warningStrings = []
        self.errorStrings = []

        # A list holds the sdf file names.
        self.SDFFileNames = []

        # A dictionary holds the sdf files.
        # The keys are the file names.
        self.SDFSet = {}

        # A list holds the directories,
        # in which sdf files are searched when the class is initialized.
        self.SDFDirs = []

        if type(wd) == type(''):
            if os.path.exists(wd) and (not os.path.isfile(wd)):
                self.SDFDirs.append(os.path.abspath(wd))
            else:
                warningS = "invalid directory path: " + wd
                self.warningStrings.append(warningS)
        elif type(wd) == type([]):
                if wd == []:
                    warningS = "_d got empty list for initialization."
                    self.warningStrings.append(warningS)
                else:
                    for i in wd:
                        if os.path.exists(i) and (not os.path.isfile(i)):
                            absDirPath = os.path.abspath(i)
                            if absDirPath in self.SDFDirs:
                                warningS = absDirPath + " given more than once, ignored."
                                self.warningStrings.append(warningS)
                            else:
                                self.SDFDirs.append(absDirPath)
                        else:
                            warningS = "invalid directory path: " + i
                            self.warningStrings.append(warningS)
        else:
            warningS = "_d need either str or list for initialization."
            self.warningStrings.append(warningS)

        self.SDFDirs.sort()
        for SDFDir in self.SDFDirs:
            fileSet = os.listdir(SDFDir)
            fileSet.sort()
            for fileName in fileSet:
                if self.isSDF(fileName):
                    absFileName = os.path.abspath(SDFDir + pathSeparator() + fileName)
                    self.SDFFileNames.append(absFileName)
                    self.SDFSet[absFileName] = _SDF(absFileName, self)

    def __repr__(self):
        return '<Set of SDF Files>'

    def __getitem__(self, index):
        return self.SDFSet[self.SDFFileNames[index]]

    def __len__(self):
        return len(self.SDFFileNames)

    def __call__(self, *args, **kwargs):
        return self.sf(*args, **kwargs)

    def show(self, full_info = False):
        if not full_info:
            print '%r' % self
        else:
            print '%r' % self
            print '-----file list-----'
            index = 0
            for fileName in self.SDFFileNames:
                print '[%d]: ' % (index),
                self.SDFSet[fileName].show(full_info = False)
                index += 1

    def list(self):
        self.show(full_info = True)

    def isSDF(self, fileName):
        if fileName[-4:].upper() == '.SDF':
            return True
        return False

    def sf(self, *args, **kwargs):
        fileList = []
        for fileName in self.SDFFileNames:
            fileList.append(self.SDFSet[fileName])
        return _searched_files(fileList).sf(*args, **kwargs)

    def sd(self, *args, **kwargs):
        dataList = []
        for fileName in self.SDFFileNames:
            for block in self.SDFSet[fileName].blocks:
                dataList.append(block.blockData)
        return _searched_data(dataList).sd(*args, **kwargs)


class _searched_files(object):
    # Abstracts a search result for sdf files.
    # Contains a list of sdf objects.

    def __init__(self, fileList):

        # Holds the sdf file objects.
        self.fileList = fileList

        self.fileList.sort(cmp = self.cmp_file)

    def __add__(self, _sfObject):
        if not type(_sfObject) == type(self):
            print type(self), 'cannot be added to other types.'
            return None
        else:
            fileList = []
            for fileObj in self.fileList:
                fileList.append(fileObj)
            for fileObj in _sfObject.fileList:
                if fileObj in fileList:
                    pass
                else:
                    fileList.append(fileObj)
            return _searched_files(fileList)

    def __repr__(self):
        return '<Collection of SDF File Searching Results>'

    def __getitem__(self, index):
        return self.fileList[index]

    def __len__(self):
        return len(self.fileList)

    def __call__(self, *args, **kwargs):
        return self.sf(*args, **kwargs)

    def cmp_file(self, file1, file2):
        return cmp(file1.FileName, file2.FileName)

    def show(self, full_info = False):
        if not full_info:
            print '%r' % self
        else:
            print '%r' % self
            print '-----file list-----'
            index = 0
            for sdfFile in self.fileList:
                print '[%d]: ' % (index),
                sdfFile.show(full_info = False)
                index += 1

    def list(self):
        self.show(full_info = True)

    def sf(self, *args, **kwargs):
        fileList = []
        if (args == ()) and (kwargs == {}):
            for fileObj in self.fileList:
                fileList.append(fileObj)
            return _searched_files(fileList)
        rev = False
        if kwargs.has_key('rev'):
            rev = True
            kwargs.pop('rev', None)
        for value in args:
            if type(value) == type(1):
                fileList = fileList + self.selectFiles(fileList, 'fileNameInteger', value, rev)
            elif (type(value) == type([])) or (type(value) == type(())):
                fileList = fileList + self.selectFiles(fileList, 'fileIndexList', value, rev)
            elif (type(value) == type('')):
                fileList = fileList + self.selectFiles(fileList, 'fileNameContainStr', value, rev)
            elif (type(value) == type(self)):
                fileList = fileList + self.selectFiles(fileList, 'importFromAnother', value, rev)
            else:
                print 'Warning: file searching condition', value, 'of type', type(value), 'is neglected.'
        for key, value in kwargs.items():
            fileList = fileList + self.selectFiles(fileList, key, value, rev)
        return _searched_files(fileList)

    def selectFiles(self, excludeList, key, value, rev):
        selectedFiles = []
        if key == 'fileNameInteger':
            for fileObj in self.fileList:
                fileNameStr = fileObj.FileName
                slashIndex = fileNameStr.rfind(pathSeparator())
                fileNameStr = fileNameStr[(slashIndex + 1):-4]
                cond = (int(fileNameStr) == value)
                if self.XOR(cond, rev) and (not fileObj in excludeList) and (not fileObj in selectedFiles):
                    selectedFiles.append(fileObj)
        elif key == 'fileIndexList':
            for index in value:
                if (type(index) == type(0)) and (index >= 0) and (index < len(self.fileList)):
                    fileObj = self.fileList[index]
                    if (not fileObj in excludeList) and (not fileObj in selectedFiles):
                        selectedFiles.append(fileObj)
        elif key == 'fileNameContainStr':
            for fileObj in self.fileList:
                fileNameStr = fileObj.FileName.upper()
                value = value.upper()
                cond = (fileNameStr.find(value) != -1)
                if self.XOR(cond, rev) and (not fileObj in excludeList) and (not fileObj in selectedFiles):
                    selectedFiles.append(fileObj)
        elif key == 'importFromAnother':
            for fileObj in value:
                if (not fileObj in excludeList) and (not fileObj in selectedFiles):
                    selectedFiles.append(fileObj)
        else:
            print 'Warning: file searching condition %s(%r)=%r is neglected.' % (key, not rev, value)
        return selectedFiles

    def XOR(self, cond, rev):
        if rev:
            return not cond
        else:
            return cond

    def sd(self, *args, **kwargs):
        dataList = []
        for fileObj in self.fileList:
            for block in fileObj.blocks:
                dataList.append(block.blockData)
        return _searched_data(dataList).sd(*args, **kwargs)


class _searched_data(object):
    # Abstracts search result of data.
    # Contains a list of data objects.

    def __init__(self, dataList):

        # Holds the data objects.
        self.dataList = dataList

        self.dataList.sort(cmp = self.cmp_data)

    def __add__(self, _sdObject):
        if not type(_sdObject) == type(self):
            print type(self), 'cannot be added to other types.'
            return None
        else:
            dataList = []
            for dataObj in self.dataList:
                dataList.append(dataObj)
            for dataObj in _sdObject.dataList:
                if dataObj in dataList:
                    pass
                else:
                    dataList.append(dataObj)
            return _searched_data(dataList)

    def __repr__(self):
        return '<Collection of Data Searching Results>'

    def __getitem__(self, index):
        return self.dataList[index]

    def __len__(self):
        return len(self.dataList)

    def __call__(self, *args, **kwargs):
        return self.sd(*args, **kwargs)

    def cmp_data(self, data1, data2):
        fNameCmp = cmp(data1.dataInfo['FileName'], data2.dataInfo['FileName'])
        if not fNameCmp == 0:
            return fNameCmp
        else:
            return cmp(data1.dataInfo['blockIndex'], data2.dataInfo['blockIndex'])

    def show(self, full_info = False, full_path = False):
        if not full_info:
            print '%r' % self
        else:
            print '%r' % self
            print '-----data list-----'
            index = 0
            for dataObj in self.dataList:
                print '[%d]: ' % (index),
                dataObj.show(full_info = False, full_path = full_path)
                index += 1

    def list(self, full_path = False):
        self.show(full_info = True, full_path = full_path)

    def sd(self, *args, **kwargs):
        dataList = []
        if (args == ()) and (kwargs == {}):
            for dataObj in self.dataList:
                dataList.append(dataObj)
            return _searched_data(dataList)
        rev = False
        if kwargs.has_key('rev'):
            rev = True
            kwargs.pop('rev', None)
        for value in args:
            if type(value) == type(1):
                dataList = dataList + self.selectData(dataList, 'blockIndexInteger', value, rev)
            elif (type(value) == type([])) or (type(value) == type(())):
                dataList = dataList + self.selectData(dataList, 'dataIndexList', value, rev)
            elif type(value) == type('a'):
                dataList = dataList + self.selectData(dataList, 'blockNameOrBlockIDContainStr', value, rev)
            elif type(value) == type(self):
                dataList = dataList + self.selectData(dataList, 'importFromAnother', value, rev)
            else:
                print 'Warning: data searching condition', value, 'of type', type(value), 'is neglected.'
        for key, value in kwargs.items():
            dataList = dataList + self.selectData(dataList, key, value, rev)
        return _searched_data(dataList)

    def selectData(self, excludeList, key, value, rev):
        selectedData = []
        if key == 'blockIndexInteger':
            for dataObj in self.dataList:
                dataBlockIndex = dataObj.dataInfo['blockIndex']
                cond = (dataBlockIndex == value)
                if self.XOR(cond, rev) and (not dataObj in excludeList) and (not dataObj in selectedData):
                    selectedData.append(dataObj)
        elif key == 'dataIndexList':
            for index in value:
                if (type(index) == type(0)) and (index >= 0) and (index < len(self.dataList)):
                    dataObj = self.dataList[index]
                    if (not dataObj in excludeList) and (not dataObj in selectedData):
                        selectedData.append(dataObj)
        elif key == 'blockNameOrBlockIDContainStr':
            value = value.upper()
            for dataObj in self.dataList:
                dataBlockName = dataObj.dataInfo['blockName'].upper()
                dataBlockID = dataObj.dataInfo['blockID'].upper()
                nameContain = dataBlockName.find(value)
                IDContain = dataBlockID.find(value)
                cond = (nameContain != -1) or (IDContain != -1)
                if self.XOR(cond, rev) and (not dataObj in excludeList) and (not dataObj in selectedData):
                    selectedData.append(dataObj)
        elif key == 'importFromAnother':
            for dataObj in value:
                if (not dataObj in excludeList) and (not dataObj in selectedData):
                    selectedData.append(dataObj)
        else:
            keyValid = False
            for dataObj in self.dataList:
                if dataObj.dataInfo.has_key(key):
                    keyValid = True
                    compareValue_x00 = dataObj.dataInfo[key]
                    compareValue = dataObj.dataInfo[key]
                    if type(compareValue == ''):
                        while compareValue[-1] == '\x00':
                            compareValue = compareValue[:-1]
                    cond1 = (value == compareValue) or (value == compareValue_x00)
                    cond2 = False
                    if (type(value) == type([])) or (type(value) == type(())):
                        for subValue in value:
                            cond2 = cond2 or (subValue == compareValue)
                    cond = cond1 or cond2
                    if self.XOR(cond, rev) and (not dataObj in excludeList) and (not dataObj in selectedData):
                        selectedData.append(dataObj)
            if not keyValid:
                print 'Warning: data searching condition %s(%r)=%r is neglected.' % (key, not rev, value)
        return selectedData

    def XOR(self, cond, rev):
        if rev:
            return not cond
        else:
            return cond


def d(wd = '.'):
    dataSet = _d(wd)
    for estr in dataSet.errorStrings:
        print 'Error:', estr
    for wstr in dataSet.warningStrings:
        print 'Warning:', wstr
    return dataSet

def pathSeparator():
    return '/'


if __name__ == '__main__':
    print 'Please import this module from python.'

