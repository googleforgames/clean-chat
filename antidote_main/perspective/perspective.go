package perspective

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

// Request is the JSON response from the Perspective API.
type Request struct {
	Comment struct {
		Text string `json:"text"`
	} `json:"comment"`
	Languages           []string `json:"languages"`
	RequestedAttributes struct {
		TOXICITY struct {
		} `json:"TOXICITY"`
		// SEVERETOXICITY struct {
		// } `json:"SEVERE_TOXICITY"`
		IDENTITYATTACK struct {
		} `json:"IDENTITY_ATTACK"`
		INSULT struct {
		} `json:"INSULT"`
		SEXUALLYEXPLICIT struct {
		} `json:"SEXUALLY_EXPLICIT"`
	} `json:"requestedAttributes"`
}

// Response is the JSON response from the Perspective API.
type Response struct {
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

// ToxicityRating holds just the values we care about for a given comment, less the API cruft.
type ToxicityRating struct {
	IdentityAttackScore   float64
	InsultScore           float64
	SexuallyExplicitScore float64
	ToxicityScore         float64
	TotalScore            float64
}

// NewToxicityRating is used as a constructor for type ToxicityRating because of additional math.
func NewToxicityRating(ToxicityScore, IdentityAttackScore, InsultScore, SexuallyExplicitScore float64) ToxicityRating {
	// FIXME: Sort the import variables.

	TotalScore := (ToxicityScore * IdentityAttackScore * InsultScore * SexuallyExplicitScore) / ((ToxicityScore * IdentityAttackScore * InsultScore * SexuallyExplicitScore) + (1 - ToxicityScore*1 - IdentityAttackScore*1 - InsultScore*1 - SexuallyExplicitScore))
	t := ToxicityRating{IdentityAttackScore, InsultScore, SexuallyExplicitScore, ToxicityScore, TotalScore}
	return t
}

// GetToxicity processes the request from perspectives, performs some math, and returns your total score.
func GetToxicity(message, lang, apiKey string) (ToxicityRating, error) {

	req := Request{}
	req.Comment.Text = message
	req.Languages = []string{"en"}

	var tr ToxicityRating
	var pr Response

	if len(apiKey) < 30 {
		return tr, fmt.Errorf("Invalid API Key: %s", apiKey)
	}

	requestBody, err := json.Marshal(req)
	if err != nil {
		return tr, err
	}

	// FIXME: Is there some better way of mashing the API key with the URL?
	resp, err := http.Post(PerspectiveURL+apiKey, "application/json", bytes.NewBuffer(requestBody))
	if err != nil {
		return tr, err
	}

	if err := json.NewDecoder(resp.Body).Decode(&pr); err != nil {
		panic(err)
	}

	tr = NewToxicityRating(
		pr.AttributeScores.TOXICITY.SummaryScore.Value,
		pr.AttributeScores.IDENTITYATTACK.SummaryScore.Value,
		pr.AttributeScores.INSULT.SummaryScore.Value,
		pr.AttributeScores.SEXUALLYEXPLICIT.SummaryScore.Value,
	)

	return tr, nil
}

// func main() {

// 	APIKey := os.Getenv("PERSPECTIVE_API_KEY")

// 	if APIKey == "" {
// 		fmt.Fprintln(os.Stderr, "Error: No 'PERSPECTIVE_API_KEY' found in your environment variables.")
// 		os.Exit(1)
// 	}

// 	if len(os.Args) != 2 {
// 		fmt.Fprintln(os.Stderr, "Usage: ./<binary> <comment>")
// 		os.Exit(2)
// 	}

// 	testReq := Request{}
// 	testReq.Comment.Text = os.Args[1]
// 	testReq.Languages = []string{"en"}

// 	tox, err := getToxicity(testReq, APIKey)
// 	if err != nil {
// 		fmt.Println(err.Error())
// 	}

// 	fmt.Println("Your toxicity breakdown for: '" + os.Args[1] + "' is as follows:")
// 	fmt.Println("Toxicity:          ", tox["TOXICITY"])
// 	fmt.Println("Severe Toxicity:   ", tox["SEVERETOXICITY"])
// 	fmt.Println("Identity Attack:   ", tox["IDENTITYATTACK"])
// 	fmt.Println("Insult:            ", tox["INSULT"])
// 	fmt.Println("Sexually Explicit: ", tox["SEXUALLYEXPLICIT"])

// 	testRating := NewToxicityRating(tox["TOXICITY"], tox["IDENTITYATTACK"], tox["INSULT"], tox["SEXUALLYEXPLICIT"])
// 	fmt.Println("----------------------------------------")
// 	fmt.Println("Final value is:    ", testRating.TotalScore)

// }
