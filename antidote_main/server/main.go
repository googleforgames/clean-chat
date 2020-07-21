package main

import (
	"context"
	"log"
	"net"

	pb "antidote/antidote"

	"github.com/golang/protobuf/ptypes"
	"google.golang.org/grpc"
)

const (
	port = ":50051"
)

// This must be implemented for mystical reasons:
type server struct {
	pb.UnimplementedToxicityServer
}

func (s *server) DetermineToxicity(ctx context.Context, in *pb.ToxicityRequest) (*pb.ToxicityResponse, error) {
	log.Printf("TS  : %s", in.GetMessageTimestamp())
	log.Printf("UUID: %s", in.GetPlayerUuid())
	log.Printf("Mess: %s", in.GetMessage())

	// TODO: Make these actually perform work:
	ts := ptypes.TimestampNow()
	evaluationUUID := "feebdead"
	toxicity := float32(0.75)

	// TODO: Store result in Spanner

	return &pb.ToxicityResponse{
		EvaluationUuid:      evaluationUUID,
		Toxicity:            toxicity,
		EvaluationTimestamp: ts,
		Traceback:           in}, nil
}

func main() {
	lis, err := net.Listen("tcp", port)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	s := grpc.NewServer()

	pb.RegisterToxicityServer(s, &server{})
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
