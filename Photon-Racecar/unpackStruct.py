'''
  Unpackes a struct created on a
  Particle Photon with the following:

  struct network_info_t{
      unsigned counter; // increasing value to verify new packets
      unsigned long milli_time;

      int throttle_pos; // signal from controller
      int throttle_out; // modified signal to car
      int steer_pos;  // signal from controller and to car
  
      unsigned ir_changes;

      int sig_strength;
      // Data from sensors
      float ax;
      float ay;
      float az;
      float battery_voltage_in;
      float battery_current_in;
      float battery_current_sum;

      unsigned long wheel_pos;

      // Wifi parameters
      byte device_mac[6];
      char local_ip[16];
      char gateway_ip[16];
      char subnet_mask[16];
      byte access_point_BSSID[6];
      char ssid[20];
      char terminator[4]; // 0xDE AD BE EF
};

  See udp-wifi-streamer.ino for the Photon code.
'''

from struct import *

def getMAS(mac):
  if len(mac) == 6:
    return "%x:%x:%x:%x:%x:%x" % unpack("BBBBBB",mac)
  return '-'

def unpackStruct(data):
  
  struct_format = 'II iii I iffffff I 6s16s16s16s6s20s4s'
  r = {}
  
  # Search for DEADBEEF and remove it from data
  beef_location = data.find( '\xDE\xAD\xBE\xEF' )
  if beef_location == -1:
    return (data, r)

  packet = data[(beef_location - calcsize(struct_format) + 4):(beef_location + 4)]
  
  data = data[(beef_location + 4):]
  
  
  (r['counter'],
   r['time'],
   r['throttle'],
   r['throttle_out'],
   r['steer'],
   r['ir_changes'],
   r['sig_strength'],
   r['ax'],
   r['ay'],
   r['az'],
   r['battery_voltage_in'],
   r['battery_current_in'],
   r['battery_current_sum'],
   r['wheel'],
   r['device_mac'],
   r['local_ip'],
   r['gateway_ip'],
   r['subnet_mask'],
   r['bssid'],
   r['ssid'],
   _) = unpack(struct_format, packet)
  
   # fix string lengths
  r['local_ip'] = r['local_ip'].rstrip(' \t\r\n\0')
  r['gateway_ip'] = r['gateway_ip'].rstrip(' \t\r\n\0')
  r['subnet_mask'] = r['subnet_mask'].rstrip(' \t\r\n\0')
  #r['bssid'] = r['bssid'].rstrip(' \t\r\n\0')
  #r['ssid'] = r['ssid'].rstrip(' \t\r\n\0')
  r['bssid'] = getMAS(r['bssid'])
  r['ssid'] = r['ssid'].rstrip(' \t\r\n\0')
  r['device_mac'] = getMAS(r['device_mac'])

  return (data, r)
  
