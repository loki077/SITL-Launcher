"""
A collection of tools for launching RealFlight 9.5, and for editing start-up
and airport files to configure the simulator for use with the SITL Launcher.
"""

import socket
import time

CONTROLLER_IP = '127.0.0.1'
CONTROLLER_PORT = 18083

DEFAULT_SERVOS = [0]*12


def reset_aircraft():
    """
    Initialize SOAP connection to RealFlight, send default servo values,
    and reset aircraft position.
    """
    # Call a restore first. This allows us to connect after the aircraft is
    # changed in RealFlight
    _soap_request_start("RestoreOriginalControllerDevice", """<?xml version='1.0' encoding='UTF-8'?>
<soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/' xmlns:xsd='http://www.w3.org/2001/XMLSchema' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
<soap:Body>
<RestoreOriginalControllerDevice><a>1</a><b>2</b></RestoreOriginalControllerDevice>
</soap:Body>
</soap:Envelope>""")
    # Pause 1 second
    time.sleep(0.1)
    # Inject controller interface
    _soap_request_start("InjectUAVControllerInterface", """<?xml version='1.0' encoding='UTF-8'?>
<soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/' xmlns:xsd='http://www.w3.org/2001/XMLSchema' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
<soap:Body>
<InjectUAVControllerInterface><a>1</a><b>2</b></InjectUAVControllerInterface>
</soap:Body>
</soap:Envelope>""")
    # Pause 1 second
    time.sleep(0.1)


    # Send default servo values
    _soap_request_start("ExchangeData", f"""<?xml version='1.0' encoding='UTF-8'?><soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/' xmlns:xsd='http://www.w3.org/2001/XMLSchema' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
<soap:Body>
<ExchangeData>
<pControlInputs>
<m-selectedChannels>4095</m-selectedChannels>
<m-channelValues-0to1>
<item>{DEFAULT_SERVOS[0]}</item>
<item>{DEFAULT_SERVOS[1]}</item>
<item>{DEFAULT_SERVOS[2]}</item>
<item>{DEFAULT_SERVOS[3]}</item>
<item>{DEFAULT_SERVOS[4]}</item>
<item>{DEFAULT_SERVOS[5]}</item>
<item>{DEFAULT_SERVOS[6]}</item>
<item>{DEFAULT_SERVOS[7]}</item>
<item>{DEFAULT_SERVOS[8]}</item>
<item>{DEFAULT_SERVOS[9]}</item>
<item>{DEFAULT_SERVOS[10]}</item>
<item>{DEFAULT_SERVOS[11]}</item>
</m-channelValues-0to1>
</pControlInputs>
</ExchangeData>
</soap:Body>
</soap:Envelope>""")
    # Pause 1 second
    time.sleep(0.1)

    # Reset aircraft position
    _soap_request_start("ResetAircraft", """<?xml version='1.0' encoding='UTF-8'?>
<soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/' xmlns:xsd='http://www.w3.org/2001/XMLSchema' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
<soap:Body>
<ResetAircraft><a>1</a><b>2</b></ResetAircraft>
</soap:Body>
</soap:Envelope>""")


def _soap_request_start(action, pkt):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((CONTROLLER_IP, CONTROLLER_PORT))

        req = f"""POST / HTTP/1.1
soapaction: '{action}'
content-length: {len(pkt)}
content-type: text/xml;charset='UTF-8'
Connection: Keep-Alive

{pkt}"""
        sock.send(req.encode('utf-8'))
        return True

if __name__ == '__main__':
    reset_aircraft()