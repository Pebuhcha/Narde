#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 25 13:15:35 2024

@author: jake
"""

import socket
import json
import threading
import tkinter as tk
from tkinter import messagebox
import configparser
import os
from game_logic import GameBoard

class ClientGUI:

  '''
  *************************************************************
  Game Logic Helper Methods
  *************************************************************
  '''
  def __init__(self, root):

    # Define configuration file path
    self.CONFIG_FILE = 'client_config.ini'
    self.client = None
    self.bd = GameBoard()
    self.root = root
    self.server_connection_setup()
    self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

  def server_connection_setup(self):
    self.root.title("Narde Game Client")

    ip, port = self.load_config()

    tk.Label(self.root, text="Server IP:").grid(row=0, column=0, padx=10, pady=5)
    ip_entry = tk.Entry(self.root)
    ip_entry.grid(row=0, column=1, padx=10, pady=5)
    ip_entry.insert(0, ip)

    tk.Label(self.root, text="Port:").grid(row=1, column=0, padx=10, pady=5)
    port_entry = tk.Entry(self.root)
    port_entry.grid(row=1, column=1, padx=10, pady=5)
    port_entry.insert(0, port)

    def connect():
        ip = ip_entry.get()
        port = port_entry.get()
        self.save_config(ip, port)
        self.client = self.connect_to_server(ip, port)
        if self.client:
            threading.Thread(target=self.handle_server_messages).start()
    
    connect_button = tk.Button(self.root, text="Connect", command=connect)
    connect_button.grid(row=2, columnspan=2, pady=10)

  '''
  *************************************************************
  GUI Methods
  *************************************************************
  '''

  def begin_turn():
    print("beginning turn..")
    #simulates a player's full turn
    #bd.play_turn()

  '''
  GUI Updates from Opponent
  '''

  def await_turn():
    print("awaiting turn..")

  def update_starting_die(die):
    print("Opponent rolled", die)
    print("updating starting die")

  def update_opp_dice(dice):
    print("updating opp dice..")

  def move_opp_checker(move):
    print("moving opp checker..")

  def finish_game(winner):
    print("finishing game..")

  def update_opp_disconnect(name):
    i=0

  '''
  *************************************************************
  Outgoing Server Messages
  *************************************************************
  '''
  def send_die_roll(self):
    '''roll = GameBoard.roll_dice()[0]
    print("Rolled", roll)
    data = {'action' : 'START ROLL', 'value': roll}
    self.client.send(json.dumps(data).encode('utf-8'))
    return roll'''

  def send_dice_roll(self):
      roll = GameBoard.roll_dice()
      data = {'action': 'ROLL', 'value': roll}
      self.client.send(json.dumps(data).encode('utf-8'))
      return roll

  def send_move(self, board_state):
      data = {'action': 'MOVE', 'value': {'board': board_state}}
      self.client.send(json.dumps(data).encode('utf-8'))

  def connect_to_server(self):
      self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.client.connect(('127.0.0.1', 5555))


  '''
  *************************************************************
  Incoming Server Messages
  *************************************************************
  '''
  def handle_server_messages(self):
    while True:
      try:
        message = self.client.recv(1024).decode('utf-8')
        data = json.loads(message)
        if data['action'] == 'START':
          color = data['value']
          self.bd.set_color(color)
          self.send_die_roll()
        elif data['action'] == 'STARTING ROLL':
          die = data['value']
          self.update_starting_die(die)
        elif data['action'] == 'NEW TURN':
          if data['value'] == self.bd.get_color():
            self.begin_turn()
          else:
            self.await_turn()
        elif data['action'] == 'ROLL':
          self.update_opp_dice(data['value'])
        elif data['action'] == 'MOVE':
          self.move_opp_checker(data['value'])
        elif data['action'] == 'WIN':
          self.finish_game(data['value'])
        elif data['action'] == 'LEFT':
          self.update_opp_disconnect(data['value'])
          
      except Exception as e:
        print(f"Server error: {e}")
        break
      
      self.clean_up_client()

  def clean_up_client(self):
      if self.client:
          try:
              self.client.close()
          except Exception as e:
              print(f"Error closing client socket: {e}")

  def on_closing(self):
      self.send_disconnect()
      self.clean_up_client()
      self.root.destroy()

  def send_disconnect(self):
      data = {'action': 'DISCONNECT'}
      try:
          self.client.send(json.dumps(data).encode('utf-8'))
      except Exception as e:
          print(f"Error sending disconnect message: {e}")
      




  

  def save_config(self, ip, port):
      config = configparser.ConfigParser()
      config['DEFAULT'] = {
          'ServerIP': ip,
          'Port': port
      }
      with open(self.CONFIG_FILE, 'w') as configfile:
          config.write(configfile)

  def load_config(self):
      config = configparser.ConfigParser()
      if os.path.exists(self.CONFIG_FILE):
          config.read(self.CONFIG_FILE)
          ip = config['DEFAULT'].get('ServerIP', '127.0.0.1')
          port = config['DEFAULT'].get('Port', '53000')
      else:
          ip = '127.0.0.1'
          port = '53000'
      return ip, port

  def connect_to_server(self, ip, port):
      try:
          self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          self.client.connect((ip, int(port)))
          messagebox.showinfo("Connection", f"Connected to server at {ip}:{port}")
          return self.client
      except Exception as e:
          messagebox.showerror("Connection Error", f"Failed to connect to server: {e}")
          return None



def main():
    root = tk.Tk()
    server_gui = ClientGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
