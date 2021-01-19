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
import os.path

languages = []

def cleanTocFile(language, tocCounter):
    path = './content/{0}/books/handbook/toc-{1}.adoc'.format(language, tocCounter)
    if os.path.exists(path):
        tocFile = open(path, 'r+', encoding = 'utf-8')
        tocFile.truncate(0)

def appendCommendAndTitle(language, tocCounter, tocContent):
  toc =  "// Code generated by the FreeBSD Documentation toolchain. DO NOT EDIT.\n"
  toc += "// Please don't change this file manually but run `make` to update it.\n"
  toc += "// For more information, please read the FreeBSD Documentation Project Primer\n\n"
  toc += "[.toc]\n"
  toc += "--\n"
  toc += '[.toc-title]\n'
  toc += setTOCTitle(language) + '\n\n'
  toc += tocContent
  toc += "--\n"

  tocFile = open('./content/{0}/books/handbook/toc-{1}.adoc'.format(language, tocCounter), 'a+', encoding = 'utf-8')
  tocFile.write(toc)

def checkIsPart(chapter):
  if "part" in chapter:
    return True
  return False

def checkIsPreface(chapterContent):
  if "[preface]" in chapterContent:
    return True
  return False

def checkIsAppendix(chapterContent):
  if "[appendix]" in chapterContent:
    return True
  return False

def setAppendixTitle(language):
  languages = {
    'en': 'Appendix',
    'de': 'Anhang',
    'el': 'Παράρτημα',
    'es': 'Apéndice',
    'fr': 'Annexe',
    'hu': 'függelék',
    'it': 'Appendice',
    'ja': '付録',
    'mn': 'Хавсралт',
    'nl': 'Bijlage',
    'pl': 'Dodatek',
    'pt_BR': 'Apêndice',
    'ru': 'Приложение',
    'zh_CN': '附录',
    'zh_TW': '附錄'
  }

  return languages.get(language)

def setChapterTitle(language):
  languages = {
    'en': 'Chapter',
    'de': 'Kapitel',
    'el': 'Κεφάλαιο',
    'es': 'Capítulo',
    'fr': 'Chapitre',
    'hu': 'Fejezet',
    'it': 'Capitolo',
    'ja': '章',
    'mn': 'Бүлэг',
    'nl': 'Hoofdstuk',
    'pl': 'Rozdział',
    'pt_BR': 'Capítulo',
    'ru': 'Глава',
    'zh_CN': '章',
    'zh_TW': '章'
  }

  return languages.get(language)

def setTOCTitle(language):
  languages = {
    'en': 'Table of Contents',
    'de': 'Inhaltsverzeichnis',
    'el': 'Πίνακας Περιεχομένων',
    'es': 'Tabla de contenidos',
    'fr': 'Table des matières',
    'hu': 'Tartalom',
    'it': 'Indice',
    'ja': '目次',
    'mn': 'Гарчиг',
    'nl': 'Inhoudsopgave',
    'pl': 'Spis treści',
    'pt_BR': 'Índice',
    'ru': 'Содержание',
    'zh_CN': '目录',
    'zh_TW': '內容目錄'
  }

  return languages.get(language)

def main(argv):

  try:
    opts, args = getopt.getopt(argv,"hl:",["language="])
  except getopt.GetoptError:
    print('handbook-toc-creator.py -l <language>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print('handbook-toc-creator.py -l <language>')
      sys.exit()
    elif opt in ("-l", "--language"):
      languages = arg.split(',')

  for language in languages:
    with open('./content/{}/books/handbook/chapters-order.adoc'.format(language), 'r', encoding = 'utf-8') as chaptersFile:
      chapters = [line.strip() for line in chaptersFile]

    chapterCounter = 1
    subChapterCounter = 1
    partCounter = 0
    toc = ""

    for chapter in chapters:
      with open('./content/{0}/books/handbook/{1}'.format(language, chapter), 'r', encoding = 'utf-8') as chapterFile:
        chapterContent = chapterFile.read().splitlines()
        chapterFile.close()
        chapter = chapter.replace("/_index.adoc", "").replace(".adoc", "")

        if checkIsPart(chapter):

          if partCounter > 0:
            cleanTocFile(language, partCounter)
            appendCommendAndTitle(language, partCounter, toc)
            toc = "" # Clean toc content

          partCounter += 1

        elif checkIsPreface(chapterContent):
          pass

        elif checkIsAppendix(chapterContent):
          for lineNumber, chapterLine in enumerate(chapterContent, 1):

            if (re.match(r"^={1} [^\n]+", chapterLine)):
              toc += "* link:../{0}[{1} {2}]\n".format(chapter, setAppendixTitle(language), chapterLine.replace("=", "").strip())

            elif (re.match(r"^={2} [^\n]+", chapterLine)):
              toc += "** link:../{0}/#{1}[{2}]\n".format(chapter, chapterContent[lineNumber-2].replace("[[", "").replace("]]", ""), chapterLine.replace("==", "").lstrip())

        else:
          for lineNumber, chapterLine in enumerate(chapterContent, 1):

            if re.match(r"^={1} [^\n]+", chapterLine):
              toc += "* link:../{0}[{1} {2}. {3}]\n".format(chapter, setChapterTitle(language), chapterCounter, chapterLine.replace("=", "").strip())

            elif re.match(r"^={2} [^\n]+", chapterLine):
              toc += "** link:../{0}/#{1}[{2}.{3}. {4}]\n".format(chapter, chapterContent[lineNumber-2].replace("[[", "").replace("]]", ""), chapterCounter, subChapterCounter, chapterLine.replace("==", "").lstrip())
              subChapterCounter += 1

          chapterCounter += 1
          subChapterCounter = 1 # Reset subChapterCounter

    cleanTocFile(language, partCounter)
    appendCommendAndTitle(language, partCounter, toc) # For the last part

if __name__ == "__main__":
  main(sys.argv[1:])
