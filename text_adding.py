import cv2
import random
import sys
import argparse
from ast import literal_eval
from math import floor

parser = argparse.ArgumentParser(description='Video Text Adding')
parser.add_argument('video', type=str, help='path of the video')
parser.add_argument('-d', '--duration', default=0.5, type=float, help='text duration in seconds')
parser.add_argument('-t', '--text', default=None, type=str, help='text to be added. default random')
parser.add_argument('--text_color', default='(255,255,255)', type=str, help='color of the text eg. \'(50,50,50)\'')
parser.add_argument('--bg_color', default='(0,0,0)', type=str, help='color of the text background eg. \'(50,50,50)\'')
parser.add_argument('--alpha', default=0.1, type=float, help='transparency of the text background (default 90 percent)')
parser.add_argument('--scale', default=0.4, type=float, help='scale of the text font')
parser.add_argument('-o', '--output', default=None, type=str, help='name of the output file')
parser.add_argument('-p', '--position', default=None, nargs=2, type=str, help='x,y coordinates of the text location in the form \'x y\'. default random')

args = parser.parse_args()

def writeToFrame(frame, pos):
	# text position starts from bottom left
	cv2.putText(frame, text, pos, font_face, args.scale, text_color, 1, cv2.LINE_AA)
	
	top_left = (pos[0] - margin, pos[1] - txt_size[0][1] - margin)
	bottom_right = (pos[0] + txt_size[0][0] + margin, pos[1] + margin)
	
	overlay = frame.copy()
	cv2.rectangle(overlay, top_left, bottom_right, bg_color, thickness)
	new_frame = cv2.addWeighted(overlay, args.alpha, frame, 1 - args.alpha, 0)
	return new_frame

def generate_string():
	string_length = random.randint(4, 8)
	output_string = ''
	ascii_numbers = random.sample(range(ord('A'), ord('Z') + 1), string_length) ## pick string_length many ascii numbers btw 'A' and 'Z'
	chars = map(lambda c: chr(c), ascii_numbers)
	return output_string.join(chars)

def modifyVideo(video_name):
	cap = cv2.VideoCapture(video_name)
	if not cap.isOpened():
		raise IOError('video is not captured')

	size = (int(cap.get(3)), int(cap.get(4)))
	fps = cap.get(5)
	number_of_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


	ext = '.' + video_name.split('.')[-1]
	fourcc = None
	if ext == '.mp4':
		fourcc = cv2.VideoWriter_fourcc(*"mp4v")
	elif ext == '.avi':
		fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
	else:
		fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
		# add if necessary
	
	out = None
	if args.output is None:
		out = cv2.VideoWriter('modified_'+video_name, fourcc, fps, size)
	else:
		out = cv2.VideoWriter(args.output + ext, fourcc, fps, size)

	i = 0
	found = 0
	written_frame_count = 0
	modifiable_frame_count = floor(args.duration*fps)
	rand_range = (number_of_frames - modifiable_frame_count - 1) if modifiable_frame_count < number_of_frames else 0
	random_frame = random.randint(0, rand_range)

	pos = (0,0)
	if args.position is None:
		# coordinates of the frame where the text can be positioned.
		xmargin = 10
		ymargin = 10
		x1 = xmargin
		x2 = size[0] - xmargin
		y1 = ymargin
		y2 = size[1] - ymargin
		x_coor = random.randint(x1, x2 - txt_size[0][0])
		y_coor = random.randint(y1 + txt_size[0][1], y2)
		pos = (x_coor, y_coor)
	else:
		pos = tuple(map(int, args.position))

	while(True):
		ret, frame = cap.read()
		if ret == False:
			break
		if i == random_frame:
			found = 1
		if found and written_frame_count < modifiable_frame_count:
			frame = writeToFrame(frame, pos)
			written_frame_count += 1
		
		out.write(frame)
		i += 1
	
	cap.release()
	out.release()


if __name__ == '__main__':
	font_face = cv2.FONT_HERSHEY_SIMPLEX
	thickness = cv2.FILLED
	margin = 3
	text_color = literal_eval(args.text_color)
	bg_color = literal_eval(args.bg_color)

	text = generate_string() if args.text is None else args.text
	txt_size = cv2.getTextSize(text, font_face, args.scale, thickness)

	modifyVideo(args.video)
