#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Merge v. 0.1
# Merges two PDFs 

import sys
import os
import Quartz as Quartz
from Foundation import NSURL, kCFAllocatorDefault
from AppKit import NSSavePanel, NSApp

# OPTIONS
# Change this filepath to the PDF you want to use a letterhead / template:
watermark = os.path.expanduser("/Users/davide/Desktop/documentazione/watermark.pdf")
watermark90 = os.path.expanduser("/Users/davide/Desktop/documentazione/watermark90.pdf")
destination = os.path.expanduser("/Users/davide/Desktop/documentazione/watermarked") # Default destination
suffix = " - wm.pdf" # Use ".pdf" if no actual suffix required.

# FUNCTIONS

def save_dialog(directory, filename):
	panel = NSSavePanel.savePanel()
	panel.setTitle_("Save PDF booklet")
	myUrl = NSURL.fileURLWithPath_isDirectory_(directory, True)
	panel.setDirectoryURL_(myUrl)
	panel.setNameFieldStringValue_(filename)
	NSApp.activateIgnoringOtherApps_(True)
	ret_value = panel.runModal()
	if ret_value:
		return panel.filename()
	else:
		return ''

# Loads in PDF document
def createPDFDocumentWithPath(path):
	return Quartz.CGPDFDocumentCreateWithURL(Quartz.CFURLCreateFromFileSystemRepresentation(kCFAllocatorDefault, path.encode('utf8'), len(path), False))

# Creates a Context for drawing
def createOutputContextWithPath(path, dictarray):
	url = Quartz.CFURLCreateFromFileSystemRepresentation(None, path.encode('utf8'), len(path), False)
	return Quartz.CGPDFContextCreateWithURL(url, None, dictarray)
	
# Gets DocInfo from input file to pass to output.
# PyObjC returns Keywords in an NSArray; they must be tupled.
def getDocInfo(file):
	pdfURL = NSURL.fileURLWithPath_(file)
	pdfDoc = Quartz.PDFDocument.alloc().initWithURL_(pdfURL)
	if pdfDoc:
		metadata = pdfDoc.documentAttributes()
		if "Keywords" in metadata:
			keys = metadata["Keywords"]
			mutableMetadata = metadata.mutableCopy()
			mutableMetadata["Keywords"] = tuple(keys)
			return mutableMetadata
		else:
			return metadata

def main(argv):
	pathToDir = argv[0]

	for fileName in os.listdir(pathToDir):
		ext = os.path.splitext(fileName)[1]
		name = os.path.splitext(fileName)[0]
		if ext == '.pdf':
			process(os.path.join(pathToDir,fileName))

def process(pathToFile):
	fileName = os.path.split(pathToFile)[1]
	shortName = os.path.splitext(fileName)[0]
	# If you want to save to a consistent location, use:
	writeFilename = os.path.join(destination, shortName + suffix)
	#writeFilename = save_dialog(destination, shortName + suffix)
	shortName = os.path.splitext(pathToFile)[0]
	metaDict = getDocInfo(pathToFile)
	writeContext = createOutputContextWithPath(writeFilename, metaDict)
	readPDF = createPDFDocumentWithPath(pathToFile)
	mergePDF = createPDFDocumentWithPath(watermark)
	mergePDF90 = createPDFDocumentWithPath(watermark90)
	
	if writeContext != None and readPDF != None:
		numPages = Quartz.CGPDFDocumentGetNumberOfPages(readPDF)
		for pageNum in range(1, numPages + 1):	
			page = Quartz.CGPDFDocumentGetPage(readPDF, pageNum)
			
			if page:
				mediaBox = Quartz.CGPDFPageGetBoxRect(page, Quartz.kCGPDFMediaBox)
				if Quartz.CGRectIsEmpty(mediaBox):
					mediaBox = None			
				

				if mediaBox.size.width > mediaBox.size.height:
					w = mediaBox.size.width
					h = mediaBox.size.height
					mediaBox.size.width = h
					mediaBox.size.height = w	


				Quartz.CGContextBeginPage(writeContext, mediaBox)
				Quartz.CGContextSaveGState(writeContext)
				m = Quartz.CGPDFPageGetDrawingTransform(page, Quartz.kCGPDFMediaBox, mediaBox, 0 ,True)
				Quartz.CGContextClipToRect(writeContext,mediaBox)
				Quartz.CGContextConcatCTM(writeContext, m)

				Quartz.CGContextSetBlendMode(writeContext, Quartz.kCGBlendModeNormal)
				Quartz.CGContextDrawPDFPage(writeContext, page)
				Quartz.CGContextRestoreGState(writeContext)

				# if mediaBox.size.width > mediaBox.size.height:
				# 	mergepage = Quartz.CGPDFDocumentGetPage(mergePDF90, 1)
				# 	print(" ROTATED")
				# else:
				mergepage = Quartz.CGPDFDocumentGetPage(mergePDF, 1)

				Quartz.CGContextDrawPDFPage(writeContext, mergepage)
				Quartz.CGContextEndPage(writeContext)
		Quartz.CGPDFContextClose(writeContext)
		del writeContext
			
	else:
		print("A valid input file and output file must be supplied.")
		sys.exit(1)

if __name__ == "__main__":
	main(sys.argv[1:])
