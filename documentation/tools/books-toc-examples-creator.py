# -*- coding: utf-8 -*-
"""
BSD 2-Clause License

Copyright (c) 2020-2021, The FreeBSD Project
Copyright (c) 2020-2021, Sergio Carlavilla <carlavilla@FreeBSD.org>

This script will generate the Table of Contents of the Handbook
"""
#!/usr/bin/env python3

import sys, getopt
import re

languages = []

"""
To determine if a chapter is a chapter we are going to check if it is
anything else, an appendix, a part, the preface ... and if it is not
any of those, it will be a chapter.

It may not be the best option, but it works :)
"""
def checkIsChapter(chapter, chapterContent):
  if "part" in chapter:
    return False
  elif "[preface]" in chapterContent:
    return False
  elif "[appendix]" in chapterContent:
    return False
  else:
    return True

def setTOCTitle(language):
  languages = {
    'en': 'List of Examples',
    'de': 'Liste der Beispiele',
    'el': 'Κατάλογος Παραδειγμάτων',
    'es': 'Lista de ejemplos',
    'fr': 'Liste des exemples',
    'hu': 'A példák listája',
    'it': 'Lista delle tabelle',
    'ja': '例の一覧',
    'mn': 'Жишээний жагсаалт',
    'nl': 'Lijst van voorbeelden',
    'pl': 'Spis przykładów',
    'pt_BR': 'Lista de Exemplos',
    'ru': 'Список примеров',
    'zh_CN': '范例清单',
    'zh_TW': '範例目錄'
  }

  return languages.get(language)

def main(argv):

  try:
    opts, args = getopt.getopt(argv,"hl:",["language="])
  except getopt.GetoptError:
    print('handbook-toc-examples-creator.py -l <language>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print('handbook-toc-examples-creator.py -l <language>')
      sys.exit()
    elif opt in ("-l", "--language"):
      languages = arg.split(',')

  for language in languages:
    with open('./content/{}/books/handbook/chapters-order.adoc'.format(language), 'r', encoding = 'utf-8') as chaptersFile:
      chapters = [line.strip() for line in chaptersFile]

    toc =  "// Code generated by the FreeBSD Documentation toolchain. DO NOT EDIT.\n"
    toc += "// Please don't change this file manually but run `make` to update it.\n"
    toc += "// For more information, please read the FreeBSD Documentation Project Primer\n\n"
    toc += "[.toc]\n"
    toc += "--\n"
    toc += '[.toc-title]\n'
    toc += setTOCTitle(language) + '\n\n'

    chapterCounter = 1
    exampleCounter = 1
    for chapter in chapters:
      with open('./content/{0}/books/handbook/{1}'.format(language, chapter), 'r', encoding = 'utf-8') as chapterFile:
        chapterContent = chapterFile.read().splitlines()
        chapterFile.close()
        chapter = chapter.replace("/_index.adoc", "").replace(".adoc", "")

        exampleId = ""
        exampleTitle = ""
        for lineNumber, chapterLine in enumerate(chapterContent, 1):
          if re.match(r"^\[example\]+", chapterLine) and re.match(r"^[.]{1}[^\n]+", chapterContent[lineNumber-2]) and re.match(r"^\[\[[^\n]+\]\]", chapterContent[lineNumber-3]):
              exampleTitle = chapterContent[lineNumber-2]
              exampleId = chapterContent[lineNumber-3]
              toc += "* {0}.{1}  link:{2}#{3}[{4}]\n".format(chapterCounter, exampleCounter, chapter, exampleId.replace("[[", "").replace("]]", ""), exampleTitle[1:])
              exampleCounter += 1
          else:
            exampleId = ""
            exampleTitle = ""

        if checkIsChapter(chapter, chapterContent):
          chapterCounter += 1
        exampleCounter = 1 # Reset example counter

    toc += "--\n"

    with open('./content/{}/books/handbook/toc-examples.adoc'.format(language), 'w', encoding = 'utf-8') as tocFile:
      tocFile.write(toc)

if __name__ == "__main__":
  main(sys.argv[1:])
