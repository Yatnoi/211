# import the necessary packages
from imutils.perspective import four_point_transform
import pytesseract
import argparse
import imutils
import cv2
import re
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input receipt image")
ap.add_argument("-d", "--debug", type=int, default=-1,
	help="whether or not we are visualizing each step of the pipeline")
args = vars(ap.parse_args())
# load the input image from disk, resize it, and compute the ratio
# of the *new* width to the *old* width
orig = cv2.imread(args["image"])
image = orig.copy()
image = imutils.resize(image, width=500)
ratio = orig.shape[1] / float(image.shape[1])
# convert the image to grayscale, blur it slightly, and then apply
# edge detection
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5,), 0)
edged = cv2.Canny(blurred, 75, 200)
# check to see if we should show the output of our edge detection
# procedure
if args["debug"] > 0:
	cv2.imshow("Input", image)
	cv2.imshow("Edged", edged)
	cv2.waitKey(0)
# find contours in the edge map and sort them by size in descending
# order
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
# initialize a contour that corresponds to the receipt outline
receiptCnt = None
# loop over the contours
for c in cnts:
	# approximate the contour
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	# if our approximated contour has four points, then we can
	# assume we have found the outline of the receipt
	if len(approx) == 4:
		receiptCnt = approx
		break
# if the receipt contour is empty then our script could not find the
# outline and we should be notified
if receiptCnt is None:
	raise Exception(("Could not find receipt outline. "
		"Try debugging your edge detection and contour steps."))

# check to see if we should draw the contour of the receipt on the
# image and then display it to our screen
if args["debug"] > 0:
	output = image.copy()
	cv2.drawContours(output, [receiptCnt], -1, (0, 255, 0), 2)
	cv2.imshow("Receipt Outline", output)
	cv2.waitKey(0)
# apply a four-point perspective transform to the *original* image to
# obtain a top-down bird's-eye view of the receipt
receipt = four_point_transform(orig, receiptCnt.reshape(4, 2) * ratio)
# show transformed image
cv2.imshow("Receipt Transform", imutils.resize(receipt, width=500))
cv2.waitKey(0)
# apply OCR to the receipt image by assuming column data, ensuring
# the text is *concatenated across the row* (additionally, for your
# own images you may need to apply additional processing to cleanup
# the image, including resizing, thresholding, etc.)
options = "--psm 4"
text = pytesseract.image_to_string(
	cv2.cvtColor(receipt, cv2.COLOR_BGR2RGB),
	config=options)

#Printing raw
print("[INFO] raw output:")
print("==================")
print(text)
print("\n")

# Assuming 'text' is the OCR output as a string
lines = text.split("\n")
# Regular expression to match lines with a price component at the end
pricePattern = re.compile(r"([0-9]+[., ][0-9]+)")

# Initialize an empty list (matrix) to store our line items
matrix = []

for line in lines:
    match = pricePattern.search(line)
    if match:
        # Extract the description and price from the match groups
        description = str(line)
        price = match.group(1).strip()
        # Append the description and price as a new row in the matrix
        matrix.append([description, price])

for i in range(len(matrix)):
        # Replace commas and spaces with periods in the string
        matrix[i][1] = matrix[i][1].replace(',', '.').replace(' ', '.')
		
for row in matrix:
    print("\t".join(row))

	
ethan = []
darren = []
split = []

for i in range(len(matrix)):
	item = int(input(matrix[i]))
	if item==1:
		ethan.append(matrix[i][1])
	if item==2: 
		darren.append(matrix[i][1])
	if item==3:
		split.append(matrix[i][1])
	if item==4:
		pass

print("-------------")
print(ethan)
print(darren)
print(split)

ethantotal = sum(float(i) for i in ethan)
darrentotal = sum(float(i) for i in darren)
splittotal = sum(float(i) for i in split)

# Print the total
print("Ethan Total:", ethantotal)
print("Darren Total:", darrentotal)
print("We are splitting:", splittotal)