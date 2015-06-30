"""
Bencode handling Class for decoding a .torrent file or other Bencoded data.

Bencode Python Class by Joe Sacher is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
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

class Bencode:
    """    Converts to and from a Bencoded data structure
    """
    
    _BenString = []
    _Pointer = 0

    #
    #  Encoding Methods
    #
    def Encode(self, data):
        """    Returns a Bencoded string describing the data provided
        
        Conversions performed:
        Strings -> Byte Strings
        Integers -> Integers
        Floats -> Integers with truncate
        List -> List
        Tuple -> List
        Dictionary -> Dictionary        
        """
        return self._localEncode(data)
        
    def _localEncode(self, data):
        """    Returns the proper Bencoded string for data given """
        encoders = {'dict':self._encodeDictionary,
                    'list':self._encodeList,
                    'tuple':self._encodeList,
                    'str':self._encodeString,
                    'int':self._encodeInteger,
                    'float':self._encodeFloat}
        dataType = type(data).__name__
        if dataType in encoders.keys():
            return encoders[dataType](data)
        else:
            raise Exception('Encoder is not defined for data type: ' + dataType)
    
    def _encodeString(self, data):
        """ Converts string to Bencoded Byte String """
        return str(len(data)) + ':' + str(data)
        
    def _encodeInteger(self, data):
        """ Converts Integer to Bencoded Integer """
        return 'i' + str(data) + 'e'
    
    def _encodeFloat(self, data):
        """ Converts Float to Bencoded Integer """
        return self._encodeInteger(int(data))
    
    def _encodeList(self, data):
        """    Converts List or Tuple to Bencoded List    """
        ben = 'l'
        for item in data:
            ben += self._localEncode(item)
        ben += 'e'
        return ben
    
    def _encodeDictionary(self, data):
        """ Converts Dictionare to Bencoded Dictionary """
        ben = 'd'
        for key in sorted(data.keys()):
            ben += self._encodeString(key)
            ben += self._localEncode(data[key])
        ben += 'e'
        return ben

    #
    # Decoding Methods
    #    
    
    def _debug(self, location):
        print location + ' - ' + str(self._Pointer) + ' ' + self._BenString[self._Pointer:self._Pointer + 30]
        
    def Decode(self, BenString):
        """ Returns the data structure defined by the Bencoded string """
        try:
            self._BenString = BenString
            self._Pointer = 0
            return self._localDecode()
        except IndexError as e:
            print "Index Error at Pointer = " + str(self._Pointer) + " of " + str(len(self._BenString)) + "\n" + str(e)
    
    def _localDecode(self):
        """ Detects and returns the proper Bencoded data type starting at current Pointer position """
        curChar = self._BenString[self._Pointer]
        if curChar == 'i':
            return self._parseInteger()
        elif curChar == 'l':
            return self._parseList()
        elif curChar == 'd':
            return self._parseDictionary()
        elif curChar in ['-','0','1','2','3','4','5','6','7','8','9']:
            return self._parseByteString()
        else:
            raise Exception('Invalid character detected at position ' + str(self._Pointer) + ': ' + str(curChar))

    def _parseDictionary(self):
        """    Parses a Bencoded Dictionary type of format d<pairs>e

        All pairs consist of ByteString key followed by any valid data type
        """
#        self._debug('Dictionary')
        self._Pointer += 1  # Consume the 'd' start character
        dict = {}
        while self._BenString[self._Pointer] != 'e':
            key = self._parseByteString()   # Skipping local decode, because key must be a byte string
            val = self._localDecode()
            dict[key] = val
        self._Pointer += 1  # Consume the 'e' termination character
        return dict

    def _parseList(self):
        """ Parses a Bencoded List type of format l<contents>e
        
        All members of the list as simply appended together in Bencode format to make up <contents>
        """
#        self._debug('List')
        self._Pointer += 1  # Consume the 'l' start character
        val = []
        
        while self._BenString[self._Pointer] != 'e':
            val.append(self._localDecode())
        
        self._Pointer += 1 # Consume the 'e' termination character
        return val

    def _parseInteger(self):
        """ Parses a Bencoded Integer type of format i<number>e
        """
#        self._debug('Integer')
        self._Pointer += 1 # Consume the 'i' start character
        
        mult = 1 # Sign multiplier to handle positive/negative

        # Check for negative number
        if self._BenString[self._Pointer] == '-':
            mult = -1
            self._Pointer += 1  # Consume the '-' character
        return self._getNumber('e') * mult

    def _getNumber(self, endChar):
        """ Returns number in string up to termination character given. """
        num = 0
        while self._BenString[self._Pointer] != endChar:
            num = num*10 + int(self._BenString[self._Pointer])
            self._Pointer += 1
        self._Pointer += 1  # Consume the 'e' termination character
        return num
        
    def _parseByteString(self):
        """    Parses a Bencoded Byte String type of format <len>:<byte string> """
#        self._debug('ByteString')
        len = self._getNumber(':')
        byteString = self._BenString[self._Pointer:self._Pointer + len]
        self._Pointer += len  # Consume the byte string
        return byteString
    
    
# Unit Tests
if __name__ == '__main__':

    def testGen(TestName, result, expected):
        if result == expected:
            print 'PASSED ' + TestName
            return True
        else:
            print '#############'
            print 'FAILED ' + TestName
            print '#############'
            print 'Expected: ' + str(expected)
            print 'Decoded: ' + str(result)
            print ''
            return False
    
    def testDe(TestName, strBE, expected):
        return testGen(TestName, bd.Decode(strBE), expected)

    def testEn(TestName, strBE, expected):
        return testGen(TestName, bd.Encode(strBE), expected)
            
    bd = Bencode()
    torrentData = {'announce':'http://tracker.thepiratebay.org/announce','announce-list':[['http://tracker.thepiratebay.org/announce'],['udp://tracker.thepiratebay.org:80/announce'],['udp://tracker.openbittorrent.com:80/announce'],['http://tracker.publicbt.com/announce'],['udp://tracker.publicbt.com:80/announce'],['http://denis.stalker.h3q.com:6969/announce'],['udp://denis.stalker.h3q.com:6969/announce']],'comment':'Torrent downloaded from http://thepiratebay.org','creation date':1289880809,'info':{'length':365980952,'name':'Hawaii.Five-0.2010.S01E09.HDTV.XviD-LOL.[VTV].avi','piece length':1048576,'pieces':'0'}}
    torrentString = 'd8:announce40:http://tracker.thepiratebay.org/announce13:announce-listll40:http://tracker.thepiratebay.org/announceel42:udp://tracker.thepiratebay.org:80/announceel44:udp://tracker.openbittorrent.com:80/announceel36:http://tracker.publicbt.com/announceel38:udp://tracker.publicbt.com:80/announceel42:http://denis.stalker.h3q.com:6969/announceel41:udp://denis.stalker.h3q.com:6969/announceee7:comment47:Torrent downloaded from http://thepiratebay.org13:creation datei1289880809e4:infod6:lengthi365980952e4:name49:Hawaii.Five-0.2010.S01E09.HDTV.XviD-LOL.[VTV].avi12:piece lengthi1048576e6:pieces1:0ee'

    print '\nEncoding Tests'
    testEn('String','abcde','5:abcde')
    testEn('Empty String','','0:')
    testEn('Integer (zero)',0,'i0e')
    testEn('Integer (negative)',-1234,'i-1234e')
    testEn('Integer (positive)',1234,'i1234e')
    testEn('Float (negative)',-1234.567,'i-1234e')
    testEn('Float (positive)',1234.567,'i1234e')
    testEn('Simple List',['abcde',12345],'l5:abcdei12345ee')
    testEn('Simple Tuple',('abcde',12345),'l5:abcdei12345ee')
    testEn('Simple Dictionary',{'akey':'mydata','key':123},'d4:akey6:mydata3:keyi123ee')
    testEn('Complex List',['abcde',{'ab':['qw',123]}],'l5:abcded2:abl2:qwi123eeee')
    testEn('Complex Dictionary',{'akey':'mydata','key':123,'list':['abc',{'def':123}],'int':123},'d4:akey6:mydata3:inti123e3:keyi123e4:listl3:abcd3:defi123eeee')
    testEn('Embedded Dictionary',{'a':{'b':{'c':'d'}}},'d1:ad1:bd1:c1:deee')
    testEn('List after ByteString end in e',{'bcde':[123,456]},'d4:bcdeli123ei456eee')
    testEn('Torrent', torrentData, torrentString)
    
    # Decoding
    print '\nDecoding Tests'
    testDe('String','5:abcde','abcde')
    testDe('Empty String','0:','')
    testDe('Integer (zero)','i0e',0)
    testDe('Integer (negative)','i-1234e',-1234)
    testDe('Integer (positive)','i1234e',1234)
    testDe('Simple List','l5:abcdei12345ee',['abcde',12345])
    testDe('Simple Dictionary','d4:akey6:mydata3:keyi123ee',{'akey':'mydata','key':123})
    testDe('Complex List','l5:abcded2:abl2:qwi123eeee',['abcde',{'ab':['qw',123]}])
    testDe('Complex Dictionary','d4:akey6:mydata3:keyi123e4:listl3:abcd3:defi123eee3:inti123eeee',{'akey':'mydata','key':123,'list':['abc',{'def':123}],'int':123})
    testDe('Embedded Dictionary','d1:ad1:bd1:c1:deee',{'a':{'b':{'c':'d'}}})
    testDe('List after ByteString end in e','d4:bcdeli123ei456eee',{'bcde':[123,456]})
    testDe('Torrent', torrentString, torrentData)
    
