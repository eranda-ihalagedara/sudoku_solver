import cv2 as cv
from imutils import contours
import numpy as np
import pytesseract
import pickle

pytesseract.pytesseract.tesseract_cmd =  'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def extract_puzzle(fname):
    # Load image, grayscale, and adaptive threshold
    image = cv.imread(fname)
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    thresh = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV,11, 10)

    cnts, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    puzzle_border = []
    
    for c in cnts:
        area = cv.contourArea(c)
        c_len = cv.arcLength(c, True)
        poly = cv.approxPolyDP(c, 0.02*c_len, True)
        # if area < 1000:
        if len(poly)==4 and area> 100000:
            puzzle_border.append(poly)
    
    if len(puzzle_border)!=1:
        print("Make the image narrowly enclose the puzzle border")
        return None
        
    cells = get_cell_contours(puzzle_border[0])
    puzzle_array = np.zeros([9,9], dtype = int)
    
    for i in range(81):
        y1,x1, dy,dx = cv.boundingRect(cells[i])
        cell_image = 255 - thresh[x1:x1+dx,y1:y1+dy]
        cell_image= cv.copyMakeBorder(cell_image,10,10,10,10,cv.BORDER_CONSTANT,value=(255,255,255))
        cell_value = get_digit(cell_image)
        puzzle_array[i//9,i%9]=cell_value

    return puzzle_array


def get_cell_contours(border):
    x0 = border[0][0][0]
    y0 = border[0][0][1]
    
    dx = (border[3][0][0] - border[0][0][0])/9
    dy = (border[1][0][1] - border[0][0][1])/9
    
    cells = []
    pdx = 0.075*dx # padding
    pdy = 0.075*dy # padding
    
    for i in range(9):
        for j in range(9):
            cell = np.array([[[x0 + j*dx + pdx, y0 + i*dy + pdy]], [[x0 + j*dx + pdx, y0 + (i+1)*dy - pdy]], [[x0 + (j+1)*dx - pdx, y0 + (i+1)*dy - pdy]], [[x0 + (j+1)*dx - pdx, y0 + i*dy + pdy]]])
            cell = np.around(cell).astype(np.int32)
            cells.append(cell)
            
    return cells

def get_digit(img):
    cell_text = pytesseract.image_to_string(img, lang="eng",config='--psm 10 --oem 3 tessedit_char_whitelist=0123456789')
    cell_digits = [int(c) for c in cell_text if c.isdigit()]

    if len(cell_digits)==1:
        return cell_digits[0]
    else:
        return 0

