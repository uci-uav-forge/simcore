import readline
from simcore import PayloadDropper

if __name__ == "__main__":
    dropper = PayloadDropper()
    while True:
        try:
            pos = None
            drop = input("Enter b or w to drop a payload: ")
            if drop == "b":
                pos = dropper.drop_payload("beacon")
            elif drop == "w":
                pos = dropper.drop_payload("waterbottle")
            else:
                print("Invalid input. Please enter 'b' or 'w'.")
                continue
            print(f"Payload dropped at position: {pos}")
        except KeyboardInterrupt:
            print("Exiting...")
            break