package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
)

// DataElement represents a single data element record from the CSV.
type DataElement struct {
	ID           string       `json:"id"`
	Title        string       `json:"title"`
	Description  string       `json:"description"`
	Aliases      []string     `json:"aliases"`
	Domain       string       `json:"domain"`
	Translations Translations `json:"translations"`
}

// Purpose represents a purpose record from the CSV.
type Purpose struct {
	ID           string       `json:"purpose_id"`
	Industry     string       `json:"industry"`
	SubCategory  string       `json:"sub_category"`
	DataElements []string     `json:"data_elements"`
	Translations Translations `json:"translations"`
}

// Translations holds the translated purpose descriptions.
type Translations struct {
	ENG string `json:"eng"`
	ASM string `json:"asm"`
	BEN string `json:"ben"`
	BRX string `json:"brx"`
	DOI string `json:"doi"`
	GUJ string `json:"guj"`
	HIN string `json:"hin"`
	KAN string `json:"kan"`
	KAS string `json:"kas"`
	KOK string `json:"kok"`
	MAI string `json:"mai"`
	MAL string `json:"mal"`
	MNI string `json:"mni"`
	MAR string `json:"mar"`
	NEP string `json:"nep"`
	ORI string `json:"ori"`
	PAN string `json:"pan"`
	SAN string `json:"san"`
	TAM string `json:"tam"`
	TEL string `json:"tel"`
	SAT string `json:"sat"`
	SND string `json:"snd"`
	URD string `json:"urd"`
}

// Global variables to store the loaded data.
var dataElements []DataElement
var purposes []Purpose

// main function execution with routes
func main() {
	if err := loadAllData(); err != nil {
		log.Fatalf("Failed to load data: %v", err)
	}

	http.HandleFunc("/data-elements", getDataElementsHandler)
	http.HandleFunc("/purposes", getPurposesHandler)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8005"
	}

	log.Printf("Server starting on port :%s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}

}

// loadAllData handles loading both CSV files.
func loadAllData() error {
	dataElementsFile := os.Getenv("DATA_ELEMENTS_PATH")
	if dataElementsFile == "" {
		dataElementsFile = "data_elements.csv"
	}

	purposesFile := os.Getenv("PURPOSES_PATH")
	if purposesFile == "" {
		purposesFile = "purposes.csv"
	}

	if err := loadDataElements(dataElementsFile); err != nil {
		return fmt.Errorf("failed to load data elements: %w", err)
	}
	if err := loadPurposes(purposesFile); err != nil {
		return fmt.Errorf("failed to load purposes: %w", err)
	}
	return nil
}

// splitAndTrim is a helper function to handle comma-separated string fields.
func splitAndTrim(s string) []string {
	if s == "" {
		return nil
	}
	parts := strings.Split(s, ",")
	for i, p := range parts {
		parts[i] = strings.TrimSpace(p)
	}
	return parts
}

// loadDataElements reads data from the data_elements.csv file.
func loadDataElements(file string) error {
	f, err := os.Open(file)
	if err != nil {
		return fmt.Errorf("cannot open %s: %w", file, err)
	}
	defer f.Close()

	r := csv.NewReader(f)
	if _, err := r.Read(); err != nil && err != io.EOF {
		return fmt.Errorf("error reading header from %s: %w", file, err)
	}

	var loadedData []DataElement
	for {
		rec, err := r.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Printf("error reading record from %s: %v", file, err)
			continue
		}
		if len(rec) < 6 {
			log.Printf("skipping malformed row in %s: %v", file, rec)
			continue
		}

		var trans Translations
		if err := json.Unmarshal([]byte(rec[5]), &trans); err != nil {
			log.Printf("bad translations JSON in %s: %v", file, err)
			trans = Translations{}
		}
		trans.ENG = rec[1]

		de := DataElement{
			ID:           rec[0],
			Title:        rec[1],
			Description:  rec[2],
			Aliases:      splitAndTrim(rec[3]),
			Domain:       rec[4],
			Translations: trans,
		}
		loadedData = append(loadedData, de)
	}

	dataElements = loadedData
	log.Printf("loaded %d data elements from %s", len(dataElements), file)
	return nil
}

// loadPurposes reads data from the purposes.csv file.
func loadPurposes(filename string) error {
	file, err := os.Open(filename)
	if err != nil {
		return fmt.Errorf("error opening file %s: %w", filename, err)
	}
	defer file.Close()

	reader := csv.NewReader(file)

	headers, err := reader.Read()
	if err != nil && err != io.EOF {
		return fmt.Errorf("error reading header from %s: %w", filename, err)
	}
	headerMap := make(map[string]int)
	for i, h := range headers {
		headerMap[h] = i
	}

	requiredHeaders := []string{"purpose_id", "industry", "sub_category", "data_elements"}
	for _, rh := range requiredHeaders {
		if _, ok := headerMap[rh]; !ok {
			return fmt.Errorf("missing required header: %s", rh)
		}
	}

	var loadedPurposes []Purpose
	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Printf("error reading record from %s: %v", filename, err)
			continue
		}
		if len(record) < len(headers) {
			log.Printf("Skipping short record in %s: %+v", filename, record)
			continue
		}

		purpose := Purpose{
			ID:           record[headerMap["purpose_id"]],
			Industry:     record[headerMap["industry"]],
			SubCategory:  record[headerMap["sub_category"]],
			DataElements: splitAndTrim(record[headerMap["data_elements"]]),
			Translations: Translations{ // Now populating the nested struct
				ENG: record[headerMap["eng"]],
				ASM: record[headerMap["asm"]],
				BEN: record[headerMap["ben"]],
				BRX: record[headerMap["brx"]],
				DOI: record[headerMap["doi"]],
				GUJ: record[headerMap["guj"]],
				HIN: record[headerMap["hin"]],
				KAN: record[headerMap["kan"]],
				KAS: record[headerMap["kas"]],
				KOK: record[headerMap["kok"]],
				MAI: record[headerMap["mai"]],
				MAL: record[headerMap["mal"]],
				MNI: record[headerMap["mni"]],
				MAR: record[headerMap["mar"]],
				NEP: record[headerMap["nep"]],
				ORI: record[headerMap["ori"]],
				PAN: record[headerMap["pan"]],
				SAN: record[headerMap["san"]],
				TAM: record[headerMap["tam"]],
				TEL: record[headerMap["tel"]],
				SAT: record[headerMap["sat"]],
				SND: record[headerMap["snd"]],
				URD: record[headerMap["urd"]],
			},
		}
		loadedPurposes = append(loadedPurposes, purpose)
	}

	purposes = loadedPurposes
	log.Printf("loaded %d purposes from %s", len(purposes), filename)
	return nil
}

// parseUintParam safely parses a query parameter as an integer.
func parseUintParam(r *http.Request, key string, defaultVal int) int {
	val := r.URL.Query().Get(key)
	if val == "" {
		return defaultVal
	}
	parsed, err := strconv.Atoi(val)
	if err != nil || parsed < 0 {
		return defaultVal
	}
	return parsed
}

// writeJSONResponse is a new helper function to standardize JSON responses.
func writeJSONResponse(w http.ResponseWriter, data interface{}, statusCode int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	if err := json.NewEncoder(w).Encode(data); err != nil {
		log.Printf("encode error: %v", err)
		http.Error(w, "Failed to encode JSON", http.StatusInternalServerError)
	}
}

// getDataElementsHandler handles HTTP requests for data elements.
func getDataElementsHandler(w http.ResponseWriter, r *http.Request) {
	params := struct {
		Offset  int
		Limit   int
		Domain  string
		Title   string
		ID      string
		DeTitle string
	}{
		Offset:  parseUintParam(r, "offset", 0),
		Limit:   parseUintParam(r, "limit", 100),
		Domain:  strings.ToLower(r.URL.Query().Get("domain")),
		Title:   strings.ToLower(r.URL.Query().Get("title")),
		ID:      r.URL.Query().Get("id"),
		DeTitle: r.URL.Query().Get("de_title"),
	}

	if params.DeTitle != "" {
		for _, de := range dataElements {
			if de.Title == params.DeTitle {
				writeJSONResponse(w, de, http.StatusOK)
				return
			}
		}
		writeJSONResponse(w, map[string]string{"error": "Data element not found"}, http.StatusNotFound)
		return
	}

	var filtered []DataElement
	for _, de := range dataElements {
		if params.Domain != "" && !strings.Contains(strings.ToLower(de.Domain), params.Domain) {
			continue
		}
		if params.Title != "" && !strings.Contains(strings.ToLower(de.Title), params.Title) {
			continue
		}
		if params.ID != "" && de.ID != params.ID {
			continue
		}
		filtered = append(filtered, de)
	}

	total := len(filtered)
	start := params.Offset
	if start > total {
		start = total
	}
	end := start + params.Limit
	if end > total {
		end = total
	}

	page := filtered[start:end]

	resp := map[string]interface{}{
		"total":  total,
		"offset": start,
		"limit":  params.Limit,
		"data":   page,
	}

	writeJSONResponse(w, resp, http.StatusOK)
}

// getPurposesHandler handles HTTP requests for purposes.
func getPurposesHandler(w http.ResponseWriter, r *http.Request) {
	params := struct {
		Offset      int
		Limit       int
		ID          string
		Industry    string
		SubCategory string
		Title       string
	}{
		Offset:      parseUintParam(r, "offset", 0),
		Limit:       parseUintParam(r, "limit", 10),
		ID:          strings.TrimSpace(r.URL.Query().Get("id")),
		Industry:    strings.TrimSpace(r.URL.Query().Get("industry")),
		SubCategory: strings.TrimSpace(r.URL.Query().Get("sub_category")),
		Title:       strings.ToLower(strings.TrimSpace(r.URL.Query().Get("title"))),
	}
	if params.Limit > 100 {
		params.Limit = 100
	}

	var filtered []Purpose
	for _, p := range purposes {
		if params.ID != "" && p.ID != params.ID {
			continue
		}
		if params.Industry != "" && !strings.EqualFold(p.Industry, params.Industry) {
			continue
		}
		if params.SubCategory != "" && !strings.EqualFold(p.SubCategory, params.SubCategory) {
			continue
		}
		// The title filter now checks the nested translations.ENG field.
		if params.Title != "" && !strings.Contains(strings.ToLower(p.Translations.ENG), params.Title) {
			continue
		}
		filtered = append(filtered, p)
	}

	total := len(filtered)
	start := params.Offset
	if start > total {
		start = total
	}
	end := start + params.Limit
	if end > total {
		end = total
	}

	page := filtered[start:end]

	resp := map[string]interface{}{
		"total":  total,
		"offset": start,
		"limit":  params.Limit,
		"data":   page,
	}

	writeJSONResponse(w, resp, http.StatusOK)
}
