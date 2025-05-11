import socket
import threading
import json
import uuid
import tkinter as tk
from tkinter import scrolledtext
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class GameState:
    def __init__(self):
        self.current_turn = None
        #self.players = []
        #self.player_names = {}
        self.start_rolls = []
        self.board = {i: [] for i in range(1, 25)}
        self.board[1] = ['w']*15
        self.board[13] = ['b']*15

        self.w_bear_count = 0
        self.b_bear_count = 0

        self.winner = None
        #self.clients = {}



    def determine_first_turn(self):
        if (self.start_rolls[0] == self.start_rolls[1]):
          return
        self.current_turn = 'b' if self.start_rolls[0] > self.start_rolls[1] else 'w'
      
    def move(self, move):
      start, end = move
      checker = self.board[start].pop(0)
      #bear off checker
      if end >= 25:
          if checker == 'w':  
              self.w_bear_count += 1
          else:
              self.b_bear_count += 1
      #simply move checker
      else:
          self.board[end].insert(0, checker)
    
    def check_win_condition(self):
        if self.w_bear_count == 15:
          self.winner = 'w'
          return True
        elif self.b_bear_count == 15:
          self.winner = 'b'
          return True
        return False




class ServerGUI:
  def __init__(self, root):
    self.root = root
    self.root.title("Game Server")
    self.root.grid_rowconfigure(2, weight=1)
    self.root.grid_columnconfigure(0, weight=1)

    self.start_button = tk.Button(root, text="Start Server", command=self.start_server)
    self.start_button.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

    self.client_list_label = tk.Label(root, text="Connected Clients:")
    self.client_list_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    self.client_list = tk.Listbox(root)
    self.client_list.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    self.log_text = scrolledtext.ScrolledText(root, width=50, height=15)
    self.log_text.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    self.client_colors = ['w', 'b']
    self.clients = {}

  def log(self, message):
    self.log_text.insert(tk.END, message + "\n")
    self.log_text.see(tk.END)

  def update_client_list(self):
    self.client_list.delete(0, tk.END)
    for client_id, client_info in self.clients.items():
      self.client_list.insert(tk.END, f"{client_info['address']}")
  
  def num_names(self):
    count = 0
    for client in self.clients.keys():
      if self.clients[client]['name']:
        count += 1
    return count
    
  def other_client(self, client_id):
    ids = list(self.clients.keys())
    if client_id == ids[0]:
      return ids[1]
    else:
      return ids[0]

  def start_server(self):
    self.start_button.config(state=tk.DISABLED)
    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server.bind(("0.0.0.0", 53000))
    self.server.listen(2)
    self.log("Server started, waiting for connections...")
    self.accept_thread = threading.Thread(target=self.accept_clients)
    self.accept_thread.start()

  def accept_clients(self):

    while True:
      try:
        client_socket, addr = self.server.accept()
        client_id = str(uuid.uuid4())
        color = self.client_colors.pop()
        self.clients[client_id] = {
                    'socket': client_socket,
                    'address': addr,
                    'color': color,
                    'name': None
                }
        #self.game_state.players.append(client_socket)
        self.log(f"Accepted connection from {addr}")
        self.update_client_list()
        client_handler = threading.Thread(target=self.handle_client, args=(client_socket, client_id))
        client_handler.start()
      except OSError:
        break  # Socket has been closed, stop accepting clients

  def handle_client(self, client_socket, client_id):
    #prompt client to send start die roll
    self.notify_client("START", self.clients[client_id]['color'], client_id)
    '''message = json.dumps({'action': "START", 'value': self.game_state.clients[client_id]['color']})
    client_socket.send(message.encode('utf-8'))'''
    buffer = ''
    run = True
    while run:

      try:
        data = client_socket.recv(1024).decode('utf-8')
        buffer += data
        while '\n' in buffer:
          message, buffer = buffer.split('\n', 1)
          if message:
  
            try:
              data = json.loads(message)
              self.log(f"Received from client at {self.clients[client_id]['address']}: {data}")
            except json.JSONDecodeError as e:
              self.log(f"JSON decode error: {e} - Data received: {message}")
              run = False
              break
            
            #receive player name and update other client
            if data['action'] == 'NAME':
              #print('Check 1')
              self.clients[client_id]['name'] = data['value']
              #print('Check 2')
              #once both names are received, send both out to the other client
              if self.num_names() == 2:
                #print(self.game_state.player_names)
                #print('Check 3')
                #this client
                
                #print('Check 4', client_socket)
                #print(self.clients)
                other_client_id = self.other_client(client_id)
                self.notify_client('NAME', self.clients[other_client_id]['name'], client_id)
                #print('Check 5', other_client_id)
                self.notify_client('NAME', self.clients[client_id]['name'], other_client_id)
                #print('Check 6')

              #receive start die roll
              elif data['action'] == 'START ROLL':
                self.game_state.start_rolls.append(data['value'])
                #print("Received Start Roll:", data['value'])
                #once both start rolls are received, notify clients of the roll
                if len(self.game_state.start_rolls) == 2:
                  self.game_state.determine_first_turn()

                  #if current_turn is not updated, rolls match, tell client to reroll
                  if self.game_state.current_turn is None:
                    self.game_state.start_rolls = []
                    self.notify_clients("START", self.clients[client_id])
                  
                  #first turn has been decided, notify other clients of rolls and begin turn
                  else:
                    #notify of roll
                    #this client is the last roll received
                    self.notify_client('STARTING ROLL', self.game_state.start_rolls[0], client_id)
                    other_client_id = self.other_client(client_id)
                    self.notify_client('STARTING ROLL', self.game_state.start_rolls[1], other_client_id)

                    #notify of turn
                    self.notify_clients("NEW TURN", self.game_state.current_turn)

              #new dice roll from client
              elif data['action'] == 'ROLL':
                roll = data['value']
                
                #no change in board state, simply notify other client
                other_client_id = self.other_client(client_id)
                self.notify_client('ROLL', roll, other_client_id)

              #record move and update other client
              elif data['action'] == 'MOVE':
                move = data['value']
                self.game_state.move(move)
                other_client_id = self.other_client(client_id)
                self.notify_client('MOVE', move, other_client_id)

                #check for win
                if self.game_state.check_win_condition():
                  self.notify_clients("WIN", self.game_state.winner)
              
              #client ends their turn, tell clients to begin new turn
              elif data['action'] == "END TURN":
                self.game_state.current_turn = 'w' if self.game_state.current_turn == 'b' else 'b'
                self.notify_clients("NEW TURN", self.game_state.current_turn)
              
            #client ends their connections
            elif data['action'] == "DISCONNECT":
              if len(self.clients) == 2:
                other_client_id = self.other_client(client_id)
                self.notify_client("LEFT", self.clients[other_client_id]['color'], other_client_id)
              run = False
              break

        
    
      except ConnectionResetError:
        self.log("Client disconnected unexpectedly")
        break
      except Exception as e:
        self.log(f"Client error: {e}")
        break
  
    self.clean_up_client(client_id)

  def clean_up_client(self, client_id):
    client_socket = self.clients[client_id]['socket']
    client_color = self.clients[client_id]['color']
    try:
        client_socket.close()
    except Exception as e:
        self.log(f"Error closing client socket: {e}")
    del self.clients[client_id]
    self.update_client_list()
    
    self.log(f"Client {client_id} connection closed")
    self.client_colors.append(client_color)


  def notify_client(self, action, game_update, client_id):
    message = json.dumps({'action': action, 'value': game_update})
    self.clients[client_id]['socket'].send(message.encode('utf-8'))
    self.log(f"Sent {message} to client at {self.clients[client_id]['address']}")

  def notify_clients(self, action, game_update):

    message = json.dumps({'action': action, 'value': game_update})
    for client_info in self.clients.values():
      client_info['socket'].send(message.encode('utf-8'))
      self.log(f"Sent {message} to client at {client_info['address']}")
  
  def on_closing(self):
    if self.server:
      self.server.close()
    if self.accept_thread:
      self.accept_thread.join()
    for client_info in self.clients.values():
      try:
        client_info['socket'].close()
      except Exception as e:
        self.log(f"Error closing client socket: {e}")
    self.root.destroy()

def main():
  root = tk.Tk()
  server_gui = ServerGUI(root)
  root.mainloop()


if __name__ == "__main__":
  main()
