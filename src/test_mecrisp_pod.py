"""
Simple console test for Mecrisp POD
input pins correspond to the usual STM32F103 pins
"""
import mecrisp_pod


def main(port):
    pod = mecrisp_pod.MecrispPOD(port)
    pod.input_pins = ('PA3', 'PA4', 'PA5', 'PA6', 'PA7', 'PB0', 'PB1', 'PB2', 'PA8', 'PA9', 'PA10',
                      'PA15', 'PB3', 'PB4', 'PB5', 'PB6', 'PB7', 'PA13', 'PA14', 'PA1', 'PA2')
    pod.initialize_pins()
    while True:
        print('')
        for pin in pod.input_pins:
            print(pin, pod.query_input_pin(pin))
        ans = input('q? ')
        if ans == 'q': break
    del pod


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
