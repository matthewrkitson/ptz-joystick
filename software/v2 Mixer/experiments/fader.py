import time
import xair_api


def main():
    kind_id = "X32"
    ip = "192.168.56.195"
    # ip = "127.0.0.1"

    with xair_api.connect(kind_id, ip=ip) as mixer:
        mixer.validate_connection()
        mixer.bus[8].mix.fader = 9.9
        time.sleep(0.5)
        mixer.bus[8].mix.fader = -60
        exit()

        while (True):
            for v in range(-90, 10):
                print(v)
                mixer.bus[8].mix.fader = v
                time.sleep(0.05)
            
            for v in range(9, -91, -1):
                print(v)
                mixer.bus[8].mix.fader = v
                time.sleep(0.05)

        while (True):
            query = input("Query: ")
            if not query:
                break;
            print(mixer.query(query))

if __name__ == "__main__":
    main()