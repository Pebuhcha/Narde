import socket
import threading
import json
import tkinter as tk
from tkinter import scrolledtext
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class GameState:
    def __init__(self):
        self.current_turn = None
        self.players = []
        self.player_names = {}
        self.start_rolls = []
        self.board = {i: [] for i in range(1, 25)}
        self.board[1] = ['w']*15
        self.board[13] = ['b']*15

        self.w_bear_count = 0
        self.b_bear_count = 0

        self.winner = None

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
        self.start_button = tk.Button(root, text="Start Server", command=self.start_server)
        self.start_button.pack(pady=20)
        self.client_list_label = tk.Label(root, text="Connected Clients:")
        self.client_list_label.pack(pady=10)
        self.client_list = tk.Listbox(root)
        self.client_list.pack(pady=10)
        self.log_text = scrolledtext.ScrolledText(root, width=50, height=15)
        self.log_text.pack(pady=10)
        self.server = None
        self.game_state = GameState()
        self.accept_thread = None

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def update_client_list(self):
        self.client_list.delete(0, tk.END)
        for player in self.game_state.players:
            self.client_list.insert(tk.END, player.getpeername())

    def start_server(self):
        self.start_button.config(state=tk.DISABLED)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("0.0.0.0", 53000))
        self.server.listen(2)
        self.log("Server started, waiting for connections...")
        self.accept_thread = threading.Thread(target=self.accept_clients)
        self.accept_thread.start()

    def accept_clients(self):
        client_counter = 0
        client_colors = ['w', 'b']
        while True:
            try:
              client_socket, addr = self.server.accept()
              self.game_state.players.append(client_socket)
              self.log(f"Accepted connection from {addr}")
              self.update_client_list()
              client_handler = threading.Thread(target=self.handle_client, args=(client_socket, client_colors[client_counter]))
              client_handler.start()
              client_counter += 1
            except OSError:
              break  # Socket has been closed, stop accepting clients

    def handle_client(self, client_socket, player_color):
      #prompt client to send start die roll
      #self.notify_client('START', player_color, client_socket)
      while True:
        try:
          '''data = client_socket.recv(4096)
          if not data:
              break
          logging.debug(f"Received data: {data}")
          try:
              message = json.loads(data.decode('utf-8'))
              logging.debug(f"Decoded JSON: {message}")
              # Process the message
          except json.JSONDecodeError as e:
              logging.error(f"JSON decode error: {e}")'''
          message = client_socket.recv(1024).decode('utf-8')
          data = json.loads(message)
          
          #receive player name and update other client
          if data['action'] == 'NAME':
            self.game_state.player_names[client_socket] = data['value']

            #once both names are received, send both out to the other client
            if len(self.game_state.player_names) == 2:
              #this client
              self.notify_client('NAME', self.game_state.player_names[client_socket], client_socket)

              other_client = (self.game_state.players - client_socket)[0]
              self.notify_client('NAME', self.game_state.player_names[other_client], other_client)

          #receive start die roll
          elif data['action'] == 'START ROLL':
            self.game_state.start_rolls.append(data['value'])

            #once both start rolls are received, notify clients of the roll
            if len(self.game_state.start_rolls) == 2:
              self.game_state.determine_first_turn()

              #if current_turn is not updates, rolls match, tell client to reroll
              if (self.game_state.current_turn == None):
                self.game_state.start_rolls = []
                self.notify_clients("START", player_color)
              
              #first turn has been decided, notify other clients of rolls and begin turn
              else:
                #notify of roll
                self.notify_client('STARTING ROLL', self.game_state.player_names[1], client_socket)
                other_client = (self.game_state.players - client_socket)[0]
                self.notify_client('STARTING ROLL', self.game_state.player_names[0], other_client)

                #notify of turn
                self.notify_clients("NEW TURN", self.game_state.current_turn)

          #new dice roll from client
          elif data['action'] == 'ROLL':
            roll = data['value']
            
            #no change in board state, simply notify other client
            other_client = (self.game_state.players - client_socket)[0]
            self.notify_client('ROLL', roll, other_client)

          #record move and update other client
          elif data['action'] == 'MOVE':
            move = data['value']
            self.game_state.move(move)
            other_client = (self.game_state.players - client_socket)[0]
            self.notify_client('MOVE', move, other_client)

            #check for win
            if self.game_state.check_win_condition():
              self.notify_clients("WIN", self.game_state.winner)
          
          #client ends their turn, tell clients to begin new turn
          elif data['action'] == "END TURN":
            self.game_state.current_turn = 'w' if self.game_state.current_turn == 'b' else 'b'
            self.notify_clients("NEW TURN", self.game_state.current_turn)
          
          #client ends their connections
          elif data['action'] == "DISCONNECT":
            if len(self.game_state.players) == 2:
              other_client = (self.game_state.players - client_socket)[0]
              self.notify_client("LEFT", self.game_state.player_names[client_socket], other_client)
            break
            
        except json.JSONDecodeError:
            self.log("Received invalid JSON data")
        except ConnectionResetError:
            self.log("Client disconnected unexpectedly")
            break
        except Exception as e:
            self.log(f"Client error: {e}")
            break
      self.clean_up_client(client_socket)

    def clean_up_client(self, client_socket):
      try:
          client_socket.close()
      except Exception as e:
          self.log(f"Error closing client socket: {e}")
      if client_socket in self.game_state.players:
          self.game_state.players.remove(client_socket)
      if client_socket in self.game_state.player_names.keys():
        del self.game_state.player_names[client_socket]
      self.update_client_list()
      self.log("Client connection closed")


    def notify_client(self, action, game_update, client_socket):
      message = json.dumps({'action': action, 'value': game_update})
      client_socket.send(message.encode('utf-8'))

    def notify_clients(self, action, game_update):

        message = json.dumps({'action': action, 'value': game_update})
        for player in self.game_state.players:
            player.send(message.encode('utf-8'))
    
    def on_closing(self):
        if self.server:
            self.server.close()
        if self.accept_thread:
            self.accept_thread.join()
        for player in self.game_state.players:
            try:
                player.close()
            except Exception as e:
                self.log(f"Error closing player socket: {e}")
        self.root.destroy()

def main():
    root = tk.Tk()
    server_gui = ServerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
