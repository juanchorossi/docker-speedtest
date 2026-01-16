-- Speedtest Results Table
CREATE TABLE speedtest_results (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  download_mbps DECIMAL(10,2),
  upload_mbps DECIMAL(10,2),
  ping_ms DECIMAL(10,2),
  isp TEXT,
  ip TEXT
);

-- Create index for faster time-based queries
CREATE INDEX idx_speedtest_created_at ON speedtest_results(created_at DESC);

-- Enable Row Level Security
ALTER TABLE speedtest_results ENABLE ROW LEVEL SECURITY;

-- Policy: Allow public read access (for dashboard)
CREATE POLICY "Allow public read access"
  ON speedtest_results
  FOR SELECT
  TO anon
  USING (true);

-- Policy: Allow authenticated insert (for the speedtest script using service role)
CREATE POLICY "Allow service role insert"
  ON speedtest_results
  FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Alternative: If using anon key for inserts (simpler setup)
CREATE POLICY "Allow anon insert"
  ON speedtest_results
  FOR INSERT
  TO anon
  WITH CHECK (true);
