'''
MTX - file parser by Ben Schneider


for now you can load it with 'execfile('mtx_parser.py)'
it will add the following content.


content:
    loaddat : load an ASCII data file ( loaddat('file.dat') )
    savedat : save an ASCII data file ( savedat('file.dat') )
    loadmtx : load a binary data file ( loadmtx('file.mtx') )
    savemtx : save a binary data file ( savemtx('file.mtx', 3d_numpy_array))


missing:
-   requires a default header when saving MTX
-   additional descriptions
-   Change into an importable thingy


'''
import numpy as np
from struct import pack, unpack
import csv


def loaddat(*inputs):
    '''
    This simply uses the numpy.genfromtxt function to
    load a data containing file in ascii
    (It rotates the output such that each colum can be accessed easily)


    example:
    in the directory:
    1.dat:
        1   2   a
        3   b   4
        c   5   6
        7   8   d


    >> A = loaddat('1.dat')
    >> A[0]
    (1,3,c,7)
    '''
    file_data = np.genfromtxt(*inputs)
    outputs = zip(*file_data)
    return outputs


def savedat(filename1,data1,**quarks):
    #just use : np.savetxt(filename, data, delimiter = ',')
    '''filename, data, arguments
    simply uses numpy.savetext with a 
    delimiter = ','    
    
    np.savetxt("QsQr.dat",stuff ,delimiter =',')
    default: delimiter = '\t'  (works best with gnuplot even with excel)  
    '''
    data1 = zip(*data1)
    if 'delimiter' in quarks:
        np.savetxt(filename1, data1 ,**quarks)    
    else:
        np.savetxt(filename1, data1 , delimiter = '\t', **quarks)    


def loadcsv(filename, delim =';'):
    #open file (using with to make sure file is closed afer use)
    with open(filename, 'Ur') as f:
        #collect tuples as a list in data, then convert to an np.array and return
        data = list(tuple(rec) for rec in csv.reader(f, delimiter=delim))
        data = np.array(data, dtype=float)
    return data.transpose()
    
    
def loadmtx(filename):
    '''
    Loads an mtx file (binary compressed file)
    (first two lines of the MTX contain information of the data shape and
    what units, limits are present)
    i.e.: 
    
    mtx, header = loadmtx('filename.mtx')
    
    mtx     :   will contain a 3d numpy array of the data
    header  :   will contain information on the labels and limits
    '''
    with open(filename, 'rb') as f:


        line = f.readline()
        header = line[:-1].split(',')
        #header = line
    
        line = f.readline()
        a = line[:-1].split(' ')
        s = np.array(map(float, a))
    
        raw = f.read() #reads everything else
        f.close()
        
    if s[3] == 4:
        data = unpack('f'*(s[2]*s[1]*s[0]), raw) #uses float
        M = np.reshape(data, (s[2], s[1], s[0]), order="F")
    else:
        data = unpack('d'*(s[2]*s[1]*s[0]), raw) #uses double
        M = np.reshape(data, (s[2], s[1], s[0]), order="F")
    return M, header
