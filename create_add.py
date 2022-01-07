from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import random

from mnemonic import Mnemonic
import bip32utils
from bit import PrivateKeyTestnet, Key

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    sender_mnemonic: str
    receiver_mnemonic: str

@app.post('/send-coin')
def send_coin(item: Item):
    #Mnemonic to Root key Generate
    
    mnemon = Mnemonic('english')
    if not mnemon.check(item.sender_mnemonic):
        raise HTTPException(status_code=400, detail='Invaild Sender Mnemonic')
    if not mnemon.check(item.receiver_mnemonic):
        raise HTTPException(status_code=400, detail='Invaild Receiver Mnemonic')
    #Sender Seed
    sender_seed = mnemon.to_seed(item.sender_mnemonic)
    sender_root_key = bip32utils.BIP32Key.fromEntropy(sender_seed)
    sender_root_private_wif = sender_root_key.WalletImportFormat()

    #Receiver Seed
    receiver_seed = mnemon.to_seed(item.receiver_mnemonic)
    receiver_root_key = bip32utils.BIP32Key.fromEntropy(receiver_seed)
    receiver_root_private_wif = receiver_root_key.WalletImportFormat()

    #value = random.randint(0,10000)

    #Child Key Generate
    #child_key = root_key.ChildKey(0).ChildKey(0)
    #child_private_wif = child_key.WalletImportFormat()

    #Generate Wallet for Test Net
    #sender_my_key = PrivateKeyTestnet(sender_root_private_wif)
    #receiver_my_key = PrivateKeyTestnet(receiver_root_private_wif)

    #Generate Wallet for Main Net
    sender_my_key = Key(sender_root_private_wif)
    receiver_my_key = Key(receiver_root_private_wif)

    #Sender Address
    sender_address = sender_my_key.address
    #Receiver Address
    receiver_address = receiver_my_key.address
    try:
        tx_hash = sender_my_key.send([(receiver_address, 0.00001, 'btc')])
    except Exception as e:
        raise HTTPException(status_code=400, detail='Insufficient Fund - '+ sender_address + ' (Please store enough fund to the sender address)')
    
    return {'detail': 'Successfully sent 0.00001 btc from '+ sender_address + ' to ' + receiver_address,'sender_address': sender_address ,'sender_balance': sender_my_key.get_balance('btc'), 'receiver_address': receiver_address, 'receiver_balance': receiver_my_key.get_balance('btc')}
