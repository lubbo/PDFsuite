#! /usr/bin/python
# coding: utf-8
# by Ben Byram-Wigfield v.1.2
# Script to apply a MacOS Quartz Filter to a PDF file.
# Altered the order of arguments to conform to pre-10.6 Apple command.
# quartzfilter.py filter input output
#
import os, getopt, sys
from Quartz import PDFDocument
from CoreFoundation import (NSURL, QuartzFilter)


def main(argv):
	inputfile = ""
	outputfile = ""
	filter = ""

	try:
		opts, args = getopt.getopt(sys.argv[1:], "ifo", ["input", "filter", "output"])
	except getopt.GetoptError as err:
		print(err)
		usage()
		sys.exit(2)

	if len(args) != 3:
		print("Not enough arguments")
		sys.exit(2)

	inputfile =args[0].decode('utf-8')
	if not inputfile:
		print 'Unable to open input file'
		sys.exit(2)

	filter = args[1].decode('utf-8')
	if not filter:
		print 'Unable to create context filter'
		sys.exit(2)

	outputfile = args[2].decode('utf-8')
	if not outputfile:
		print 'Unable to create output context'
		sys.exit(2)

	pdfURL = NSURL.fileURLWithPath_(inputfile)
	pdfDoc = PDFDocument.alloc().initWithURL_(pdfURL)
	filterURL = NSURL.fileURLWithPath_(filter)
	value = QuartzFilter.quartzFilterWithURL_(filterURL)
	dict = { 'QuartzFilter': value }
	pdfDoc.writeToFile_withOptions_(outputfile, dict)

if __name__ == "__main__":
   main(sys.argv[1:])