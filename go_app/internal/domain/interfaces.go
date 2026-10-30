package domain

type PcapAnalyzer interface {
	Analyze(data []byte) (*AnalysisResult, error)
}
