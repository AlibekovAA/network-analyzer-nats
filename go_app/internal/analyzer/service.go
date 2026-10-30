package analyzer

import (
	"context"
	"encoding/base64"
	"encoding/hex"
	"sync"
	"time"

	"go_app/internal/domain"
	"go_app/internal/infrastructure/logger"
)

const analysisRetention = 15 * time.Minute

type analysisState struct {
	content   []byte
	updatedAt time.Time
}

type Service struct {
	log      *logger.Logger
	analyzer domain.PcapAnalyzer
	mu       sync.Mutex
	data     map[string]*analysisState
	cancel   context.CancelFunc
	done     chan struct{}
}

func NewService(log *logger.Logger, analyzer domain.PcapAnalyzer) *Service {
	ctx, cancel := context.WithCancel(context.Background())
	service := &Service{
		log:      log,
		analyzer: analyzer,
		data:     make(map[string]*analysisState),
		cancel:   cancel,
		done:     make(chan struct{}),
	}
	go service.cleanupExpired(ctx)
	return service
}

func (s *Service) Close() {
	s.cancel()
	<-s.done
}

func (s *Service) cleanupExpired(ctx context.Context) {
	defer close(s.done)
	ticker := time.NewTicker(time.Minute)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			s.mu.Lock()
			for analysisID, state := range s.data {
				if time.Since(state.updatedAt) >= analysisRetention {
					delete(s.data, analysisID)
				}
			}
			s.mu.Unlock()
		}
	}
}

func (s *Service) decodeData(data, encoding string) ([]byte, error) {
	switch encoding {
	case "hex":
		return hex.DecodeString(data)
	case "base64":
		return base64.StdEncoding.DecodeString(data)
	default:
		return nil, domain.ErrUnsupportedEncoding
	}
}
