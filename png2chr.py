#!/usr/bin/env python3

from PIL import Image
import pathlib, math, os, re, sys

def bits_to_byte(bit_array):
  byte = 0
  for i in range(0,8):
    byte = byte << 1;
    byte = byte + bit_array[i];
  return byte

def hardware_tile_to_bitplane(index_array):
  # Note: expects an 8x8 array of palette indices. Returns a 16-byte array of raw NES data
  # which encodes this tile's data as a bitplane for the PPU hardware
  low_bits = [x & 0x1 for x in index_array]
  high_bits = [((x & 0x2) >> 1) for x in index_array]
  low_bytes = [bits_to_byte(low_bits[i:i+8]) for i in range(0,64,8)]
  high_bytes = [bits_to_byte(high_bits[i:i+8]) for i in range(0,64,8)]
  return low_bytes + high_bytes

def convert_to_raw_chr(image, is_obj=False):
  chr_tiles = []
  for tile_y in range(0, math.floor(image.height / 8)):
    for tile_x in range(0, 16):
      left = tile_x * 8
      top = tile_y * 8
      right = left + 8
      bottom = top + 8
      chr_tiles.append(hardware_tile_to_bitplane(image.crop((left, top, right, bottom)).getdata()))
  if is_obj:
    chr_tiles = reorder_tiles_as_large_sprites(chr_tiles)
  chr_bytes = []
  for tile in chr_tiles:
    chr_bytes = chr_bytes + tile
  return chr_bytes

# we can define entire 4k CHR banks as .png instead, and this permits animations
# to boot. here, treat it the same as a rather large sprite
def read_png_chr(filename):
  im = Image.open(filename)
  assert im.getpalette() != None, "Non-paletted tile found! This is unsupported: " + filename
  assert im.width in [128], "PNG CHR files must be 128 pixels wide! Bailing. " + filename
  assert im.height in [128,512], "PNG CHR files must be 128 or 16384 pixels tall! Bailing. " + filename
  is_obj = "_obj" in str(filename)
  return convert_to_raw_chr(im, is_obj=is_obj)

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print("Usage: png2chr.py source.png output.chr")
    sys.exit(-1)
  input_filename = sys.argv[1]
  output_filename = sys.argv[2]

  raw_chr_bytes = read_png_chr(input_filename)
  with open(output_filename, 'wb') as chr_file:
    chr_file.write(bytes(raw_chr_bytes))
