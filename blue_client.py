import bluetooth
import base64
import time


class BluetoothConnection:
    def find_nearby_devices(self):
        print("Detecting nearby Bluetooth devices...")

        loop_num = 3
        i = 0
        try:
            self.nearby_devices = bluetooth.discover_devices(lookup_names=True)
            while self.nearby_devices.__len__() == 0 and i < loop_num:
                self.nearby_devices = bluetooth.discover_devices(lookup_names=True)
                if self.nearby_devices.__len__() > 0:
                    break
                i = i + 1
                time.sleep(2)
                print("No Bluetooth device around here! trying again {}...".format(str(i)))
            if not self.nearby_devices:
                print("There's no Bluetooth device around here. Program stop!")
            else:
                print("{} nearby Bluetooth device(s) has(have) been found:".format(self.nearby_devices.__len__()),
                      self.nearby_devices)
        except Exception as e:
            # print(traceback.format_exc())
            print("There's no Bluetooth device around here. Program stop(2)!")

    def send_message_to_target(self, addr):
        try:
            client_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            client_sock.connect((addr, 1))
            print('Connect successfully to ', addr)
            # data = input()
            print('sending message')
            st_time = time.time()
            # file = open('weight.pt', 'rb')
            # for i in file:
            #     client_sock.send(i)
            # file.close()
            with open('weight.pt', 'rb') as f:
                while True:
                    b = f.read(1024)
                    if len(b) == 0:
                        break
                    client_sock.send(b)
            print("All message sent successfully in {}s".format(time.time() - st_time))
            # time.sleep(10)
            client_sock.close()
            # client_sock.send('quit'.encode())
            '''
            while(True): 
                data = input()
                data_encode = data.encode('utf-8')
                client_sock.send(data_encode)
                if client_sock.recv(1024).decode()=='quit':
                    print('Connection terminated')
                    client_sock.close()
                    break
            '''
        except:
            # print(Exception.with_traceback())
            print('Cannot connect to target device.')


if __name__ == '__main__':
    # BluetoothConnection().find_nearby_devices()
    BluetoothConnection().send_message_to_target('E4:5F:01:CA:18:C8')

    # img_data = base64.b64decode(msg_img.get_img())
    # with open('001.png', 'wb') as f:
    #     f.write(img_data)
