// rec --channels=1 --bits=16 --rate=16k --type=raw --no-show-progress - | ./livecaption
package main

// [START speech_transcribe_streaming_mic]
import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"regexp"
	"strings"

	speech "cloud.google.com/go/speech/apiv1"
	speechpb "google.golang.org/genproto/googleapis/cloud/speech/v1"
)

type antidoteResponse struct {
	Outputs struct {
		Prediction  [][]float64 `json:"prediction"`
		Description string      `json:"description"`
	} `json:"outputs"`
}

type antidoteRequest struct {
	Inputs struct {
		Review []string `json:"review"`
	} `json:"inputs"`
}

func censor(offense string) string {
	if len(offense) < 4 {
		return strings.Repeat("*", len(offense))
	}
	return offense[0:1] + strings.Repeat("*", len(offense)-2) + offense[len(offense)-1:len(offense)]
}

func getToxicity(comment string) float64 {

	req := antidoteRequest{}
	req.Inputs.Review = make([]string, 1)
	req.Inputs.Review[0] = comment
	jsonReq, _ := json.Marshal(req)
	var jsonResp []byte

	resp, err := http.Post("http://localhost:8501/v1/models/bert_model:predict", "application/json", bytes.NewBuffer(jsonReq))
	if err != nil {
		fmt.Printf("The HTTP request failed with error %s\n", err)
	} else {
		jsonResp, _ = ioutil.ReadAll(resp.Body)
		//fmt.Println(string(jsonResp))
	}

	toxicity := antidoteResponse{}
	if err := json.Unmarshal(jsonResp, &toxicity); err != nil {
		fmt.Printf("The unmarshalling failed %s\n", err)
	}

	return toxicity.Outputs.Prediction[0][0]

}

func main() {

	file, _ := os.Open("bad-words.txt")
	defer file.Close()

	var badWords string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		badWords += scanner.Text() + "|"
	}

	bwrx := regexp.MustCompile(badWords[0 : len(badWords)-1])

	ctx := context.Background()

	client, err := speech.NewClient(ctx)
	if err != nil {
		log.Fatal(err)
	}
	stream, err := client.StreamingRecognize(ctx)
	if err != nil {
		log.Fatal(err)
	}
	// Send the initial configuration message.
	if err := stream.Send(&speechpb.StreamingRecognizeRequest{
		StreamingRequest: &speechpb.StreamingRecognizeRequest_StreamingConfig{
			StreamingConfig: &speechpb.StreamingRecognitionConfig{
				Config: &speechpb.RecognitionConfig{
					Encoding:        speechpb.RecognitionConfig_LINEAR16,
					SampleRateHertz: 16000,
					LanguageCode:    "en-US",
				},
			},
		},
	}); err != nil {
		log.Fatal(err)
	}

	go func() {
		// Pipe stdin to the API.
		buf := make([]byte, 1024)
		for {
			n, err := os.Stdin.Read(buf)
			if n > 0 {
				if err := stream.Send(&speechpb.StreamingRecognizeRequest{
					StreamingRequest: &speechpb.StreamingRecognizeRequest_AudioContent{
						AudioContent: buf[:n],
					},
				}); err != nil {
					log.Printf("Could not send audio: %v", err)
				}
			}
			if err == io.EOF {
				// Nothing else to pipe, close the stream.
				if err := stream.CloseSend(); err != nil {
					log.Fatalf("Could not close stream: %v", err)
				}
				return
			}
			if err != nil {
				log.Printf("Could not read from stdin: %v", err)
				continue
			}
		}
	}()

	for {
		resp, err := stream.Recv()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Fatalf("Cannot stream results: %v", err)
		}
		if err := resp.Error; err != nil {
			// Workaround while the API doesn't give a more informative error.
			if err.Code == 3 || err.Code == 11 {
				log.Print("WARNING: Speech recognition request exceeded limit of 60 seconds.")
			}
			log.Fatalf("Could not recognize: %v", err)
		}
		for _, result := range resp.Results {

			comment := result.Alternatives[0].Transcript
			toxicity := getToxicity(comment)

			if toxicity < 0.25 {
				fmt.Println("Normal speech detected:", comment)
			} else if toxicity < 0.5 {
				fmt.Println("Slightly bad speech detected:", bwrx.ReplaceAllStringFunc(comment, censor))
			} else if toxicity < 0.75 {
				fmt.Println("Really bad speech detected:", bwrx.ReplaceAllStringFunc(comment, censor))
			} else {
				fmt.Println("Hateful speech detected:", bwrx.ReplaceAllStringFunc(comment, censor))
			}

			// fmt.Printf("Result: %+v\n", result.Alternatives[0].Transcript)
			// Result: alternatives:{transcript:"will this function"  confidence:0.9136761}  is_final:true  result_end_time:{seconds:3  nanos:690000000}

		}
	}
}

// [END speech_transcribe_streaming_mic]
