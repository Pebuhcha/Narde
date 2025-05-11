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
from PIL import Image, ImageTk
from game_logic import GameBoard

class ClientGUI:


  def __init__(self, root):
    self.name = None
    self.opp_name = None

    self.submitted_name = False

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
    self.ip_entry = tk.Entry(self.root)
    self.ip_entry.grid(row=0, column=1, padx=10, pady=5)
    self.ip_entry.insert(0, ip)

    tk.Label(self.root, text="Port:").grid(row=1, column=0, padx=10, pady=5)
    self.port_entry = tk.Entry(self.root)
    self.port_entry.grid(row=1, column=1, padx=10, pady=5)
    self.port_entry.insert(0, port)

    self.status_label = tk.Label(self.root, text="", fg="red")
    self.status_label.grid(row=3, columnspan=2, pady=5)

    def connect():
      ip = self.ip_entry.get()
      port = self.port_entry.get()
      self.save_config(ip, port)
      self.client = self.connect_to_server(ip, port)
      if self.client:
        print('listening')
        threading.Thread(target=self.handle_server_messages).start()

    self.connect_button = tk.Button(self.root, text="Connect", command=connect)
    self.connect_button.grid(row=2, columnspan=2, pady=10)
  
  def connect_to_server(self, ip, port):
    try:
      self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.client.connect((ip, int(port)))
      self.status_label.config(text="Connected to server", fg="green")
      print('in')
      self.show_name_entry()
      print('out')
      return self.client
    except Exception as e:
      self.status_label.config(text=f"Failed to connect: {e}", fg="red")
      return None



  def show_name_entry(self):
    tk.Label(self.root, text="Enter your name:").grid(row=4, column=0, padx=10, pady=5)
    self.name_entry = tk.Entry(self.root)
    self.name_entry.grid(row=4, column=1, padx=10, pady=5)

    submit_button = tk.Button(self.root, text="Submit", command=self.submit_name)
    submit_button.grid(row=5, columnspan=2, pady=10)

  def submit_name(self):
    self.name = self.name_entry.get()
    data = {'action': 'NAME', 'value': self.name}
    self.client.send((json.dumps(data) + '\n').encode('utf-8'))
    self.submitted_name = True
    self.clear_window()
    self.show_game_gui()

  
  def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

  def show_game_gui(self):
      self.root.title("Narde Game")
       # Configure the grid
      self.root.grid_columnconfigure(0, weight=1)
      self.root.grid_columnconfigure(1, weight=1)
      self.root.grid_rowconfigure(0, weight=1)


      # Get screen dimensions
      screen_width = self.root.winfo_screenwidth()
      screen_height = self.root.winfo_screenheight()

      # Load an image using Pillow
      image_path = "/Users/jake/Desktop/narde/board.png"  # Replace with your image path
      pil_image = Image.open(image_path)

      # Calculate the resize ratio to fit the screen
      image_width, image_height = pil_image.size
      ratio = min(screen_width / image_width * 6 / 7, screen_height / image_height * 6 / 7)
      new_width = int(image_width * ratio)
      new_height = int(image_height * ratio)

      # Resize the image
      resized_image = pil_image.resize((new_width, new_height), Image.LANCZOS)

      # Convert the image to a Tkinter PhotoImage
      tk_image = ImageTk.PhotoImage(resized_image)

      # Create a label widget to display the image
      image_label = tk.Label(self.root, image=tk_image)
      image_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

      # Create a frame for the info section
      info_frame = tk.Frame(self.root)
      info_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

      self.root.mainloop()



  def begin_turn():
    print("beginning turn..")
    #simulates a player's full turn
    #bd.play_turn()

  def update_opp_name(self, name):
    self.opp_name = name

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
    roll = GameBoard.roll_dice()[0]
    print("Rolled", roll)
    data = {'action' : 'START ROLL', 'value': roll}
    self.client.send((json.dumps(data) + '\n').encode('utf-8'))
    return roll

  def send_dice_roll(self):
      roll = GameBoard.roll_dice()
      data = {'action': 'ROLL', 'value': roll}
      self.client.send(json.dumps(data).encode('utf-8'))
      return roll

  def send_move(self, board_state):
      data = {'action': 'MOVE', 'value': {'board': board_state}}
      self.client.send((json.dumps(data) + '\n').encode('utf-8'))

  '''def connect_to_server(self):
      self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.client.connect(('127.0.0.1', 5555))'''


  '''
  *************************************************************
  Incoming Server Messages
  *************************************************************
  '''
  def handle_server_messages(self):
    '''while self.name == None:
      continue'''
    '''data = {'action': 'NAME', 'value': 'test'}
    self.client.send((json.dumps(data) + '\n').encode('utf-8'))'''
    while True:
      try:
        message = self.client.recv(1024).decode('utf-8')
        #print("Message:",message)
        data = json.loads(message)
        print("data:", data)
        if data['action'] == 'START':

          #data = {'action': 'TEST', 'value': 'test'}
          #self.client.send(json.dumps(data).encode('utf-8'))
          color = data['value']
          self.bd.set_color(color)
          self.send_die_roll()
        elif data['action'] == 'NAME':
          self.update_opp_name(data['value'])
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
      self.client.send((json.dumps(data) + '\n').encode('utf-8'))
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




def main():
  root = tk.Tk()
  server_gui = ClientGUI(root)
  root.mainloop()

if __name__ == "__main__":
  main()
