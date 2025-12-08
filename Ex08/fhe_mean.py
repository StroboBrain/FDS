import concrete.numpy as cnp
import numpy as np
import random


#we expect exactly 6 values
NUM_VALUES = 6

#build FHE function: Compute scaled mean = (sum(x) * 100) // 6
#using integer arithmetic only
@cnp.compiler({"values": cnp.array(cnp.uint8, shape=(NUM_VALUES,))})
def fhe_mean(values):
    #compute sum of encrypted inputs
    total = cnp.sum(values)
    scaled = total * 100

    #integer division by 6
    result = scaled // NUM_VALUES

    #return encrypted scaled mean
    return result


def encrypt_values(public_ctx, values):
    #encrypt each value individually
    return public_ctx.encrypt(values)

def decrypt_result(private_ctx, encrypted_result):
    return private_ctx.decrypt(encrypted_result)
