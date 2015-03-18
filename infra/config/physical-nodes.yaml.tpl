# physical-nodes.yaml
---

infra::nodes:
 # List here the controller servers - prefix (host)name with 'controller'
 controller1:
  ip: 192.168.1.92
 # List here the compute servers - prefix (host)name with 'compute'
 compute1: 
  ip: 192.168.1.93
  bridge_uplinks:
   - "br-vm:eth3" 
 compute2: 
  ip: 192.168.1.93
  bridge_uplinks:
   - "br-vm:eth3" 
 # List here the network servers - prefix (host)name with 'network'
 network1: 
  ip: 192.168.1.95
  bridge_uplinks:
   - "br-ex:eth0"
   - "br-vm:eth3"

