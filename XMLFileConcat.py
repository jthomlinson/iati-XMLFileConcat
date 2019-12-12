import sys
import getopt
import pathlib
import regex as re
import codecs


import xml.etree.ElementTree
import defusedxml.cElementTree as ET
import xml.etree.cElementTree as oET



class XMLFileConcat:

    def __init__(self, sourcePath, outFile, filter, tag):
        self.filter = filter
        self.tag = tag
        self.sourcePath = sourcePath
        self.outFileName = outFile
        
        
    def getFileCount(self, path, count = 0):
        for item in path.iterdir():
            if item.is_dir() and not(item.is_symlink()):
                count = self.getFileCount(item, count)
            else:
                if item.is_file():
                    if re.search('\.xml$', item.name):
                        count += 1
        return count
        
    def outputCount(self):
        count = self.getFileCount(self.sourcePath)

        if (self.outFileName):
            with codecs.open(self.outFileName, 'w', encoding = 'utf-8') as handle:
                handle.write(f"{count}\n")
        else:
            sys.stdout.write(f"{count}\n")

    def outputList(self, path = None, handle = None):
        if (path == None):
            path = self.sourcePath
            
        inHandle = handle
            
        if (inHandle == None):
            if (self.outFileName):
                handle = codecs.open(self.outFileName, 'w', encoding = 'utf-8')
            else:
                handle = sys.stdout

        for item in path.iterdir():
            if item.is_file():
                if re.search('\.xml$', item.name):
                    handle.write(f"{item.name}\n")

        for item in path.iterdir():
            if item.is_dir() and not(item.is_symlink()):
                self.outputList(item, handle)

        if (inHandle == None) and (handle is not sys.stdout):
            handle.close()


    def concat(self):
        match, not_match, parse_error, count = 0, 0, 0, 0
        tag_dict = {}
        if self.tag == None:
            root = oET.Element("root")
        else:
            root = oET.Element(self.tag)
        for item in self.sourcePath.rglob('*.xml'):
            if item.is_file():
                count += 1
                try:
                    loadTree = ET.parse(item)
                except xml.etree.ElementTree.ParseError as exp:
                    parse_error += 1
                    print('Parse error:', exp)
                else:
                    graft = loadTree.getroot()
                    if graft.tag in tag_dict:
                        tag_dict[graft.tag] = tag_dict[graft.tag] + 1
                    else:
                        tag_dict[graft.tag] = 1
#                        'iati-organisations' or 'iati-activities'
                    if self.filter == None:
                        root.append(graft)
                        match += 1
                    else:
                        if self.filter == graft.tag:
                            root.append(graft)
                            match += 1
                        else:
                            not_match += 1
        tree = oET.ElementTree(root)
        if self.outFileName == None:
            tree.write(sys.stdout, encoding='unicode', xml_declaration = True)
        else:
            tree.write(self.outFileName, encoding = 'UTF-8', xml_declaration = True)
            print(f'Match = {match} Not match {not_match} Parse failed {parse_error} Total {count}')
            for x in tag_dict:
                print('{:-6}     | {}'.format(tag_dict[x], x))




    def report(self):
        match, not_match,count = 0, 0, 0
        start_set = set([])
        start_dict = {}
        for item in self.sourcePath.rglob('*.xml'):
            with open(str(item), 'rb') as f:
                b = f.read(16)
                start_set.add(b)
                if b in start_dict:
                    start_dict[b]['count'] = start_dict[b]['count'] + 1
                else:
                    start_dict[b] = {'count':1, 'roots':{}}
            try:
                tree = ET.parse(item)
                root = tree.getroot()
                if root.tag in start_dict[b]['roots']:
                    start_dict[b]['roots'][root.tag] = start_dict[b]['roots'][root.tag] + 1
                else:
                    start_dict[b]['roots'][root.tag] = 1
                match += 1
            except xml.etree.ElementTree.ParseError as exp:
                print('Parse error:', exp)
                not_match += 1
            except Exception as exp:
                print('Hit Except clause', type(exp))
                raise
               
        print('File count | File starts')
        for x in start_dict:
            print('{:-6}     | {}  Roots: {}'.format(start_dict[x]['count'], x, len(start_dict[x]['roots'])))
            for y in start_dict[x]['roots']:
                print('------ {:-6}  {} '.format(start_dict[x]['roots'][y], y))

        print(f'\nGood {match}, Bad {not_match}, Total {match + not_match}')





def argToPath(inputPath):
    path = pathlib.Path(inputPath)
    if not(path.is_dir()):
        sys.stderr.write(f"Error: {inputPath} is not a valid directory")
        sys.exit(2)
    return path

            
def main(argv):
    usage = '''
Usage:
python XMLFileConcat.py [-h | -c | -l | -r] | [-f <tag> -o <outputfile> -t <tag>] <inputpath>
Operation:
The code searches the directory structure below the specified input path location for files with the .xml file extension. Each file is parsed to check that it contains well-formed XLM. An output XML string is created composed of a new root tag followed by the contents of each of the files read in. If no output file is specified, the XML string is written to stdout. If the -o option is used the string is written to the specified filename. The output is written in UTF-8 format. By default, the root tag of the output XML is \'root\'. A different name for the root tag can be specified by using the -t option. By default, the contents of all well-formed XML files is sent to the output. However, the -f option can be used filter the files so that only those having a specific root tag, e.g. 'iati-activities' or 'iati-organisations', will be written to the output.

Options:
-h\tDisplay this help text
-l\tList XML files found searching down the directory structure from the specified input path locacation. The files are not opened.
-c\tCount XML files found searching down the directory structure from the specified input path locacation. The files are not opened.
-r\tWrite out a report listing the different character strings found at the start of each of the files and the number of occurrences of each string.
'''

    filter = None
    outputFile = None
    tag = None
    
    switches = {'help':False, 'count':False, 'list':False, 'report':False}
    
    try:
        opts, args = getopt.getopt(argv, 'hcf:lo:rt:', ["help", "count", "filter=", "list", "ofile=", "report", "tag=" ])
    except getopt.GetoptError:
        print("Usage:")
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
#        print(opt, arg)
        if opt == '-h':
            print(usage)
            exit(0)
        elif opt in ("-c", "--count"):
            switches['count'] = True
        elif opt in ("-f", "--filter"):
            filter = arg
        elif opt in ("-l", "--list"):
            switches['list'] = True
        elif opt in ("-o", "--ofile"):
            outputFile = arg
        elif opt in ("-r", "--report"):
            switches['report'] = True
        elif opt in ("-t", "--tag"):
            tag = arg
    
    path = argToPath(args[0])
        
    fConcat = XMLFileConcat(path, outputFile, filter, tag)

#    print(switches)
#    exit(0)
    if (switches['help']):
        print(usage )
        sys.exit()
    elif (switches['count']) or (switches['list']) or (switches['report']):
        if (switches['count']):
            fConcat.outputCount()
            
        if (switches['list']):
            fConcat.outputList()
        
        if (switches['report']):
            fConcat.report()
    else:
        fConcat.concat()


if (__name__ == '__main__'):
    main(sys.argv[1:])
