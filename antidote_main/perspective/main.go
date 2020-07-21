package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
)

// PerspectiveRequest is the JSON response from the Perspective API.
type PerspectiveRequest struct {
	Comment struct {
		Text string `json:"text"`
	} `json:"comment"`
	Languages           []string `json:"languages"`
	RequestedAttributes struct {
		TOXICITY struct {
		} `json:"TOXICITY"`
		SEVERETOXICITY struct {
		} `json:"SEVERE_TOXICITY"`
		IDENTITYATTACK struct {
		} `json:"IDENTITY_ATTACK"`
		INSULT struct {
		} `json:"INSULT"`
		SEXUALLYEXPLICIT struct {
		} `json:"SEXUALLY_EXPLICIT"`
	} `json:"requestedAttributes"`
}

// PerspectiveResponse is the JSON response from the Perspective API.
type PerspectiveResponse struct {
	AttributeScores struct {
		SEVERETOXICITY struct {
			SpanScores []struct {
				Begin int `json:"begin"`
				End   int `json:"end"`
				Score struct {
					Value float64 `json:"value"`
					Type  string  `json:"type"`
				} `json:"score"`
			} `json:"spanScores"`
			SummaryScore struct {
				Value float64 `json:"value"`
				Type  string  `json:"type"`
			} `json:"summaryScore"`
		} `json:"SEVERE_TOXICITY"`
		INSULT struct {
			SpanScores []struct {
				Begin int `json:"begin"`
				End   int `json:"end"`
				Score struct {
					Value float64 `json:"value"`
					Type  string  `json:"type"`
				} `json:"score"`
			} `json:"spanScores"`
			SummaryScore struct {
				Value float64 `json:"value"`
				Type  string  `json:"type"`
			} `json:"summaryScore"`
		} `json:"INSULT"`
		TOXICITY struct {
			SpanScores []struct {
				Begin int `json:"begin"`
				End   int `json:"end"`
				Score struct {
					Value float64 `json:"value"`
					Type  string  `json:"type"`
				} `json:"score"`
			} `json:"spanScores"`
			SummaryScore struct {
				Value float64 `json:"value"`
				Type  string  `json:"type"`
			} `json:"summaryScore"`
		} `json:"TOXICITY"`
		IDENTITYATTACK struct {
			SpanScores []struct {
				Begin int `json:"begin"`
				End   int `json:"end"`
				Score struct {
					Value float64 `json:"value"`
					Type  string  `json:"type"`
				} `json:"score"`
			} `json:"spanScores"`
			SummaryScore struct {
				Value float64 `json:"value"`
				Type  string  `json:"type"`
			} `json:"summaryScore"`
		} `json:"IDENTITY_ATTACK"`
		SEXUALLYEXPLICIT struct {
			SpanScores []struct {
				Begin int `json:"begin"`
				End   int `json:"end"`
				Score struct {
					Value float64 `json:"value"`
					Type  string  `json:"type"`
				} `json:"score"`
			} `json:"spanScores"`
			SummaryScore struct {
				Value float64 `json:"value"`
				Type  string  `json:"type"`
			} `json:"summaryScore"`
		} `json:"SEXUALLY_EXPLICIT"`
	} `json:"attributeScores"`
	Languages         []string `json:"languages"`
	DetectedLanguages []string `json:"detectedLanguages"`
}

// PerspectiveURL is the URL.
const PerspectiveURL = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key="

func getToxicity(req PerspectiveRequest, key string) (map[string]float64, error) {
	var pr PerspectiveResponse
	scores := make(map[string]float64, 5)

	requestBody, err := json.Marshal(req)
	if err != nil {
		return scores, err
	}

	resp, err := http.Post(PerspectiveURL+key, "application/json", bytes.NewBuffer(requestBody))
	if err != nil {
		return scores, err
	}

	if err := json.NewDecoder(resp.Body).Decode(&pr); err != nil {
		panic(err)
	}

	scores["TOXICITY"] = pr.AttributeScores.TOXICITY.SummaryScore.Value
	scores["SEXUALLYEXPLICIT"] = pr.AttributeScores.SEXUALLYEXPLICIT.SummaryScore.Value
	scores["IDENTITYATTACK"] = pr.AttributeScores.IDENTITYATTACK.SummaryScore.Value
	scores["INSULT"] = pr.AttributeScores.INSULT.SummaryScore.Value
	scores["SEVERETOXICITY"] = pr.AttributeScores.SEVERETOXICITY.SummaryScore.Value

	return scores, nil
}

func main() {

	APIKey := os.Getenv("PERSPECTIVE_API_KEY")

	if APIKey == "" {
		fmt.Fprintln(os.Stderr, "Error: No 'PERSPECTIVE_API_KEY' found in your environment variables.")
		os.Exit(1)
	}

	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "Usage: ./<binary> <comment>")
		os.Exit(2)
	}

	testReq := PerspectiveRequest{}
	testReq.Comment.Text = os.Args[1]
	testReq.Languages = []string{"en"}

	tox, err := getToxicity(testReq, APIKey)
	if err != nil {
		fmt.Println(err.Error())
	}

	fmt.Println("Your toxicity breakdown for: '" + os.Args[1] + "' is as follows:")
	fmt.Println("Toxicity:          ", tox["TOXICITY"])
	fmt.Println("Severe Toxicity:   ", tox["SEVERETOXICITY"])
	fmt.Println("Identity Attack:   ", tox["IDENTITYATTACK"])
	fmt.Println("Insult:            ", tox["INSULT"])
	fmt.Println("Sexually Explicit: ", tox["SEXUALLYEXPLICIT"])

}
