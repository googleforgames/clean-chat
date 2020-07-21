package main

import (
	"context"
	"log"
	"time"

	pb "antidote/antidote"

	"github.com/golang/protobuf/ptypes"
	"google.golang.org/grpc"
)

const (
	address     = "localhost:50051"
	defaultName = "world"
)

func main() {
	// Set up a connection to the server.
	conn, err := grpc.Dial(address, grpc.WithInsecure(), grpc.WithBlock())
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()
	c := pb.NewToxicityClient(conn)

	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	ts := ptypes.TimestampNow()
	playerUUID := "deadbeef"
	message := "This is a message."

	r, err := c.DetermineToxicity(ctx, &pb.ToxicityRequest{
		MessageTimestamp: ts,
		PlayerUuid:       playerUUID,
		Message:          message})
	if err != nil {
		log.Fatalf("could not greet: %v", err)
	}

	log.Printf("UUID: %s", r.GetEvaluationUuid())
	log.Printf("TOX : %v", r.GetToxicity())
	log.Printf("TS  : %s", r.GetEvaluationTimestamp())
	log.Printf("TRAC: %s", r.GetTraceback())
}
