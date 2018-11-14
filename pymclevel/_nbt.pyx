# cython: profile=True
# vim:set sw=2 sts=2 ts=2:

"""
Cython implementation

Named Binary Tag library. Serializes and deserializes TAG_* objects
to and from binary data. Load a Minecraft level by calling nbt.load().
Create your own TAG_* objects and set their values.
Save a TAG_* object to a file or StringIO object.

Read the test functions at the end of the file to get started.

This library requires Numpy.    Get it here:
http://new.scipy.org/download.html

Official NBT documentation is here:
http://www.minecraft.net/docs/NBT.txt


Copyright 2012 David Rio Vierra
"""


#  UNICODE_NAMES
#According to NBT specification, tag names are UTF-8 encoded text. Decoding the bytes to unicode objects takes
#time and also takes a lot of memory because unicode strings can't be interned. Since all known tag names can be
#represented using ASCII, we can read the names as str objects ('bytes' according to Cython),
#saving time by skipping the decode step and saving a ton of memory by not storing duplicate strings.
#
#(I also tried to address this by "interning" the unicode strings into a dict myself, but this doubled the load time.)
#
# When UNICODE_NAMES is True, follows the NBT spec exactly and decodes all tag names to 'unicode' objects
# When UNICODE_NAMES is False, reads tag names as 'str' objects
DEF UNICODE_NAMES = False

import collections
import gzip
import zlib

from cStringIO import StringIO
from cpython cimport PyTypeObject, PyObject_TypeCheck, PyUnicode_DecodeUTF8, PyList_Append
import numpy

cdef extern from "cStringIO.h":
    struct PycStringIO_CAPI:
        int cwrite(object o, char * buf, Py_ssize_t len)
        PyTypeObject * OutputType
cdef extern from "cobject.h":
    void * PyCObject_Import(char * module_name, char * cobject_name)

cdef PycStringIO_CAPI *PycStringIO = <PycStringIO_CAPI *> PyCObject_Import("cStringIO", "cStringIO_CAPI")
cdef PyTypeObject * StringO = PycStringIO.OutputType

from numpy import array, zeros, uint8, fromstring, ndarray, frombuffer

cdef char TAG_END = 0
cdef char TAG_BYTE = 1
cdef char TAG_SHORT = 2
cdef char TAG_INT = 3
cdef char TAG_LONG = 4
cdef char TAG_FLOAT = 5
cdef char TAG_DOUBLE = 6
cdef char TAG_BYTE_ARRAY = 7
cdef char TAG_STRING = 8
cdef char TAG_LIST = 9
cdef char TAG_COMPOUND = 10
cdef char TAG_INT_ARRAY = 11
cdef char TAG_SHORT_ARRAY = 12


class NBTFormatError (ValueError):
    pass

import nbt_util
cdef class TAG_Value:
    IF UNICODE_NAMES:
        cdef unicode _name
    ELSE:
        cdef bytes _name
    cdef public char tagID

    def __repr__(self):
        return "<%s name=\"%s\" value=%r>" % (self.__class__.__name__, self.name, self.value)

    def __str__(self):
        return nbt_util.nested_string(self)

    property name:
        def __get__(self):
            return self._name

        def __set__(self, val):
            IF UNICODE_NAMES:
                if isinstance(val, str):
                    val = PyUnicode_DecodeUTF8(val, len(val), "strict")
            ELSE:
                if isinstance(val, unicode):
                    val = str(val)
            self._name = val

    def __reduce__(self):
        return self.__class__, (self.value, self._name)


cdef class TAG_Byte(TAG_Value):
    cdef public char value

    cdef save_value(self, buf):
        save_byte(self.value, buf)

    def __init__(self, char value=0, name=""):
        self.value = value
        self.name = name
        self.tagID = TAG_BYTE


cdef class TAG_Short(TAG_Value):
    cdef public short value

    cdef save_value(self, buf):
        save_short(self.value, buf)

    def __init__(self, short value=0, name=""):
        self.value = value
        self.name = name
        self.tagID = TAG_SHORT


cdef class TAG_Int(TAG_Value):
    cdef public int value

    cdef save_value(self, buf):
        save_int(self.value, buf)

    def __init__(self, int value=0, name=""):
        self.value = value
        self.name = name
        self.tagID = TAG_INT


cdef class TAG_Long(TAG_Value):
    cdef public long long value

    cdef save_value(self, buf):
        save_long(self.value, buf)

    def __init__(self, long long value=0, name=""):
        self.value = value
        self.name = name
        self.tagID = TAG_LONG


cdef class TAG_Float(TAG_Value):
    cdef public float value

    cdef save_value(self, buf):
        save_float(self.value, buf)

    def __init__(self, float value=0., name=""):
        self.value = value
        self.name = name
        self.tagID = TAG_FLOAT


cdef class TAG_Double(TAG_Value):
    cdef public double value

    cdef save_value(self, buf):
        save_double(self.value, buf)

    def __init__(self, double value=0., name=""):
        self.value = value
        self.name = name
        self.tagID = TAG_DOUBLE


cdef class TAG_Byte_Array(TAG_Value):
    cdef public object value
    dtype = numpy.dtype('u1')

    def __init__(self, value=None, name=""):
        if value is None:
            value = zeros((0,), self.dtype)

        self.value = value
        self.name = name
        self.tagID = TAG_BYTE_ARRAY

    cdef save_value(self, buf):
        save_array(self.value, buf, 1)

    def __repr__(self):
        return "<%s name=%s length=%d>" % (self.__class__.__name__, self.name, len(self.value))


cdef class TAG_Int_Array(TAG_Value):
    cdef public object value
    dtype = numpy.dtype('>u4')

    def __init__(self, value=None, name=""):
        if value is None:
            value = zeros((0,), self.dtype)

        self.value = value
        self.name = name
        self.tagID = TAG_INT_ARRAY

    cdef save_value(self, buf):
        save_array(self.value, buf, 4)


cdef class TAG_Short_Array(TAG_Value):
    cdef public object value
    dtype = numpy.dtype('>u2')

    def __init__(self, value=None, name=""):
        if value is None:
            value = zeros((0,), self.dtype)

        self.value = value
        self.name = name
        self.tagID = TAG_SHORT_ARRAY

    cdef save_value(self, buf):
        save_array(self.value, buf, 2)


cdef class TAG_String(TAG_Value):
    cdef unicode _value

    def __init__(self, value="", name=""):
        self.value = value
        self.name = name
        self.tagID = TAG_STRING

    property value:
        def __get__(self):
            return self._value

        def __set__(self, value):
            if isinstance(value, str):
                value = PyUnicode_DecodeUTF8(value, len(value), "strict")
            self._value = value

    cdef save_value(self, buf):
        save_string(self._value.encode('utf-8'), buf)


cdef class _TAG_List(TAG_Value):
    cdef public list value
    cdef public char list_type

    def __init__(self, value=None, name="", list_type=TAG_BYTE):
        self.value = []
        self.name = name
        self.list_type = list_type
        self.tagID = TAG_LIST
        if value:
            self.list_type = value[0].tagID
            for tag in value:
                self.check_tag(tag)
            self.value = list(value)


    def __repr__(self):
        return "<%s name='%s' list_type=%r length=%d>" % (self.__class__.__name__, self.name,
                                                          tag_classes[self.list_type],
                                                          len(self))

    def check_tag(self, value):
        if value.tagID != self.list_type:
            raise TypeError("Invalid type %s for TAG_List(%s)" % (value.__class__, tag_classes[self.list_type]))

    # --- collection methods ---
    def __getitem__(self, index):
        return self.value[index]

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            for tag in value:
                self.check_tag(tag)
        else:
            self.check_tag(value)
        self.value[index] = value

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def insert(self, index, tag):
        if len(self.value) == 0:
            self.list_type = tag.tagID
        else:
            self.check_tag(tag)

        self.value.insert(index, tag)

    def __delitem__(self, key):
        del self.value[key]

    cdef save_value(self, buf):
        cdef char list_type = self.list_type
        cdef TAG_Value tag

        save_tag_id(list_type, buf)
        save_int(<int>len(self.value), buf)

        cdef TAG_Value subtag
        for subtag in self.value:
            if subtag.tagID != list_type:
                raise ValueError("Asked to save TAG_List with different types! Found %s and %s" % (subtag.tagID,
                                                                                                   list_type))
            save_tag_value(subtag, buf)


class TAG_List(_TAG_List, collections.MutableSequence):
    pass


cdef class _TAG_Compound(TAG_Value):
    cdef public object value

    def __init__(self, value=None, name=""):
        self.value = value or []
        self.name = name
        self.tagID = TAG_COMPOUND

    #
    # --- collection methods ---
    #

    def __getitem__(self, key):
        cdef TAG_Value tag
        for tag in self.value:
            if tag._name == key:
                return tag
        raise KeyError("Key %s not found." % key)

    def __setitem__(self, key, tag):
        tag.name = key
        cdef TAG_Value v
        self.value = [v for v in self.value if v._name != key]
        self.value.append(tag)

    def __delitem__(self, key):
        oldlen = len(self.value)
        cdef TAG_Value v
        self.value = [v for v in self.value if v._name != key]
        if oldlen == len(self.value):
            raise KeyError("Key %s not found" % key)

    def __iter__(self):
        cdef TAG_Value v
        for v in self.value:
            yield v._name

    def __contains__(self, k):
        return any(tag.name == k for tag in self.value)

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return "<%s name='%s' keys=%r>" % (str(self.__class__.__name__), self.name, self.keys())

    def add(self, TAG_Value tag):
        if not tag._name:
            raise ValueError("Cannot add unnamed tag to TAG_Compound")

        self[tag._name] = tag

    def get_all(self, key):
        return [v for v in self.value if v.name == key]

    cdef save_value(self, buf):
        cdef TAG_Value subtag
        for subtag in self.value:
            save_tag_id(subtag.tagID, buf)
            save_tag_name(subtag, buf)
            save_tag_value(subtag, buf)
        save_tag_id(TAG_END, buf)

    def save(self, filename_or_buf=None, compressed=True):
        """
        Pass a filename to save the data to a file. Pass a file-like object (with a read() method)
        to write the data to that object. Pass nothing to return the data as a string.
        """
        io = StringIO()
        save_tag_id(self.tagID, io)
        save_tag_name(self, io)
        save_tag_value(self, io)
        data = io.getvalue()
        if compressed:
            gzio = StringIO()
            gz = gzip.GzipFile(fileobj=gzio, mode='wb')
            gz.write(data)
            gz.close()
            data = gzio.getvalue()

        if filename_or_buf is None:
            return data

        if isinstance(filename_or_buf, basestring):
            f = file(filename_or_buf, "wb")
            f.write(data)
        else:
            filename_or_buf.write(data)


class TAG_Compound(_TAG_Compound, collections.MutableMapping):
    pass
#    def __init__(self, value = None, name=""):
#        _TAG_Compound.__init__(self, value, name)

#cdef int needswap = (sys.byteorder == "little")
cdef swab(void * vbuf, int nbytes):
    cdef unsigned char * buf = <unsigned char *> vbuf
    #print "Swapping ", nbytes, "bytes"
    #for i in range(nbytes): print buf[i],
    #print "to",
    #if not needswap: return
    cdef int i
    for i in range((nbytes+1)/2):
        buf[i], buf[nbytes - i -1] = buf[nbytes - i - 1], buf[i]
    #for i in range(nbytes): print buf[i],


def gunzip(data):
    return gzip.GzipFile(fileobj=StringIO(data)).read()


def try_gunzip(data):
    try:
        data = gunzip(data)
    except IOError, zlib.error:
        pass
    return data


def load(filename="", buf=None):
    if filename:
        buf = file(filename, "rb")

    if hasattr(buf, "read"):
        buf = buf.read()

    return load_buffer(try_gunzip(buf))


cdef class load_ctx:
    cdef size_t offset
    cdef char * buffer
    cdef size_t size


cdef char * require(load_ctx self, size_t s) except NULL:
    if s > self.size - self.offset:
        raise NBTFormatError("NBT Stream too short. Asked for %d, only had %d" % (s, (self.size - self.offset)))

    cdef char * ret = self.buffer + self.offset
    self.offset += s
    return ret


cdef load_buffer(bytes buf):
    cdef load_ctx ctx = load_ctx()
    ctx.offset = 1
    ctx.buffer = buf
    ctx.size = len(buf)
    if len(buf) < 1:
        raise NBTFormatError("NBT Stream too short!")

    cdef unsigned int * magic_no = <unsigned int *> ctx.buffer

    if ctx.buffer[0] != TAG_COMPOUND:
        raise NBTFormatError('Not an NBT file with a root TAG_Compound '
                             '(file starts with "%4s" (0x%08x)' % (ctx.buffer, magic_no[0]))
    name = load_name(ctx)
    tag = load_compound(ctx)
    tag.name = name
    return tag

cdef load_byte(load_ctx ctx):

    cdef TAG_Byte tag = TAG_Byte.__new__(TAG_Byte)
    tag.value = require(ctx, 1)[0]
    tag.tagID = TAG_BYTE
    return tag


cdef load_short(load_ctx ctx):
    cdef short * ptr = <short *> require(ctx, 2)
    cdef TAG_Short tag = TAG_Short.__new__(TAG_Short)
    tag.value = ptr[0]
    swab(&tag.value, 2)
    tag.tagID = TAG_SHORT
    return tag


cdef load_int(load_ctx ctx):
    cdef int * ptr = <int *> require(ctx, 4)
    cdef TAG_Int tag = TAG_Int.__new__(TAG_Int)
    tag.value = (ptr[0])
    swab(&tag.value, 4)
    tag.tagID = TAG_INT
    return tag


cdef load_long(load_ctx ctx):
    cdef long long * ptr = <long long *> require(ctx, 8)
    cdef TAG_Long tag = TAG_Long.__new__(TAG_Long)
    tag.value = ptr[0]
    swab(&tag.value, 8)
    tag.tagID = TAG_LONG
    return tag


cdef load_float(load_ctx ctx):
    cdef float * ptr = <float *> require(ctx, 4)
    cdef TAG_Float tag = TAG_Float.__new__(TAG_Float)
    tag.value = ptr[0]
    swab(&tag.value, 4)
    tag.tagID = TAG_FLOAT
    return tag


cdef load_double(load_ctx ctx):
    cdef double * ptr = <double *> require(ctx, 8)
    cdef TAG_Double tag = TAG_Double.__new__(TAG_Double)
    tag.value = ptr[0]
    swab(&tag.value, 8)
    tag.tagID = TAG_DOUBLE
    return tag


cdef load_array(load_ctx ctx, object TagClass):
    cdef int * ptr = <int *> require(ctx, 4)
    cdef int length = ptr[0]
    swab(&length, 4)

    byte_length = length * TagClass.dtype.itemsize
    cdef char *arr = require(ctx, byte_length)
    return TagClass(fromstring(arr[:byte_length], dtype=TagClass.dtype, count=length))


cdef load_compound(load_ctx ctx):
    cdef char tagID
    cdef _TAG_Compound root_tag = TAG_Compound()

    while True:
        tagID = require(ctx, 1)[0]
        if tagID == TAG_END:
            break
        else:
            root_tag.value.append(load_named(ctx, tagID))

    return root_tag


cdef load_named(load_ctx ctx, char tagID):
    name = load_name(ctx)
    cdef TAG_Value tag = load_tag(tagID, ctx)
    tag._name = name
    return tag


cdef load_list(load_ctx ctx):

    cdef char list_type = require(ctx, 1)[0]
    cdef int * ptr = <int *> require(ctx, 4)
    cdef int length = ptr[0]
    swab(&length, 4)

    cdef _TAG_List tag = TAG_List(list_type=list_type)
    cdef list val = tag.value
    cdef int i
    for i in range(length):
        PyList_Append(val, load_tag(list_type, ctx))

    return tag


cdef unicode load_string(load_ctx ctx):

    cdef unsigned short * ptr = <unsigned short *> require(ctx, 2)
    cdef unsigned short length = ptr[0]
    swab(&length, 2)

    u = PyUnicode_DecodeUTF8(require(ctx, length), length, "strict")
    return u

IF UNICODE_NAMES:
    cdef unicode load_name(load_ctx ctx):
        return load_string(ctx)
ELSE:
    cdef bytes load_name(load_ctx ctx):
        """
        Like load_string, but returns a str instead so python can intern it, saving memory.
        """
        cdef unsigned short *ptr = <unsigned short *> require(ctx, 2)
        cdef unsigned short length = ptr[0]
        swab(&length, 2)

        return require(ctx, length)[:length]

cdef load_tag(char tagID, load_ctx ctx):
    if tagID == TAG_BYTE:
        return load_byte(ctx)

    if tagID == TAG_SHORT:
        return load_short(ctx)

    if tagID == TAG_INT:
        return load_int(ctx)

    if tagID == TAG_LONG:
        return load_long(ctx)

    if tagID == TAG_FLOAT:
        return load_float(ctx)

    if tagID == TAG_DOUBLE:
        return load_double(ctx)

    if tagID == TAG_BYTE_ARRAY:
        return load_array(ctx, TAG_Byte_Array)

    if tagID == TAG_STRING:
        u = load_string(ctx)
        return TAG_String(u)

    if tagID == TAG_LIST:
        return load_list(ctx)

    if tagID == TAG_COMPOUND:
        return load_compound(ctx)

    if tagID == TAG_INT_ARRAY:
        return load_array(ctx, TAG_Int_Array)

    if tagID == TAG_SHORT_ARRAY:
        return load_array(ctx, TAG_Short_Array)


def hexdump(src, length=8):
    FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
    N=0
    result=''
    while src:
        s, src = src[:length], src[length:]
        hexa = ' '.join(["%02X"%ord(x) for x in s])
        s = s.translate(FILTER)
        result += "%04X   %-*s   %s\n" % (N, length * 3, hexa, s)
        N+=length
    return result


cdef cwrite(obj, char *buf, size_t len):
    #print "cwrite %s %s %d" % (map(ord, buf[:min(4, len)]), buf[:min(4, len)].decode('ascii', 'replace'), len)
    return PycStringIO.cwrite(obj, buf, len)


cdef save_tag_id(char tagID, object buf):
    cwrite(buf, &tagID, 1)


cdef save_tag_name(TAG_Value tag, object buf):
    IF UNICODE_NAMES:
        cdef unicode name = tag._name
        save_string(name.encode('utf-8'), buf)
    ELSE:
        save_string(tag._name, buf)


cdef save_string(bytes value, object buf):
    cdef short length = <short>len(value)
    cdef char * s = value
    swab(&length, 2)
    cwrite(buf, <char *> &length, 2)
    cwrite(buf, s, len(value))


cdef save_array(object value, object buf, char size):
    value = value.tostring()
    cdef char * s = value
    cdef int length = <int>len(value) / size
    swab(&length, 4)
    cwrite(buf, <char *> &length, 4)
    cwrite(buf, s, len(value))


cdef save_byte(char value, object buf):
    cwrite(buf, <char *> &value, 1)


cdef save_short(short value, object buf):
    swab(&value, 2)
    cwrite(buf, <char *> &value, 2)


cdef save_int(int value, object buf):
    swab(&value, 4)
    cwrite(buf, <char *> &value, 4)


cdef save_long(long long value, object buf):
    swab(&value, 8)
    cwrite(buf, <char *> &value, 8)


cdef save_float(float value, object buf):
    swab(&value, 4)
    cwrite(buf, <char *> &value, 4)


cdef save_double(double value, object buf):
    swab(&value, 8)
    cwrite(buf, <char *> &value, 8)


cdef save_tag_value(TAG_Value tag, object buf):
    cdef char tagID = tag.tagID
    if tagID == TAG_BYTE:
        (<TAG_Byte> tag).save_value(buf)

    if tagID == TAG_SHORT:
        (<TAG_Short> tag).save_value(buf)

    if tagID == TAG_INT:
        (<TAG_Int> tag).save_value(buf)

    if tagID == TAG_LONG:
        (<TAG_Long> tag).save_value(buf)

    if tagID == TAG_FLOAT:
        (<TAG_Float> tag).save_value(buf)

    if tagID == TAG_DOUBLE:
        (<TAG_Double> tag).save_value(buf)

    if tagID == TAG_BYTE_ARRAY:
        (<TAG_Byte_Array> tag).save_value(buf)

    if tagID == TAG_STRING:
        (<TAG_String> tag).save_value(buf)

    if tagID == TAG_LIST:
        (<_TAG_List> tag).save_value(buf)

    if tagID == TAG_COMPOUND:
        (<_TAG_Compound> tag).save_value(buf)

    if tagID == TAG_INT_ARRAY:
        (<TAG_Int_Array> tag).save_value(buf)

    if tagID == TAG_SHORT_ARRAY:
        (<TAG_Int_Array> tag).save_value(buf)


tag_classes = {TAG().tagID: TAG for TAG in (TAG_Byte, TAG_Short, TAG_Int, TAG_Long, TAG_Float, TAG_Double, TAG_String,
                                            TAG_Byte_Array, TAG_List, TAG_Compound, TAG_Int_Array, TAG_Short_Array)}

#if __name__ == "__main__":
#    import test.time_nbt
