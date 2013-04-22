'''
This is a tool to convert rst file to xml file'.
Srt file is converted to utf-8 encoding, sorted by start time, and converted to xml format.
How to use:
$ python srt_to_xml.py filename
'''
import re
from xml.etree import ElementTree as ET
import sys
import os.path
from collections import OrderedDict
from StringIO import StringIO
import os


def read_srt(input_file_object):
    '''
    Convert rst file object to a list of dialogues.
    A dialogue structure:  {'id': 1, 'start_time': 275, 'end_time': 600, 'subtitle': [line1, line2, ...]}
    start_time and end_time are in miniseconds.
    Parameter:
        input_file_object: file object type.
    Return:
        type: list.
        value: a list of dialogue.
    '''
    dialogue_list = []
    # variable i is the line number of in one dialogue.
    i = 0
    lines = input_file_object.readlines()
    subtitle = []
    dialogue = OrderedDict([('id', 0), ('start_time', 0), ('end_time', 0), ('subtitle', [])])
    for line in lines:
        i += 1
        line = line.strip()
        # check blank line.
        if line:
            if i == 1:
                dialogue['id'] = int(line)
            elif i == 2:
                pattern = re.compile(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})')
                time = re.findall(pattern, line)
                start_time = int(time[0][0]) * 3600000 + int(time[0][1]) * 60000 + int(time[0][2]) * 1000 + int(time[0][3])
                dialogue['start_time'] = start_time
                end_time = int(time[1][0]) * 3600000 + int(time[1][1]) * 60000 + int(time[1][2]) * 1000 + int(time[1][3])
                dialogue['end_time'] = end_time
            else:
                subtitle.append(line)
        else:
            dialogue['subtitle'] = subtitle
            if dialogue['id'] != 0:
                dialogue_list.append(dialogue)
            subtitle = []
            dialogue = OrderedDict([('id', 0), ('start_time', 0), ('end_time', 0), ('subtitle', [])])
            i = 0
    dialogue['subtitle'] = subtitle
    if dialogue['id'] != 0:
        dialogue_list.append(dialogue)
    # sort all dialogues by start time.
    dialogue_list.sort(key=lambda d: d['start_time'])
    return dialogue_list


def generate_xml(dialogue_list):
    xml = ET.Element('xml')
    for dialogue in dialogue_list:
        dia = ET.SubElement(xml, 'dia')
        st = ET.SubElement(dia, 'st')
        et = ET.SubElement(dia, 'et')
        sub = ET.SubElement(dia, 'sub')
        st.text = unicode(dialogue['start_time'])
        et.text = unicode(dialogue['end_time'])
        # join subtitles with newline.
        sub.text = unicode('\n'.join(dialogue['subtitle']), encoding='utf-8')
        # sub.text = unicode('&#x000A;'.join(dialogue['subtitle']), encoding='utf-8')
    xml_tree = ET.ElementTree(xml)
    return xml_tree


def main():
    input_path = os.path.abspath(sys.argv[1])
    # Output file is created in the same directory as input file.
    dir_path = os.path.dirname(input_path)
    output_path = os.path.join(dir_path, 'output.xml')
    input_file_object = open(input_path, 'rb')
    # import zh_to_utf8.
    zh_to_utf8_path = os.path.join(os.path.dirname(dir_path), 'zh_to_utf8')
    sys.path.append(zh_to_utf8_path)
    from zh_to_utf8 import zh_to_utf8
    utf8_string = zh_to_utf8(input_file_object)
    input_file_object.close()
    utf8_file_object = StringIO(utf8_string)
    dialogue_list = read_srt(utf8_file_object)
    utf8_file_object.close()
    xml_tree = generate_xml(dialogue_list)
    xml_tree.write(output_path, encoding='utf-8')
    print 'Succeed!'
    print 'Output file path is ' + output_path
    return


if __name__ == '__main__':
    main()
