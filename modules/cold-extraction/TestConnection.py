from pynetdicom import AE
from pynetdicom.sop_class import VerificationSOPClass
import json

# Reads the Niffler system configuration file, "system.json".
with open('system.json', 'r') as f:
    niffler = json.load(f)


QUERY_AET = niffler['QueryAet']
query = QUERY_AET.split(':')

ae = AE()
ae.ae_title = query[0]
ae.port = query[1]

ae.add_requested_context(VerificationSOPClass)

SRC_AET = niffler['SrcAet']
srct = SRC_AET.split(':')

port = int(srct[1])
src = srct[0].split('@')

assoc = ae.associate(src[1], port, ae_title=src[0])

if assoc.is_established:
    status = assoc.send_c_echo()

    if status:
        # If successful, the outputstatus will be: 0x0000
        print('C-ECHO request status: 0x{0:04x}'.format(status.Status))
    else:
        print('Connection timed out, was aborted or received invalid response')

    assoc.release()
else:
    print('Association rejected, aborted or never connected')
