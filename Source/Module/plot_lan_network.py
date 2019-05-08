#File Import
import pcap_reader
import communication_details_fetch
import tor_traffic_handle
import malicious_traffic_identifier
import device_details_fetch
import memory

import networkx as nx
#import matplotlib.pyplot as plt

from graphviz import Digraph
import threading
import os

class plotLan:

    def __init__(self, filename, path, option="Tor"):
        self.directory = os.path.join(path, "Report")
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.filename = os.path.join(self.directory, filename+"_"+option)

        self.styles = {
            'graph': {
                'label': 'PcapGraph',
                'fontsize': '16',
                'fontcolor': 'black',
                'bgcolor': 'grey',
                'rankdir': 'BT',
                'dpi':'600'
            },
            'nodes': {
                'fontname': 'Helvetica',
                'shape': 'circle',
                'fontcolor': 'black',
                'color': ' black',
                'style': 'filled',
                'fillcolor': 'yellow',
            }
        }

        self.sessions = memory.packet_db.keys()
        device_details_fetch.fetchDeviceDetails("ieee").fetch_info()
        if option == "Malicious" or option == "All":
            self.mal_identify = malicious_traffic_identifier.maliciousTrafficIdentifier()
        if option == "Tor" or option == "All":
            self.tor_identify = tor_traffic_handle.torTrafficHandle().tor_traffic_detection()
        self.draw_graph(option)
    
    def apply_styles(self, graph, styles):
        graph.graph_attr.update(
            ('graph' in styles and styles['graph']) or {}
        )
        graph.node_attr.update(
            ('nodes' in styles and styles['nodes']) or {}
        )
        return graph

    def apply_custom_style(self, graph, color):
        style = {'edges': {
                'style': 'dashed',
                'color': color,
                'arrowhead': 'open',
                'fontname': 'Courier',
                'fontsize': '12',
                'fontcolor': color,
        }}
        graph.edge_attr.update(
            ('edges' in style and style['edges']) or {}
        )
        return graph

    def draw_graph(self,option="All"):
        f = Digraph('network_diagram - '+option, filename=self.filename, engine="dot", format="png")
        f.attr(rankdir='LR', size='8,5')

        f.attr('node', shape='doublecircle')
        f.node('defaultGateway')

        f.attr('node', shape='circle')

        print("Starting Graph Plotting")

        if option == "All":
            # add nodes
            for session in self.sessions:
                src, dst, port = session.split("/")

                # TODO: Improvise this logic below
                # * graphviz graph is not very good with the ":" in strings
                if ":" in src:
                    map_src = src.replace(":",".")
                else:
                    map_src = src
                if ":" in dst:
                    map_dst = dst.replace(":", ".")
                else:
                    map_dst = dst
                
                # Lan Host
                if src not in memory.lan_hosts:
                    curr_node = map_src
                    f.node(curr_node)
                else:
                    curr_node = memory.lan_hosts[src]["node"]
                    f.node(curr_node)

                # Destination
                if dst in memory.destination_hosts:
                    destination = 'defaultGateway'
                    dlabel = memory.destination_hosts[dst]
                else:
                    if dst in memory.lan_hosts:
                        destination = memory.lan_hosts[dst]["node"]
                        dlabel = ""
                    else:
                        destination = dst
                        dlabel = ""

                if session in memory.possible_tor_traffic:
                    f.edge(curr_node, destination, label='TOR: ' + str(map_dst) ,color="white")
                elif session in memory.possible_mal_traffic:
                    f.edge(curr_node, destination, label='Malicious: ' + str(map_dst) ,color="red")
                else:
                    if port == "443":
                        f.edge(curr_node, destination, label='HTTPS: ' + map_dst +": "+dlabel, color = "blue")
                    if port == "80":
                        f.edge(curr_node, destination, label='HTTP: ' + map_dst +": "+dlabel, color = "green")
                    if port == "ICMP":
                        f.edge(curr_node, destination, label='ICMP: ' + str(map_dst) ,color="black")
                    if port == "53":
                        f.edge(curr_node, destination, label='DNS: ' + str(map_dst) ,color="orange")

        elif option == "HTTP":
            for session in self.sessions:
                src, dst, port = session.split("/")
                # TODO: Improvise this logic below
                # * graphviz graph is not very good with the ":" in strings
                if ":" in src:
                    map_src = src.replace(":",".")
                else:
                    map_src = src
                if ":" in dst:
                    map_dst = dst.replace(":", ".")
                else:
                    map_dst = dst

                # Lan Host
                if src not in memory.lan_hosts:
                    curr_node = map_src
                    f.node(curr_node)
                else:
                    curr_node = memory.lan_hosts[src]["node"]
                    f.node(curr_node)
                
                # Destination Host
                if dst in memory.destination_hosts:
                    destination = 'defaultGateway'
                    dlabel = memory.destination_hosts[dst]
                else:
                    if dst in memory.lan_hosts:
                        destination = memory.lan_hosts[dst]["node"]
                        dlabel = ""
                    else:
                        destination = dst
                        dlabel = ""


                if port == "80":
                    f.edge(curr_node, destination, label='HTTP: ' + str(map_dst)+": "+dlabel, color = "green")

        elif option == "HTTPS":
            for session in self.sessions:
                src, dst, port = session.split("/")
                # TODO: Improvise this logic below
                # * graphviz graph is not very good with the ":" in strings
                if ":" in src:
                    map_src = src.replace(":",".")
                else:
                    map_src = src
                if ":" in dst:
                    map_dst = dst.replace(":", ".")
                else:
                    map_dst = dst

                # Lan Host
                if src not in memory.lan_hosts:
                    curr_node = map_src
                    f.node(curr_node)
                else:
                    curr_node = memory.lan_hosts[src]["node"]
                    f.node(curr_node)

                # Destination Host
                if dst in memory.destination_hosts:
                    destination = 'defaultGateway'
                    dlabel = memory.destination_hosts[dst]
                else:
                    if dst in memory.lan_hosts:
                        destination = memory.lan_hosts[dst]["node"]
                        dlabel = ""
                    else:
                        destination = dst
                        dlabel = ""


                if port == "443":
                    f.edge(curr_node, destination, label='HTTPS: ' + str(map_dst)+": "+dlabel, color = "blue")

        elif option == "Tor":
            for session in self.sessions:
                src, dst, port = session.split("/")
                # TODO: Improvise this logic below
                # * graphviz graph is not very good with the ":" in strings
                if ":" in src:
                    map_src = src.replace(":",".")
                else:
                    map_src = src
                if ":" in dst:
                    map_dst = dst.replace(":", ".")
                else:
                    map_dst = dst

                # Lan Host
                if src not in memory.lan_hosts:
                    curr_node = map_src
                    f.node(curr_node)
                else:
                    curr_node = memory.lan_hosts[src]["node"]
                    f.node(curr_node)

                # Destination Host
                if dst in memory.destination_hosts:
                    destination = 'defaultGateway'
                    dlabel = memory.destination_hosts[dst]
                else:
                    if dst in memory.lan_hosts:
                        destination = memory.lan_hosts[dst]["node"]
                        dlabel = ""
                    else:
                        destination = dst
                        dlabel = ""


                if session in memory.possible_tor_traffic:
                    f.edge(curr_node, destination, label='TOR: ' + str(map_dst) ,color="white")

        elif option == "Malicious":
            # TODO: would we need to iterate over and over all the session irrespective of the properties
            for session in self.sessions:
                src, dst, port = session.split("/")
                # TODO: Improvise this logic below
                # * graphviz graph is not very good with the ":" in strings
                if ":" in src:
                    map_src = src.replace(":",".")
                else:
                    map_src = src
                if ":" in dst:
                    map_dst = dst.replace(":", ".")
                else:
                    map_dst = dst

                # Lan Host
                if src not in memory.lan_hosts:
                    curr_node = map_src
                    f.node(curr_node)
                else:
                    curr_node = memory.lan_hosts[src]["node"]
                    f.node(curr_node)

                # Destination Host
                if dst in memory.destination_hosts:
                    destination = 'defaultGateway'
                    dlabel = memory.destination_hosts[dst]
                else:
                    if dst in memory.lan_hosts:
                        destination = memory.lan_hosts[dst]["node"]
                        dlabel = ""
                    else:
                        destination = dst
                        dlabel = ""

                if session in memory.possible_mal_traffic:
                    f.edge(curr_node, destination, label='Malicious: ' + str(map_dst) ,color="red")
            
        elif option == "ICMP":
            for session in self.sessions:
                src, dst, protocol = session.split("/")
                if ":" in src:
                    map_src = src.replace(":",".")
                else:
                    map_src = src
                if ":" in dst:
                    map_dst = dst.replace(":", ".")
                else:
                    map_dst = dst

                # Lan Host
                if src not in memory.lan_hosts:
                    curr_node = map_src
                    f.node(curr_node)
                else:
                    curr_node = memory.lan_hosts[src]["node"]
                    f.node(curr_node)

                # Destination Host
                if dst in memory.destination_hosts:
                    destination = 'defaultGateway'
                    dlabel = memory.destination_hosts[dst]
                else:
                    if dst in memory.lan_hosts:
                        destination = memory.lan_hosts[dst]["node"]
                        dlabel = ""
                    else:
                        destination = dst
                        dlabel = ""

                if protocol == "ICMP":
                    f.edge(curr_node, destination, label='ICMP: ' + str(map_dst) ,color="black")
    
        elif option == "DNS":
            for session in self.sessions:
                src, dst, port = session.split("/")
                if ":" in src:
                    map_src = src.replace(":",".")
                else:
                    map_src = src
                if ":" in dst:
                    map_dst = dst.replace(":", ".")
                else:
                    map_dst = dst

                # Lan Host
                if src not in memory.lan_hosts:
                    curr_node = map_src
                    f.node(curr_node)
                else:
                    curr_node = memory.lan_hosts[src]["node"]
                    f.node(curr_node)

                # Destination Host
                if dst in memory.destination_hosts:
                    destination = 'defaultGateway'
                    dlabel = memory.destination_hosts[dst]
                else:
                    if dst in memory.lan_hosts:
                        destination = memory.lan_hosts[dst]["node"]
                        dlabel = ""
                    else:
                        destination = dst
                        dlabel = ""

                if port == "53":
                    f.edge(curr_node, destination, label='DNS: ' + str(map_dst) ,color="orange")

        
        self.apply_styles(f,self.styles)
        f.render()

def main():
    # draw example
    pcapfile = pcap_reader.PcapEngine('examples/torExample.pcap', "scapy")
    print("Reading Done....")
    details = communication_details_fetch.trafficDetailsFetch("sock")
    import sys
    print(sys.path[0])
    network = plotLan("test", sys.path[0])

#main()
