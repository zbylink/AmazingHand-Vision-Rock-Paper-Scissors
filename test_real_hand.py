from hand_control import AmazingHand
import time


hand = AmazingHand()


try:

    print("Middle position")
    hand.middle()
    time.sleep(1)

    print("Shame action")
    hand.shame()
    time.sleep(2)



finally:

    print("Return middle")

    hand.middle()
    time.sleep(2)

    hand.stop()