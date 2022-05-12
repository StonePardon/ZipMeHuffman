import argparse
import bitarray as bit


class Node:
	def __init__(self, freq,  value=-1, one=None, zero=None):
		self.freq = freq
		self.value = value
		self.one = one
		self.zero = zero
	def get_children(self):
		return self.one, self.zero
	

def UnZipMeHuffman(filename):
	print("UnZMH mode")
	if filename.split('.')[-1] != "zmh":
		print("Wrong format:")
		print("Need *.zmh file")
		raise SystemExit
	try:
		hf = open(filename, "rb")
	except:
		print("Can't open your file:")
		print("Check correct spelling of name and that path to file is full")
		raise SystemExit
	voc_size = hf.read(2)
	voc_size = int.from_bytes(voc_size, "big")
	huff_voc = {}
	for i in range(voc_size):
		byte = hf.read(1)
		size = int.from_bytes(hf.read(1), "big")
		value = bit.bitarray()
		byte_size = size // 8
		if size % 8:
			byte_size += 1
		value.frombytes(hf.read(byte_size))
		if value == None:
			value = bit.bitarray("00000000")
		huff_voc[byte] = value[:size]
	
	ending_size =int.from_bytes(hf.read(1), "big")
	huff_text = bit.bitarray()
	huff_text.frombytes(hf.read())
	hf.close()

	try:
		huff_decode = bit.decodetree(huff_voc)
	except:
		print("Error with decode vocabulary")
		print("zmh file is broken")	
		raise SystemExit
	if ending_size != 8 and ending_size!= 0:
		huff_text = huff_text[:-ending_size]
	try:  
		real_text = huff_text.decode(huff_decode)
	except:
		print("Unknown error")
		print("zmh file is broken")	
		raise SystemExit

	unhuffman_file = filename.split('.')[0]
	with open(unhuffman_file, "wb") as rf:
		for byte in real_text:
			rf.write(byte)
		print("Done!")

def ZipMeHuffman(filename): 
	print("ZMH mode") 
	barray = {}
	try:
		with open(filename, "rb") as f:
			byte = f.read(1)
			while byte:
				if byte in barray.keys():
					barray[byte] += 1
				else:
					barray[byte] = 1
				byte = f.read(1)
	except:
		print("Can't open your file:")
		print("Check correct spelling of name and that path to file is full")
		raise SystemExit
	sort_barray = sorted(barray.items(), key = lambda x: x[1])
	
	huff_array = []
	for char, fr in sort_barray:
		huff_array.append(Node(fr, char))

	while len(huff_array) != 1:
		freq0 = huff_array[0].freq    
		freq1 = huff_array[1].freq
		new_node = Node(freq0+freq1, one=huff_array[1], zero=huff_array[0])
		huff_array[1] = new_node
		huff_array.pop(0)
		huff_array = sorted(huff_array, key = lambda x: x.freq)
	
	number = len(sort_barray)
	while len(huff_array) != number:
		if len(huff_array) == 1:
			node0 = huff_array[0].zero
			node1 = huff_array[0].one
			node0.freq =  bit.bitarray('0')
			node1.freq =  bit.bitarray('1')
			huff_array.pop(0)
			huff_array.append(node0)
			huff_array.append(node1)
			continue
		new_array = []
		for node in huff_array:
			if node.one == None and node.zero == None:
				new_array.append(node)
				continue
			node0 = node.zero
			node1 = node.one
			node0.freq = bit.bitarray(node.freq)
			node1.freq = bit.bitarray(node.freq)
			node0.freq.extend([0])
			node1.freq.extend([1])
			new_array.append(node0)
			new_array.append(node1)
		huff_array = new_array

	huffman_voc = {}
	for elem in huff_array:
		huffman_voc[elem.value] = elem.freq

	huff_text = bit.bitarray()
	text_size = 0
	with open(filename, "rb") as f:
		byte = f.read(1)
		while byte:
			text_size += 1
			value = huffman_voc[byte]
			huff_text.extend(value)
			byte = f.read(1)
	huff_file_name = filename.split('.')[0] + ".zmh"
	with open(huff_file_name, "wb") as hf:
		hf.write( (len(huffman_voc)).to_bytes(2, byteorder='big') )
		# запишем алфавит
		for key, value in huffman_voc.items():
			hf.write(key)
			hf.write((len(value)).to_bytes(1, byteorder='big'))
			hf.write(value.tobytes())
		# запишем число незначащих бит в концее
		ending = 8 - (len(huff_text) % 8)
		hf.write(ending.to_bytes(1, byteorder='big'))
		hf.write(huff_text.tobytes())
		print("Done!")


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='ZipMeHuffman packer and unpacker')

	parser.add_argument('filename', help="Name of file to pack or unpack")
	parser.add_argument('--mode', choices=["pack", "unpack"], nargs='?', default="pack", type=str, help='choose mode of work: pack or unpack; default mode = pack')
	args = parser.parse_args()


	filename = args.filename
	mode = args.mode


	if mode == "pack":
		ZipMeHuffman(filename)
	if mode == "unpack":
		UnZipMeHuffman(filename)