package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/googleforgames/antidote/perspective"
	"github.com/gorilla/websocket"
)

var clients = make(map[*websocket.Conn]bool) // connected clients
var broadcast = make(chan Message)           // broadcast channel

// Configure the upgrader
var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

// Message is our app struct:
type Message struct {
	Email    string `json:"email"`
	Username string `json:"username"`
	Message  string `json:"message"`
}

func handleConnections(w http.ResponseWriter, r *http.Request) {
	// Upgrade initial GET request to a websocket
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Fatal(err)
	}
	// Make sure we close the connection when the function returns
	defer ws.Close()

	// Register our new client
	clients[ws] = true

	for {
		var msg Message
		// Read in a new message as JSON and map it to a Message object
		err := ws.ReadJSON(&msg)
		if err != nil {
			log.Printf("error: %v", err)
			delete(clients, ws)
			break
		}
		// Send the newly received message to the broadcast channel
		broadcast <- msg
	}
}

func handleMessages(apiKey string) {
	// func handleMessages() {
	for {
		// Grab the next message from the broadcast channel
		msg := <-broadcast

		// Call the Tox API here:
		tox, err := perspective.GetToxicity(msg.Message, "en", apiKey)
		if err != nil {
			fmt.Println("Error:", err)
		}
		fmt.Printf("Got toxicity score of %v for [%s].\n", tox.TotalScore, msg.Message)

		for client := range clients {
			if tox.TotalScore < 0 {
				toxLine := fmt.Sprintf("@%s, Warning: Impolite conversation will result in user suspension.", msg.Username)
				toxMessage := Message{"toxicity@toxicity.googleapis.com", "Toxicity Bot", toxLine}
				err := client.WriteJSON(toxMessage)
				if err != nil {
					log.Printf("error: %v", err)
					client.Close()
					delete(clients, client)
				}
			} else {
				err := client.WriteJSON(msg)
				if err != nil {
					log.Printf("error: %v", err)
					client.Close()
					delete(clients, client)
				}
			}
		}

	}
}

func main() {

	APIKey := os.Getenv("PERSPECTIVE_API_KEY")

	if APIKey == "" {
		fmt.Fprintln(os.Stderr, "Error: No 'PERSPECTIVE_API_KEY' found in your environment variables.")
		os.Exit(1)
	}

	// Create a simple file server
	fs := http.FileServer(http.Dir("../public"))
	http.Handle("/", fs)

	// Configure websocket route
	http.HandleFunc("/ws", handleConnections)

	// Start listening for incoming chat messages
	go handleMessages(APIKey)

	// Start the server on localhost port 8000 and log any errors
	log.Println("http server started on :8000")
	err := http.ListenAndServe(":8000", nil)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}
