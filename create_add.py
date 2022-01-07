from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import random

from mnemonic import Mnemonic
import bip32utils
from bit import PrivateKeyTestnet

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    mnemonic: str

@app.post('/send-coin')
def send_coin(item: Item):
    #Mnemonic to Root key Generate
    
    mnemon = Mnemonic('english')
    if not mnemon.check(item.mnemonic):
        raise HTTPException(status_code=400, detail='Invaild Mnemonic')
    seed = mnemon.to_seed(item.mnemonic)
    root_key = bip32utils.BIP32Key.fromEntropy(seed)
    root_private_wif = root_key.WalletImportFormat()

    value = random.randint(0,10000)

    #Child Key Generate
    child_key = root_key.ChildKey(0).ChildKey(0)
    child_private_wif = child_key.WalletImportFormat()

    #Generate Wallet
    my_key = PrivateKeyTestnet(root_private_wif)
    my_key2 = PrivateKeyTestnet(child_private_wif)

    #Sender Address
    to_address = my_key2.address
    transfer_balance = my_key.get_balance('btc')
    try:
        tx_hash = my_key.send([(to_address, 0.00001, 'btc')])
    except Exception as e:
        raise HTTPException(status_code=400, detail='Insufficient Fund - '+ my_key.address + ' (Please store enough fund to the address)')
    my_key_final = PrivateKeyTestnet(root_private_wif)
    my_key2_final = PrivateKeyTestnet(child_private_wif)
    return {'detail': 'Successfully sent 0.00001 btc from '+ my_key.address + ' to ' + to_address,'sender_address': my_key.address ,'sender_balance': my_key_final.get_balance('btc'), 'receiver_address': to_address}
