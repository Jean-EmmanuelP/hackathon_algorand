from pyteal import Seq, If, Int, Txn, Log, Itob, Btoi, Assert, Bytes, Concat
from pyteal import compileTeal, Mode
import base64

def sum_contract():
    # The ABI selector for "sum(uint64,uint64)uint64" is "cF3R/w=="
    method_selector = base64.b64decode("cF3R/w==")  # Decode the base64 string to bytes

    program = Seq([
        If(Txn.application_id() == Int(0))
        .Then(Int(1))
        .Else(
            Seq([
                # Verify this is a call to our sum method
                Assert(Txn.application_args[0] == Bytes(method_selector)),
                
                # Return format for ABI: 
                # - First 4 bytes: Return type prefix ("uint")
                # - Next 8 bytes: The actual uint64 value
                Log(
                    Concat(
                        Bytes("uint"),  # ABI return type prefix
                        Itob(           # Convert result to 8 bytes
                            Btoi(Txn.application_args[1]) +  # First number
                            Btoi(Txn.application_args[2])    # Second number
                        )
                    )
                ),
                Int(1)
            ])
        )
    ])
    return program


# Write TEAL code to file
if __name__ == "__main__":
    with open("sum_contract.teal", "w") as f:
        teal_code = compileTeal(sum_contract(), mode=Mode.Application, version=5)
        print('Contract compiled succesfuly')
