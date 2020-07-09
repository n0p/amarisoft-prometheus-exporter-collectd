import collectd
from websocket import create_connection
import json
import threading



epc_list = []

def read_thread(epc_ip):
    try:
        
        ws = create_connection('ws://%s:9000' % epc_ip)

        # CPU Load
        ws.send('{"message":"stats"}')
        result =  ws.recv()
        j_res = json.loads(result)
        vl = collectd.Values(type='vcpu')
        vl.host=epc_ip
        vl.plugin="epc_cpu"
        vl.plugin_instance="cpu"
        vl.type_instance="cpu"
        vl.interval=5
        cpu=j_res['cpu']['global']
        vl.dispatch(values=[cpu])

        ws.send('{"message":"enb"}')
        result =  ws.recv()
        j_res = json.loads(result)

        # connected enbs
        vl = collectd.Values(type='count')

        vl.host=epc_ip

        for i in range (0,len(j_res['enb_list'])):
            plmn = j_res['enb_list'][i]['plmn']
            eNB_ID = j_res['enb_list'][i]['eNB_ID']
            address = j_res['enb_list'][i]['address']
            ue_ctx = j_res['enb_list'][i]['ue_ctx']
            address=address[0:address.index(":")]
            vl.plugin='epc_enb_ctx'
            vl.plugin_instance="ip_"+str(address)+"_ID_"+str(eNB_ID)+"_ID"
            vl.type_instance=plmn
            vl.interval=5
            vl.dispatch(values=[ue_ctx])


    except Exception as e:
        print(e)
        print('epc @ %s is not connected !' % epc_ip)


def read(data=None):
    global epc_list
    for ip_i in epc_list:
        threading.Thread(target=read_thread,kwargs=dict(epc_ip=ip_i)).start()





def write(vl, data=None):
    print "(plugin: %s host: %s type: %s pl.i: %s ty.i: %s): %s\n" % (vl.plugin, vl.host, vl.type,vl.plugin_instance,vl.type_instance, vl.values)





def init():
    global epc_list
    print("loading EPC list")
    f = open('/etc/collectd/plugins/epc_list.cfg', 'r')
    epc_list = f.read().splitlines()
    print(epc_list)

collectd.register_read(read)
collectd.register_write(write)
collectd.register_init(init)