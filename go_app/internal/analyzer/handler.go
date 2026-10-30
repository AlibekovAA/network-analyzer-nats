package analyzer

import (
	"encoding/json"
	"time"

	"go_app/internal/domain"
)

func (s *Service) HandleStart(msg []byte) error {
	var start struct {
		AnalysisID  string `json:"analysis_id"`
		TotalChunks int    `json:"total_chunks"`
	}
	if err := json.Unmarshal(msg, &start); err != nil {
		return err
	}

	s.mu.Lock()
	s.data[start.AnalysisID] = &analysisState{updatedAt: time.Now()}
	s.mu.Unlock()
	s.log.Printf("Starting analysis ID: %s, expecting %d chunks", start.AnalysisID, start.TotalChunks)
	return nil
}

func (s *Service) HandleChunk(msg []byte) ([]byte, error) {
	var chunk domain.ChunkMessage
	if err := json.Unmarshal(msg, &chunk); err != nil {
		return nil, err
	}

	decodedData, err := s.decodeData(chunk.Data, chunk.Encoding)
	if err != nil {
		return nil, err
	}

	s.mu.Lock()
	state := s.data[chunk.AnalysisID]
	if state == nil {
		state = &analysisState{}
		s.data[chunk.AnalysisID] = state
	}
	if chunk.ChunkNumber == 0 {
		state.content = decodedData
	} else {
		state.content = append(state.content, decodedData...)
	}
	state.updatedAt = time.Now()
	s.mu.Unlock()

	s.log.Printf("Processed chunk %d/%d for analysis ID: %s",
		chunk.ChunkNumber+1, chunk.TotalChunks, chunk.AnalysisID)

	return []byte(`{"status":"ok"}`), nil
}

func (s *Service) HandleFinish(msg []byte) ([]byte, error) {
	var finish struct {
		AnalysisID string `json:"analysis_id"`
	}
	if err := json.Unmarshal(msg, &finish); err != nil {
		return nil, err
	}

	s.mu.Lock()
	state := s.data[finish.AnalysisID]
	var data []byte
	if state != nil {
		state.updatedAt = time.Now()
		data = state.content
	}
	s.mu.Unlock()
	result, err := s.analyzer.Analyze(data)
	if err != nil {
		return nil, err
	}

	s.mu.Lock()
	if s.data[finish.AnalysisID] == state {
		delete(s.data, finish.AnalysisID)
	}
	s.mu.Unlock()
	s.log.Printf("Analysis completed for ID: %s, processed %d packets",
		finish.AnalysisID, len(result.Packets))

	return json.Marshal(result)
}
