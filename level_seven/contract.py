from pyteal import *
from base64 import b64decode, b64encode

def approval_program():
    # Get and log the forward_auth selector
    # forward_auth_selector = MethodSignature("forward_auth()void")
    # print("forward_auth selector in base64:", b64encode(forward_auth_selector).decode())
    # print("forward_auth selector in bytes:", forward_auth_selector)
    
    # Define the target app ID (Level 7 contract)
    target_app_id = Int(724672237)
    
    # Define the authorize selector using the hex value
    # authorize_selector = Bytes.fromhex("73bc6501")
    
    # Method to forward authorization
    forward_auth_method = Seq([
        # Verify method selector
        # Assert(Txn.application_args[0] == authorize_selector),
        
        # Create inner transaction to call authorize
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.ApplicationCall,
            TxnField.application_id: target_app_id,
            TxnField.application_args: [
                Bytes(b64decode('c7xlAQ==')),  # Use the hex selector instead of base64
                Txn.sender()
            ],
        }),
        InnerTxnBuilder.Submit(),
        
        Return(Int(1))
    ])

    # Handle application calls
    program = Cond(
        [Txn.application_id() == Int(0), Seq([
            # Add foreign app check on creation
            Assert(Txn.applications.length() == Int(1)),
            Assert(Txn.applications[1] == target_app_id),
            Return(Int(1))
        ])],  # On creation
        [Txn.on_completion() == OnComplete.NoOp, forward_auth_method]
    )

    return program

def clear_state_program():
    return Return(Int(1))

if __name__ == "__main__":
    with open("authorize_approval.teal", "w") as f:
        a = compileTeal(approval_program(), mode=Mode.Application, version=6)
    with open("authorize_clear.teal", "w") as f:
        a = compileTeal(clear_state_program(), mode=Mode.Application, version=6)
    print('Compiled succesfully')