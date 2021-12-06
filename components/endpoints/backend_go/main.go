package main

import (
        "fmt"
        "log"
        "net/http"
        "os"
		"encoding/json"

		// go get -u cloud.google.com/go/pubsub
		"cloud.google.com/go/pubsub"
)

const (
	gcpProjectID  = "globalgame"
	pubsubTopicID = "globalgame-antidote-text-input"
)

func main() {

	log.Print("Starting server...")
	
	http.HandleFunc("/", handlerMain)
	http.HandleFunc("/test", handlerTest)
	http.HandleFunc("/chat", handlerChat)

	// Determine port for HTTP service.
	port := os.Getenv("PORT")
	if port == "" {
			port = "8080"
			log.Printf("Defaulting to port %s", port)
	}

	// Start HTTP server.
	log.Printf("Listening on port %s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
			log.Fatal(err)
	}
}

func handlerMain(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "It works.")
}

func handlerTest(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello!")
}

func handlerChat(w http.ResponseWriter, r *http.Request) {

	var chatpaylod map[string]interface{}

    if r.URL.Path != "/chat" {
        http.Error(w, "404 not found.", http.StatusNotFound)
        return
    }

    switch r.Method {
    case "GET":
    
		fmt.Fprintf(w, "Endpoint used for text-based chat input\n")
		//http.ServeFile(w, r, "form.html")
	
    case "POST":
        if err := r.ParseForm(); err != nil {
            fmt.Fprintf(w, "ParseForm() err: %v\n", err)
            return
        }

		fmt.Printf("FormValue %v\n", r)

		// Used for JSON POST
		err := json.NewDecoder(r.Body).Decode(&chatpaylod)
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

		// Convert map to JSON for printing purposes
		jsonStr, err := json.Marshal(chatpaylod)
		if err != nil {
			fmt.Printf("Error: %s", err.Error())
		} else {
			fmt.Println(string(jsonStr))
		}

		// Publish payload to PubSub
        fmt.Fprintf(w, "Payload received: %v", string(jsonStr))

		msg := "test"
		err := publish(w io.Writer, gcpProjectID, pubsubTopicID, msg)
		if err != nil {
			fmt.Printf("Error during PubSub Publish: %s", err.Error())
		} else {
			fmt.Println("Successfully published to PubSub topic %v", topicID)
		}

    default:
        fmt.Fprintf(w, "Warning, only GET and POST methods are supported.")
    }
}

func publish(w io.Writer, projectID, topicID, msg string) error {

	ctx := context.Background()
	client, err := pubsub.NewClient(ctx, projectID)
	if err != nil {
			return fmt.Errorf("pubsub.NewClient: %v", err)
	}
	defer client.Close()

	t := client.Topic(topicID)
	result := t.Publish(ctx, &pubsub.Message{
			Data: map[string]string{
				"text":     "golang",
				"username": "testuser123",
			},
	})
	// Block until the result is returned and a server-generated
	// ID is returned for the published message.
	id, err := result.Get(ctx)
	if err != nil {
			return fmt.Errorf("Get: %v", err)
	}
	fmt.Fprintf(w, "Published a message; msg ID: %v\n", id)
	return nil
}