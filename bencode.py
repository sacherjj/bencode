"""
Bencode handling Class for decoding a .torrent file or other Bencoded data.

Bencode Python Class by Joe Sacher is licensed under a
Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
http://creativecommons.org/licenses/by-nc-sa/3.0/

General Bencoding guidelines:
    Byte string (not necessarily a valid text string) 
        <length>:<contents>
    
    Integer  (no leading zero, leading '-' negates) 
        i<number in base 10>e  
        
    List 
        l<contents>e
    
    Dictionary: 
        d<contents>e
        
        contents are <key><value><key><value>
        key byte string
        value any valid
"""


class Bencode(object):
    """
    Converts to and from a Bencoded data structure
    """
    
    _ben_string = []
    _pointer = 0

    def __init__(self):
        pass

    #
    #  Encoding Methods
    #
    def encode(self, data):
        """
        Returns a Bencoded string describing the data provided
        
        Conversions performed:
        Strings -> Byte Strings
        Integers -> Integers
        Floats -> Integers with truncate
        List -> List
        Tuple -> List
        Dictionary -> Dictionary        
        """
        return self._local_encode(data)
        
    def _local_encode(self, data):
        """ Returns the proper Bencoded string for data given """
        encoders = {'dict': self._encode_dictionary,
                    'list': self._encode_list,
                    'tuple': self._encode_list,
                    'str': self._encode_string,
                    'int': self._encode_integer,
                    'float': self._encode_float}
        data_type = type(data).__name__
        if data_type in encoders.keys():
            return encoders[data_type](data)
        else:
            raise Exception('Encoder is not defined for data type: %s' % data_type)

    @staticmethod
    def _encode_string(data):
        """ Converts string to Bencoded Byte String """
        return '%d:%s' % (len(data), data)
        
    @staticmethod
    def _encode_integer(data):
        """ Converts Integer to Bencoded Integer string """
        return 'i%de' % data

    def _encode_float(self, data):
        """ Converts Float to Bencoded Integer string """
        return self._encode_integer(int(data))
    
    def _encode_list(self, data):
        """ Converts List or Tuple to Bencoded List string """
        ben = ['l']
        for item in data:
            ben.append(self._local_encode(item))
        ben.append('e')
        return ''.join(ben)
    
    def _encode_dictionary(self, data):
        """ Converts Dictionary to Bencoded Dictionary String """
        ben = ['d']
        for key in sorted(data.keys()):
            ben.append(self._encode_string(key))
            ben.append(self._local_encode(data[key]))
        ben.append('e')
        return''.join(ben)

    #
    # Decoding Methods
    #    
    
    def _debug(self, location):
        print location + ' - ' + str(self._pointer) + ' ' + self._ben_string[self._pointer:self._pointer + 30]
        
    def decode(self, ben_string):
        """ Returns the data structure defined by the Bencoded string """
        try:
            self._ben_string = ben_string
            self._pointer = 0
            return self._local_decode()
        except IndexError as e:
            print("Index Error at Pointer = %d of %d\n%s" % (self._pointer, len(self._ben_string), str(e)))

    def _local_decode(self):
        """ Detects and returns the proper Bencoded data type starting at current Pointer position """
        cur_char = self._ben_string[self._pointer]
        if cur_char == 'i':
            return self._parse_integer()
        elif cur_char == 'l':
            return self._parse_list()
        elif cur_char == 'd':
            return self._parse_dictionary()
        elif cur_char in ('-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
            return self._parse_byte_string()
        else:
            raise Exception('Invalid character detected at position %d : %s' % (self._pointer, str(cur_char)))

    def _parse_dictionary(self):
        """    Parses a Bencoded Dictionary type of format d<pairs>e

        All pairs consist of ByteString key followed by any valid data type
        """
#        self._debug('Dictionary')
        self._pointer += 1  # Consume the 'd' start character
        be_dict = {}
        while self._ben_string[self._pointer] != 'e':
            key = self._parse_byte_string()   # Skipping local decode, because key must be a byte string
            val = self._local_decode()
            be_dict[key] = val
        self._pointer += 1  # Consume the 'e' termination character
        return be_dict

    def _parse_list(self):
        """ 
        Parses a Bencoded List type of format l<contents>e
        
        All members of the list as simply appended together in Bencode format to make up <contents>
        """
#        self._debug('List')
        self._pointer += 1  # Consume the 'l' start character
        val = []
        
        while self._ben_string[self._pointer] != 'e':
            val.append(self._local_decode())
        
        self._pointer += 1 # Consume the 'e' termination character
        return val

    def _parse_integer(self):
        """ 
        Parses a Bencoded Integer type of format i<number>e
        """
        self._pointer += 1  # Consume the 'i' start character
        
        mult = 1  # Sign multiplier to handle positive/negative

        # Check for negative number
        if self._ben_string[self._pointer] == '-':
            mult = -1
            self._pointer += 1  # Consume the '-' character
        return self._get_number('e') * mult

    def _get_number(self, end_char):
        """ 
        Returns number in string up to termination character given. 
        """
        
        num = 0
        while self._ben_string[self._pointer] != end_char:
            num = num*10 + int(self._ben_string[self._pointer])
            self._pointer += 1
        self._pointer += 1  # Consume the 'e' termination character
        return num
        
    def _parse_byte_string(self):
        """
        Parses a Bencoded Byte String type of format <len>:<byte string> 
        """

        str_len = self._get_number(':')
        byte_string = self._ben_string[self._pointer:self._pointer + str_len]
        self._pointer += str_len  # Consume the byte string
        return byte_string


    
# Unit Tests
if __name__ == '__main__':

    def test_gen(test_name, result, expected):
        if result == expected:
            print 'PASSED ' + test_name
            return True
        else:
            print '#############'
            print 'FAILED ' + test_name
            print '#############'
            print 'Expected: ' + str(expected)
            print 'Decoded: ' + str(result)
            print ''
            return False
    
    def test_de(test_name, str_be, expected):
        return test_gen(test_name, bd.decode(str_be), expected)

    def test_en(test_name, str_be, expected):
        return test_gen(test_name, bd.encode(str_be), expected)
            
    bd = Bencode()
    torrentData = {'announce':'http://tracker.thepiratebay.org/announce','announce-list':[['http://tracker.thepiratebay.org/announce'],['udp://tracker.thepiratebay.org:80/announce'],['udp://tracker.openbittorrent.com:80/announce'],['http://tracker.publicbt.com/announce'],['udp://tracker.publicbt.com:80/announce'],['http://denis.stalker.h3q.com:6969/announce'],['udp://denis.stalker.h3q.com:6969/announce']],'comment':'Torrent downloaded from http://thepiratebay.org','creation date':1289880809,'info':{'length':365980952,'name':'Hawaii.Five-0.2010.S01E09.HDTV.XviD-LOL.[VTV].avi','piece length':1048576,'pieces':'0'}}
    torrentString = 'd8:announce40:http://tracker.thepiratebay.org/announce13:announce-listll40:http://tracker.thepiratebay.org/announceel42:udp://tracker.thepiratebay.org:80/announceel44:udp://tracker.openbittorrent.com:80/announceel36:http://tracker.publicbt.com/announceel38:udp://tracker.publicbt.com:80/announceel42:http://denis.stalker.h3q.com:6969/announceel41:udp://denis.stalker.h3q.com:6969/announceee7:comment47:Torrent downloaded from http://thepiratebay.org13:creation datei1289880809e4:infod6:lengthi365980952e4:name49:Hawaii.Five-0.2010.S01E09.HDTV.XviD-LOL.[VTV].avi12:piece lengthi1048576e6:pieces1:0ee'

    print '\nEncoding Tests'
    test_en('String', 'abcde', '5:abcde')
    test_en('Empty String', '', '0:')
    test_en('Integer (zero)', 0, 'i0e')
    test_en('Integer (negative)', -1234, 'i-1234e')
    test_en('Integer (positive)', 1234, 'i1234e')
    test_en('Float (negative)', -1234.567, 'i-1234e')
    test_en('Float (positive)', 1234.567, 'i1234e')
    test_en('Simple List', ['abcde', 12345], 'l5:abcdei12345ee')
    test_en('Simple Tuple', ('abcde', 12345), 'l5:abcdei12345ee')
    test_en('Simple Dictionary', {'akey':'mydata', 'key':123}, 'd4:akey6:mydata3:keyi123ee')
    test_en('Complex List', ['abcde', {'ab': ['qw', 123]}], 'l5:abcded2:abl2:qwi123eeee')
    test_en('Complex Dictionary', {'akey': 'mydata', 'key': 123, 'list': ['abc', {'def': 123}], 'int': 123},
            'd4:akey6:mydata3:inti123e3:keyi123e4:listl3:abcd3:defi123eeee')
    test_en('Embedded Dictionary', {'a': {'b': {'c': 'd'}}}, 'd1:ad1:bd1:c1:deee')
    test_en('List after ByteString end in e', {'bcde': [123, 456]}, 'd4:bcdeli123ei456eee')
    test_en('Torrent', torrentData, torrentString)
    
    # Decoding
    print '\nDecoding Tests'
    test_de('String','5:abcde','abcde')
    test_de('Empty String','0:','')
    test_de('Integer (zero)','i0e',0)
    test_de('Integer (negative)','i-1234e',-1234)
    test_de('Integer (positive)','i1234e',1234)
    test_de('Simple List','l5:abcdei12345ee',['abcde',12345])
    test_de('Simple Dictionary','d4:akey6:mydata3:keyi123ee',{'akey':'mydata','key':123})
    test_de('Complex List','l5:abcded2:abl2:qwi123eeee',['abcde',{'ab':['qw',123]}])
    test_de('Complex Dictionary','d4:akey6:mydata3:keyi123e4:listl3:abcd3:defi123eee3:inti123eeee',{'akey':'mydata','key':123,'list':['abc',{'def':123}],'int':123})
    test_de('Embedded Dictionary','d1:ad1:bd1:c1:deee',{'a':{'b':{'c':'d'}}})
    test_de('List after ByteString end in e','d4:bcdeli123ei456eee',{'bcde':[123,456]})
    test_de('Torrent', torrentString, torrentData)
    
