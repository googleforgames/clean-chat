
####################################################
#
#   Antidote ML Events Simulator
#
#   This simulator will randomly generate events,
#   at randomized intervals, on user-idefined port.
#
####################################################

import sys
import time
import socket
import random
import json
from random_username.generate import generate_username
from google.cloud import pubsub_v1

####################################################
# Config
####################################################

try:
        ensemble_container = sys.argv[1]
except:
        ensemble_container = 'antidote_ensemble'

print('[ DEBUG ] Ensemble Container Name: {}'.format(ensemble_container))

try:
    simulator_config = {
        'host': socket.gethostbyname(ensemble_container),
        'port': 5000
    }
except:
    simulator_config = {}

####################################################
# Functions
####################################################

def pubsub_publish( pubsub_publisher, project_id, pubsub_topic, message ):
    '''
        Pub/Sub Publish Message
        Notes:
          - When using JSON over REST, message data must be base64-encoded
          - Messages must be smaller than 10MB (after decoding)
          - The message payload must not be empty
          - Attributes can also be added to the publisher payload
        
        
        pubsub_publisher  = pubsub_v1.PublisherClient()
        
    '''
    try:
        # Initialize PubSub Path
        pubsub_topic_path = pubsub_publisher.topic_path( project_id, pubsub_topic )
        
        # If message is JSON, then dump to json string
        if type( message ) is dict:
            message = json.dumps( message )
        
        # When you publish a message, the client returns a Future.
        #message_future = pubsub_publisher.publish(pubsub_topic_path, data=message.encode('utf-8'), attribute1='myattr1', anotherattr='myattr2')
        message_future = pubsub_publisher.publish(pubsub_topic_path, data=message.encode('utf-8') )
        message_future.add_done_callback( pubsub_callback )
    except Exception as e:
        print('[ ERROR ] {}'.format(e))


def pubsub_callback( message_future ):
    # When timeout is unspecified, the exception method waits indefinitely.
    if message_future.exception(timeout=30):
        print('[ ERROR ] Publishing message on {} threw an Exception {}.'.format(topic_name, message_future.exception()))
    else:
        print('[ INFO ] Result: {}'.format(message_future.result()))


def get_ip():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
    except:
        ip_address = ''
    
    return ip_address


def send_tcp(socket_tcp_obj, payload):
    try:
        if type(payload) is dict:
            payload = json.dumps(payload).encode('utf-8')
        else:
            payload = '{}'.format(payload).encode('utf-8')
        
        #socket_tcp_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #socket_tcp_obj.connect((host, port))
        socket_tcp_obj.sendall(payload)
        print('[ INFO ] TCP payload: {}'.format(payload))
        #socket_tcp_obj.close()
    except Exception as e:
        print('[ EXCEPTION ] {}'.format(e))
    return None


def send_udp(socket_udp_obj, host, port, payload):
    try:
        if type(payload) is dict:
            payload = json.dumps(payload).encode('utf-8')
        else:
            payload = '{}'.format(payload).encode('utf-8')
        
        #socket_udp_obj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_udp_obj.sendto(payload,(host,port))
        print('[ INFO ] UDP payload: {}'.format(payload))
        #socket_udp_obj.close()
    except Exception as e:
        print('[ EXCEPTION ] {}'.format(e))
    return None


def simulate_payload(ip_addr, userid, score_bias=50, enable_sleep=True):
    if enable_sleep:
        time.sleep(random.random()*2)
    
    payload = {
        'ip': ip_addr,
        'userid': userid,
        'name':  'griefing',
        'score': random.triangular(1,100,score_bias) / 100 #random.random()
    }
    return payload


####################################################
# Main
####################################################

def main():
    userid  = "smurfer1" #generate_username()[0]
    ip_addr = get_ip()
    
    '''
    # TCP Connection
    try:
        host = simulator_config['host']
        port = simulator_config['port']
        socket_tcp_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_tcp_obj.connect((host, port))
        while True:
            time.sleep(random.random()*2)
            
            payload = {
                'score': random.random()
            }
            
            send_tcp(socket_tcp_obj, payload)
    except Exception as e:
        print('[ EXCEPTION ] {}'.format(e))
        sys.exit()
    '''
    
    '''
    # UDP Connection
    try:
        #host = simulator_config['host']
        host = simulator_config['host']
        port = simulator_config['port']
        socket_udp_obj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            time.sleep(random.random()*2)
            
            payload = {
                'name':'griefing',
                'score': random.random()
            }
            
            send_udp(socket_udp_obj, host, port, payload)
    except Exception as e:
        print('[ EXCEPTION ] {}'.format(e))
        sys.exit()
    '''
    
    # PubSub Sink
    try:
        pubsub_publisher = pubsub_v1.PublisherClient()
        while True:
            project_id   = 'gaming-demos' 
            pubsub_topic = 'antidote-griefing'
            
            payload = simulate_payload(score_bias=10, userid=userid, ip_addr=ip_addr)
            print('[ INFO ] {}'.format(payload))
            pubsub_publish(pubsub_publisher, project_id=project_id, pubsub_topic=pubsub_topic, message=payload)
    except Exception as e:
        print('[ EXCEPTION ] {}'.format(e))
        sys.exit()


main()


#ZEND
