from pyteal import *

def approval_program():
    target_app_id = Int(724672278)  # Level 9 App ID
    level_8_id = Int(724672240)     # Level 8 App ID

    # Opt-In method
    opt_in_method = Seq([
        # Create inner transaction to perform Opt-In
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.ApplicationCall,
            TxnField.application_id: target_app_id,
            TxnField.on_completion: OnComplete.OptIn,
            TxnField.fee: Int(0),  # Set fee to 0
            TxnField.applications: [level_8_id],  # Include Level 8 app as foreign app
        }),
        InnerTxnBuilder.Submit(),
        Return(Int(1))
    ])

    # Program to handle calls
    program = Cond(
        [Txn.application_id() == Int(0), Return(Int(1))],  # Approve contract creation
        [Txn.on_completion() == OnComplete.NoOp, opt_in_method]
    )

    return program 

def clear_state_program():
    return Return(Int(1))

if __name__ == "__main__":
    with open("opt_in_approval.teal", "w") as f:
        a = compileTeal(approval_program(), mode=Mode.Application, version=6)
    with open("opt_in_clear.teal", "w") as f:
        b = compileTeal(clear_state_program(), mode=Mode.Application, version=6)
    print('Contract Compiled Succesfuly')