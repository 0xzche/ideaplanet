from asyncio import start_unix_server
import sys, os
import pprint
from tokenize import blank_re
import numpy as np
from PIL import ImageFilter
sys.path.insert(0, os.path.expandvars("$GITHUB/ideaplanet/0xgenerator/python"))
pprint.pprint(sys.path)
from py0xlab import *
from py0xlab.frame import where, is_same_color, get_bg_color
from py0xlab import frame as frm
from py0xlab import io
from pathlib import Path
from tqdm import tqdm
from argparse import ArgumentParser
log.basicConfig(level=log.DEBUG)

class Piece:

    arr: np.array
    speed_x: float
    speed_y: float
    start_x: float
    start_y: float

    def __init__(self):
        pass

def replace_non_background_by_non_background(arr1, arr2, bg_color1=None, bg_color2=None):
    """ Replace the backgroud in arr1 by non-background in arr2.
    """
    assert arr1.shape == arr2.shape, f"inputs shape mismatch: {arr1.shape} vs {arr2.shape}"
    if bg_color1 is None:
        bg_color1   = arr1[5, 5, :]
    if bg_color2 is None:
        bg_color2   = arr2[3, 3, :]
    is_bg1      = is_same_color(arr1, bg_color1)
    is_bg2      = is_same_color(arr2, bg_color2)
    #replace     = np.logical_and(is_bg1, np.logical_not(is_bg2))
    arr2_a      = where(is_bg2, np.array([135, 206, 235]), arr2)
    replace     = np.logical_not(is_bg1)
    new_arr     = where(replace, arr2_a, arr1)
    return new_arr

def gen_sakura_gif(file_name):

    #input_file = Path(os.path.expandvars("~/cloud/data/0xgenerator/inputs")) / "sakura.png"
    input_dir = Path("/Users/zche/data/0xgenerator/sakura_rain/inputs/")
    output_dir = Path("/Users/zche/data/0xgenerator/sakura_rain/ouputs/") 

    origin_size = 1200
    output_size = (600, 600)
    fg_frame = io.read_frame(input_dir / f"{file_name}", size=output_size)
    #skr_frame = io.read_frame(input_dir / "sakura.png", to_np=True) # sakura frame
    skr_arr = io.read_frame(input_dir / "sakura.png", to_np=True) # sakura frame
    bg_color2   = skr_arr[3, 3, :]
    is_bg2      = is_same_color(skr_arr, bg_color2, tol=60)
    skr_frame   = io.np_to_im( where(is_bg2, np.array([135, 206, 235]), skr_arr))
    skr_frame.resize((100, 100))

    w, h = skr_frame.size
    nn = 4
    raw_piece_size = w // nn, h // nn 
    raw_pieces = []
    for i in range(nn):
        for j in range(nn):
            raw_piece = skr_frame.crop((
                w // nn * i,
                h // nn * j,
                w // nn * i + raw_piece_size[0],
                h // nn * j + raw_piece_size[1]
            ))
            raw_pieces.append(raw_piece)


    pieces = []
    
    base_speed = 2

    n_pieces = 150
    for i in tqdm(range(n_pieces)):
        rescale = (output_size[0] / origin_size)  
        #distance_factor = np.random.rand() 
        distance_factor = 1 - (i * 1.0 / n_pieces)
        rescale_idio =  (0.2 + 0.8 * distance_factor)
        piece_idx = np.random.randint(0, len(raw_pieces) - 1)
        piece_size = [int(_ * rescale * rescale_idio) for _ in raw_piece_size]
        piece = raw_pieces[piece_idx].resize(piece_size) # piece to place on top of background rescaled
        #piece.save(str(output_dir / f"sakura_piece_rescaled.png")) # for debug
        #log.info(f"piece {piece_idx} rescaled by {rescale} to new size {piece_size}")
        piece_arr = np.array(piece)
        replace_ = is_same_color(piece_arr, get_bg_color(piece_arr))
        piece_arr = where(
            replace_,
            frm.yellow(piece_size),
            piece_arr) # replace background by green
        piece_arr = frm.rotate(piece_arr, k=np.random.randint(0, 4))
        
        p = Piece()
        p.arr = piece_arr
        p.speed_x = base_speed * (0.1 + 0.9*distance_factor) # horizontal speed at each frame, how much of the frame does the p fly for the whole time
        p.speed_y = -(1+np.random.rand()) / 2 * p.speed_x 
        p.start_x = np.random.rand()
        p.start_y = np.random.rand()

        #if i < 10: # for debug
            #io.np_to_im(p.arr).save(str(output_dir / f"test_{i}.png"))
        pieces.append(p)

    out_w, out_h = output_size
    n_frames = 150
    output_frames = []

    blank_bg = frm.yellow(output_size)
    for t in tqdm(range(n_frames)):
        new_bg = np.array(blank_bg)
        for p in pieces:
            loc = (
                int((p.speed_x / n_frames * t + p.start_x) * out_w), 
                int((p.speed_y / n_frames * t + p.start_y) * out_h)
            )
            new_bg = frm.paste(p.arr, new_bg, loc=loc, bg_color1=frm.YELLOW, bg_color2=frm.YELLOW)
        arr = replace_non_background_by_non_background(
            fg_frame, new_bg,
            bg_color1=get_bg_color(fg_frame),
            bg_color2=frm.YELLOW,
        )
        output_frames.append(arr)
    
    for i, arr in tqdm(enumerate(output_frames)):
        frame = io.np_to_im(arr, "RGB")
        #frame = frame.filter(ImageFilter.SMOOTH)
        #output_frames[i] = frame
        #output_frames[i] = frame #.quantize()#dither=Image.NONE)
        output_frames[i] = frame.quantize(kmeans=3)#dither=Image.NONE)
        #output_frames[i] = frame.quantize(dither=Image.FLOYDSTEINBERG)

    output_file = Path("/Users/zche/data/0xgenerator/sakura_rain/ouputs/") / f"reverse_sakura_{file_name.split('.')[0]}.gif"
    io.compile_gif(
        output_frames,
        output_file=output_file,
        total_time=7.0,
    )
    


parser = ArgumentParser()
parser.add_argument("file_name", type=str)
    
if __name__ == "__main__":

    gen_sakura_gif(file_name=parser.parse_args().file_name)
