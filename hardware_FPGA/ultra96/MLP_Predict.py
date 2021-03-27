from pynq import Overlay
import pynq.lib.dma
from pynq import DefaultIP
from pynq import allocate
import numpy as np

import time
def MLP_Start():
    overlay = Overlay('/home/xilinx/impl_float32/design_1.bit')
    dma = overlay.axi_dma_0      

def MLP_Predict(inputs):
    overlay = Overlay('/home/xilinx/impl_float32/design_1.bit')
    dma = overlay.axi_dma_0            
    in_buffer = allocate(shape=(86,), dtype=np.int32)
    for i in range(86):
        in_buffer[i] = unpack('i', pack('f',inputs[i]))[0];
    print(in_buffer)
    out_buffer = allocate(shape=(4,), dtype=np.int32)
    dma.sendchannel.transfer(in_buffer)
    dma.recvchannel.transfer(out_buffer)
    dma.sendchannel.wait()
    dma.recvchannel.wait()
    out = (out_buffer[0:3])
    out = out_buffer.tolist()
    return(out.index(max(out)))