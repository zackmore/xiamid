# -*- coding: utf-8 -*-
#
# TODO:
# 1.Get single file info and save as filename.
# 2.Album download.
# 3.Artist download.

import pdb

import BeautifulSoup
import requests
import argparse
import urllib

URL_single_prefix = 'http://www.xiami.com/song/playlist/id/'


class SingleDownload(object):
    def __init__(self, sid):
        self.sid = sid
        self.xml_url = URL_single_prefix + str(sid)
        self.encoded_url = ''
        self.url = ''
        self.info = {}

    def get_xml(self):
        request_headers = {'User-Agent': 'Wget/1.12'}
        xml_response = requests.get(self.xml_url, headers = request_headers)

        if xml_response.status_code != 200:
            print 'Could not get the url.'
            return False
        xml_file = xml_response.text

        soup = BeautifulSoup.BeautifulSoup(xml_file)
        encoded_url_el = soup.find('location')
        self.encoded_url = encoded_url_el.text

        self.info['title'] = soup.find('title').text
        self.info['album'] = soup.find('album_name').text
        self.info['artist'] = soup.find('artist').text

        return self.encoded_url

    def decode_url(self):
        def URL_matrix(URL):
            rows = int(URL[0])
            mess_text = URL[1:]
            text_index = 0
            matrix = []

            for r in range(rows):
                matrix.append([])
            cols = len(mess_text) / rows

            if len(mess_text) % rows != 0:
                big_rows = len(mess_text) % rows
                big_cols = cols + 1
            for r in range(rows):
                try:
                    big_rows
                except NameError:
                    for c in range(cols):
                        matrix[r].append(mess_text[text_index])
                        text_index += 1
                else:
                    if r < big_rows:
                        for c in range(big_cols):
                            matrix[r].append(mess_text[text_index])
                            text_index += 1
                    else:
                        for c in range(cols):
                            matrix[r].append(mess_text[text_index])
                            text_index += 1
            return matrix

        def matrix_to_url(matrix):
            if type(matrix[0]) != type([]):
                print 'Invalid 2D matrix.'
                return False

            url = ''
            index = 0
            cols = len(matrix[0])

            for col in range(cols):
                for row in matrix:
                    try:
                        url += row[index]
                    except:
                        continue
                index +=1
            url = urllib.unquote(url)
            return url.replace('^', '0')

        matrix = URL_matrix(self.encoded_url)
        self.url = matrix_to_url(matrix)
        return self.url

    def download_file(self):
        self.get_xml()
        self.decode_url()

        local_filename = self.info['title'] + ' - ' +\
                        self.info['album'] + ' - ' +\
                        self.info['artist'] + '.' +\
                        self.url.split('.')[-1]
        r = requests.get(self.url, stream = True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        return local_filename


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Xiami mp3 download.')
    parser.add_argument('-s', dest='sid', type=int, help='Single song id')
    args = parser.parse_args()

    d = SingleDownload(args.sid)
    d.download_file()

