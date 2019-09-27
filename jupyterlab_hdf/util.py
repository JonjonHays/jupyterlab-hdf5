import re

from tornado.web import HTTPError

__all__ = [
    # 'chunkSlice',
    'dsetChunk',
    # 'dsetContentDict',
    # 'dsetDict',
    # 'groupDict',
    'uriJoin',
    'uriName'
]

## chunk handling
# def chunkSlice(chunk, s):
#     if s.start is None:
#         return slice(None, s.stop*chunk, s.step)
#
#     return slice(s.start*chunk, s.stop*chunk, s.step)

def dsetChunk(dset, select):
    slices = getHyperslabSlices(dset.shape, select)
    return dset[slices].tolist()

def getHyperslabSlices(dsetshape, select):
    rank = len(dsetshape)
    if select == 'ALL':
        # Default: return entire dataset
        return tuple(slice(0, extent) for extent in dsetshape)
    if rank == 1:
        return slice()

    if not select.startswith('['):
        msg = "Bad Request: selection query missing start bracket"
        raise HTTPError(400, reason=msg)
    if not select.endswith(']'):
        msg = "Bad Request: selection query missing end bracket"
        raise HTTPError(400, reason=msg)

    # strip brackets
    select = select[1:-1]

    select_array = select.split(',')
    slices = []
    for dim, dim_slice in enumerate(select_array):
        extent = dsetshape[dim]

        # default slice values
        start = 0
        stop = extent
        step = 1
        if dim_slice.find(':') < 0:
            # just a number - return slice(start, start + 1, 1) for this dimension
            try:
                start = int(dim_slice)
            except ValueError:
                msg = "Bad Request: invalid selection parameter (can't convert to int) for dimension: " + str(dim)
                raise HTTPError(400, reason=msg)
            stop = start + 1
        elif dim_slice == ':':
            # select everything (default)
            pass
        else:
            fields = dim_slice.split(":")
            if len(fields) > 3:
                msg = "Bad Request: Too many ':' seperators for dimension: " + str(dim)
                raise HTTPError(400, reason=msg)
            try:
                if fields[0]:
                    start = int(fields[0])
                if fields[1]:
                    stop = int(fields[1])
                if len(fields) > 2 and fields[2]:
                    step = int(fields[2])
            except ValueError:
                msg = "Bad Request: invalid selection parameter (can't convert to int) for dimension: " + str(dim)
                raise HTTPError(400, reason=msg)

        if start < 0 or start > extent:
            msg = "Bad Request: Invalid selection start parameter for dimension: " + str(dim)
            raise HTTPError(400, reason=msg)
        if stop > extent:
            msg = "Bad Request: Invalid selection stop parameter for dimension: " + str(dim)
            raise HTTPError(400, reason=msg)
        if step <= 0:
            msg = "Bad Request: invalid selection step parameter for dimension: " + str(dim)
            raise HTTPError(400, reason=msg)
        slices.append(slice(start, stop, step))

    return tuple(slices)



## create dicts to be converted to json
# def dsetContentDict(dset, row=None, col=None):
#     return dict([
#         # metadata
#         ('attrs', dict(*dset.attrs.items())),
#         ('dtype', dset.dtype.str),
#         ('ndim', dset.ndim),
#         ('shape', dset.shape),
#
#         # actual data
#         ('data', dsetChunk(dset, row, col) if row and col else None)
#     ])

# def dsetDict(name, uri, content=None):
#     return dict([
#         ('type', 'dataset'),
#         ('name', name),
#         ('uri', uri),
#         ('content', content)
#     ])
#
# def groupDict(name, uri):
#     return dict([
#         ('type', 'group'),
#         ('name', name),
#         ('uri', uri),
#         ('content', None)
#     ])


## uri handling
_emptyUriRe = re.compile('//')
def uriJoin(*parts):
    return _emptyUriRe.sub('/', '/'.join(parts))

def uriName(uri):
    return uri.split('/')[-1]
